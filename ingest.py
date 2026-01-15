import os
import json
import time
import requests
import logging
import argparse
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
from coin_registry import CoinRegistry
import safe_zone
from api_library import CoinGeckoEndpoints
from transform import transform_and_validate
import database
import budget_monitor

# Setup clean logging (just the message for CLI visual appeal)
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION (Use Environment Variables for Production) ---
API_URL = CoinGeckoEndpoints.build_url(CoinGeckoEndpoints.SIMPLE_PRICE)

def print_separator(char='-', length=70):
    print(char * length)

def print_header(title):
    print_separator('=')
    print(f"  {title.upper()}")
    print_separator('=')

class MarketSentinel:
    def __init__(self):
        pass

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=16),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def fetch_bulk_data(self, asset_ids):
        """
        Fetches data with Exponential Backoff.
        Trips Circuit Breaker (raises exception) after 5 failed attempts.
        """
        if not asset_ids:
            logger.warning("No valid assets provided to fetch.")
            return None

        # UPDATED: Requesting Market Cap and Volume
        params = {
            'ids': ','.join(asset_ids),
            'vs_currencies': 'usd',
            'include_last_updated_at': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        try:
            response = requests.get(API_URL, params=params, timeout=10)
            
            # Monitoring "Credit Burn"
            remaining = response.headers.get('x-ratelimit-remaining')
            limit = response.headers.get('x-ratelimit-limit')
            if remaining:
                logger.info(f"      [i] Credits: {remaining}/{limit} remaining.")

            # 304 Not Modified: Data is still fresh in cache
            if response.status_code == 304:
                logger.info("  [!] 304 Not Modified (Cache Hit). Skipping chunk.")
                return None

            # Check for CoinGecko specific error codes/headers before raising
            if response.status_code >= 400:
                self._log_api_error_details(response)
            
            # Raise HTTPError for bad responses (4xx, 5xx) so retry triggers
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            # Re-raise so tenacity can handle the retry logic
            raise e

    def _log_api_error_details(self, response):
        """Helper to log descriptive errors based on CoinGecko status codes."""
        code = response.status_code
        try:
            error_body = response.json()
            internal_code = error_body.get('error_code')
            message = error_body.get('error', 'No message')
        except:
            internal_code = None
            message = response.text

        logger.error(f"  [x] API Error {code}: {message}")

        if code == 400:
            logger.error("      Solution: Check parameters or syntax.")
        elif code == 401:
            logger.error("      Solution: Invalid or missing API key (Error 10002).")
        elif code == 403:
            logger.error("      Solution: Disable this feature in code (Pro feature accessed).")
        elif code == 414:
            logger.error("      Solution: Keep ID strings under 2,000 characters (Reduce batch size).")
        elif code == 429:
            retry_after = response.headers.get('Retry-After', 'Unknown')
            logger.warning(f"      Solution: Rate Limit Hit. Retry-After: {retry_after}s (Handling via Backoff).")
        elif code in [500, 503]:
            logger.error("      Solution: Server Error. Retrying...")

def main():
    # Load defaults from config file
    config_defaults = {
        "mode": "ingest",
        "limit": 500,
        "targets": None
    }
    
    try:
        if os.path.exists("ingest_config.json"):
            with open("ingest_config.json", "r") as f:
                file_config = json.load(f)
                config_defaults.update(file_config)
    except Exception as e:
        logger.warning(f"Could not load ingest_config.json: {e}")

    parser = argparse.ArgumentParser(description="Market Sentinel Ingestion Tool")
    parser.add_argument('--mode', choices=['ingest', 'dry-run'], default=config_defaults['mode'], help=f"Execution mode (Default: {config_defaults['mode']})")
    parser.add_argument('--limit', type=int, default=config_defaults['limit'], help=f"Number of assets to process (Default: {config_defaults['limit']})")
    parser.add_argument('--targets', type=str, default=config_defaults['targets'], help="Comma-separated list of symbols (e.g. BTC,ETH)")
    
    args = parser.parse_args()
    
    print_header("Market Sentinel: Crypto ETL Pipeline")
    print(f"  Mode:       {args.mode.upper()}")
    print(f"  Start Time: {datetime.now().strftime('%H:%M:%S')}")
    print_separator()
    
    # 1. Initialize Database Schema (if in ingest mode)
    if args.mode == 'ingest':
        print("  [*] Initializing Database...")
        database.init_db()

    total_start = time.perf_counter()
    
    # 2. Initialize Registry (Forces Fresh Sync)
    print("  [*] Syncing Coin Registry...")
    reg_start = time.perf_counter()
    registry = CoinRegistry()
    print(f"  [+] Registry Synced in {time.perf_counter() - reg_start:.2f}s")
    
    # 3. Determine Assets
    assets = []
    if args.targets:
        target_list = [t.strip() for t in args.targets.split(',')]
        assets = registry.validate_asset_list(target_list)
        print(f"  [+] Targeting {len(assets)} specific assets: {args.targets}")
    else:
        # Default strategy: Top N assets from the smart registry
        limit = args.limit
        all_entries = registry.registry
        assets = [coin['id'] for coin in all_entries[:limit]]
        print(f"  [+] Targeting Top {len(assets)} assets by Market Cap.")

    # Filter Inactive "Ghost" Coins
    original_count = len(assets)
    assets = registry.filter_active_assets(assets)
    if len(assets) < original_count:
        print(f"  [-] Filtered {original_count - len(assets)} inactive 'Ghost' coins.")

    # 4. Initialize Sentinel
    sentinel = MarketSentinel()
    
    # 5. Chunking & Execution
    chunk_size = safe_zone.CG_CHUNKS_SIMPLE
    chunks = [assets[i:i + chunk_size] for i in range(0, len(assets), chunk_size)]
    
    print(f"  [+] Processing Plan: {len(chunks)} chunks (Max {chunk_size} items each).")
    print_separator()
    
    total_upserted = 0

    for i, chunk in enumerate(chunks):
        chunk_start = time.perf_counter()
        try:
            print(f"  [>] Processing Chunk {i+1}/{len(chunks)}...", end='\r')
            
            raw = sentinel.fetch_bulk_data(chunk)
            
            if raw:
                # Pass chunk (requested_ids) and registry for Ghost Coin logic
                # Now returns: (coin_id, symbol, price, market_cap, volume, timestamp)
                cleaned = transform_and_validate(raw, chunk, registry)
                
                if args.mode == 'ingest':
                    # Database Load
                    database.load_batch(cleaned)
                    total_upserted += len(cleaned)
                    print(f"  [OK] Chunk {i+1} Processed | Upserted {len(cleaned)} records", end='')
                else:
                    # Dry Run / Simulation
                    if cleaned:
                        sample = cleaned[0] 
                        # Sample tuple: (id, symbol, price, mcap, vol, time)
                        # Format: Asset: BTC | Price: $95,000.00
                        print(f"  [OK] Chunk {i+1}: {len(cleaned)} records ready.   ", end='')
                        print(f"\n      Sample: {sample[1].upper():<6} | ${sample[2]:,.2f} | Cap: ${sample[3]/1e9:,.1f}B | {sample[5].strftime('%H:%M:%S')}", end='')
            
            chunk_time = time.perf_counter() - chunk_start
            print(f" ({chunk_time:.2f}s)")
            
            # Polite pause between chunks
            if i < len(chunks) - 1:
                time.sleep(2)
                
        except Exception as e:
            print(f"\n  [x] CRITICAL: Circuit Breaker Tripped on Chunk {i+1}.")
            print(f"      Reason: {e}")
            logger.critical(str(e))
            # Continue to next chunk or exit? Original logic was exit(1) for critical errors
            exit(1)
            
    # 6. Cleanup & Retention
    if args.mode == 'ingest':
        print_separator()
        database.enforce_retention_policy()

    print_separator('=')
    print(f"  DONE. Total Cycle Time: {time.perf_counter() - total_start:.2f}s")
    if args.mode == 'ingest':
        print(f"  Total Records Upserted: {total_upserted}")
    print_separator('=')
    
    return args

if __name__ == "__main__":
    # Budget Guard Integration
    start_time = datetime.now()
    
    try:
        args = main()
        
        # Only log to budget if we actually interacted with Neon
        if args and args.mode == 'ingest':
            end_time = datetime.now()
            budget_monitor.save_run(start_time, end_time)
            budget_monitor.check_budget_status()
            
    except Exception as e:
        logger.error(f"Execution Failed: {e}")