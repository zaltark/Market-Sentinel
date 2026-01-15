import os
import json
import time
import requests
import logging
import safe_zone
from api_library import CoinGeckoEndpoints

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REGISTRY_FILE = safe_zone.REGISTRY_FILE
LIST_API_URL = CoinGeckoEndpoints.build_url(CoinGeckoEndpoints.COINS_LIST)
MARKETS_API_URL = CoinGeckoEndpoints.build_url(CoinGeckoEndpoints.COINS_MARKETS)

class CoinRegistry:
    def __init__(self):
        self.registry = self._load_registry()

    def _load_registry(self):
        """
        Loads the registry from disk if it exists and is recent (< 24h).
        Otherwise, fetches a fresh registry.
        """
        if os.path.exists(REGISTRY_FILE):
            file_age = time.time() - os.path.getmtime(REGISTRY_FILE)
            if file_age < 86400: # 24 hours
                try:
                    with open(REGISTRY_FILE, 'r') as f:
                        data = json.load(f)
                        if data:
                            logger.info(f"Loaded cached registry from {REGISTRY_FILE} ({int(file_age/3600)}h old).")
                            return data
                except Exception as e:
                    logger.warning(f"Failed to read registry cache: {e}")

        logger.info("Registry cache missing or expired. Syncing with CoinGecko...")
        return self._fetch_and_save_registry()

    def _fetch_and_save_registry(self):
        """
        Builds a 'Smart Registry'.
        1. Fetches Top 250 coins by Market Cap (The 'Canonical' versions).
        2. Fetches the complete list (The 'Long Tail').
        3. Merges them, placing Top 250 first to resolve ticker collisions.
        4. Preserves 'status' and 'failure_count' from the old registry.
        """
        logger.info("Building fresh coin registry...")
        
        # Load old registry to preserve state (failures/status)
        old_registry_map = {}
        if os.path.exists(REGISTRY_FILE):
            try:
                with open(REGISTRY_FILE, 'r') as f:
                    old_data = json.load(f)
                    # Map ID -> {status, failure_count}
                    for coin in old_data:
                        old_registry_map[coin['id']] = {
                            'status': coin.get('status', 'active'),
                            'failure_count': coin.get('failure_count', 0)
                        }
            except:
                pass # Corrupt file or first run

        # 1. Fetch High Priority (Top 250)
        priority_coins = []
        try:
            logger.info("Fetching Top 250 coins by Market Cap...")
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': safe_zone.CG_MAX_PER_PAGE,
                'page': '1'
            }
            response = requests.get(MARKETS_API_URL, params=params, timeout=10)
            response.raise_for_status()
            priority_coins = response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch Top 250: {e}. Relying on full list only.")

        # 2. Fetch Full List
        full_list = []
        try:
            logger.info("Fetching complete coin list...")
            response = requests.get(LIST_API_URL, timeout=10)
            response.raise_for_status()
            full_list = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch full list: {e}")
            if not priority_coins:
                return []

        # 3. Merge & Sort & Restore State
        combined_registry = []
        seen_ids = set()

        def process_coin(coin_data):
            if coin_data['id'] in seen_ids:
                return
            
            # Restore state or default
            prev_state = old_registry_map.get(coin_data['id'], {'status': 'active', 'failure_count': 0})
            
            clean_entry = {
                'id': coin_data['id'],
                'symbol': coin_data['symbol'],
                'name': coin_data['name'],
                'status': prev_state['status'],
                'failure_count': prev_state['failure_count']
            }
            combined_registry.append(clean_entry)
            seen_ids.add(coin_data['id'])

        # Add Priority Coins first
        for coin in priority_coins:
            process_coin(coin)

        # Add remaining from full list
        for coin in full_list:
            process_coin(coin)

        # Save to file
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(combined_registry, f)
        
        logger.info(f"Smart Registry saved. {len(combined_registry)} coins indexed (Top 250 prioritized).")
        return combined_registry

    def mark_coin_failure(self, coin_id):
        """Increments failure count. If >= 3, marks inactive."""
        # Reload to ensure we are editing current state
        # (Optimization: In a real app, we'd keep this in memory, but for CLI we read/write)
        with open(REGISTRY_FILE, 'r+') as f:
            data = json.load(f)
            found = False
            for coin in data:
                if coin['id'] == coin_id:
                    coin['failure_count'] = coin.get('failure_count', 0) + 1
                    if coin['failure_count'] >= 3:
                        coin['status'] = 'inactive'
                        logger.warning(f"Coin '{coin_id}' flagged INACTIVE (3 consecutive failures).")
                    found = True
                    break
            
            if found:
                f.seek(0)
                json.dump(data, f)
                f.truncate()

    def reset_coin_status(self, coin_id):
        """Resets failure count to 0 on successful fetch."""
        with open(REGISTRY_FILE, 'r+') as f:
            data = json.load(f)
            found = False
            for coin in data:
                if coin['id'] == coin_id and coin.get('failure_count', 0) > 0:
                    coin['failure_count'] = 0
                    coin['status'] = 'active'
                    found = True
                    break
            
            if found:
                f.seek(0)
                json.dump(data, f)
                f.truncate()
    
    def filter_active_assets(self, asset_ids):
        """Returns only assets that are NOT inactive."""
        active_ids = []
        inactive_count = 0
        
        # Build lookup for speed
        registry_map = {c['id']: c.get('status', 'active') for c in self.registry}
        
        for aid in asset_ids:
            if registry_map.get(aid) == 'inactive':
                inactive_count += 1
            else:
                active_ids.append(aid)
        
        if inactive_count > 0:
            logger.info(f"Filtered out {inactive_count} inactive assets.")
            
        return active_ids

    def get_coin_id(self, symbol_or_name):
        """
        Searches for a coin by symbol (e.g., 'btc') or name (e.g., 'Bitcoin').
        Returns the API 'id' (e.g., 'bitcoin').
        Prioritizes exact symbol matches.
        """
        search_term = symbol_or_name.lower()
        
        # 1. Exact Symbol Match (Will hit Top 250 first due to list order)
        for coin in self.registry:
            if coin['symbol'].lower() == search_term:
                return coin['id']
        
        # 2. Exact Name Match
        for coin in self.registry:
            if coin['name'].lower() == search_term:
                return coin['id']
        
        return None

    def validate_asset_list(self, user_inputs):
        """
        Takes a list of symbols/names (e.g., ['BTC', 'Ripple', 'Doge'])
        Returns a list of valid API IDs (e.g., ['bitcoin', 'ripple', 'dogecoin'])
        """
        valid_ids = []
        for term in user_inputs:
            coin_id = self.get_coin_id(term)
            if coin_id:
                valid_ids.append(coin_id)
            else:
                logger.warning(f"Could not find API ID for: {term}")
        return valid_ids

if __name__ == "__main__":
    # Test the registry
    registry = CoinRegistry()
    test_coins = ['BTC', 'ETH', 'BNB', 'USDC', 'XRP', 'Doge', 'MadeUpCoin']
    print(f"\nResolving IDs for: {test_coins}")
    resolved = registry.validate_asset_list(test_coins)
    print(f"Resolved IDs: {resolved}")
