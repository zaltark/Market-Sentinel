from datetime import datetime

def transform_and_validate(raw_data, requested_ids, registry):
    """
    The 'Schema Shield' & 'Ghost Coin Guard'.
    Ensures data is clean, handles inactive coins, and prepares data for DB.
    
    Args:
        raw_data (dict): Dictionary returned from the API.
        requested_ids (list): List of IDs that were requested.
        registry (CoinRegistry): Instance of the registry to update status/lookup symbols.
        
    Returns:
        list: A list of tuples (coin_id, symbol, price, market_cap, volume, timestamp).
    """
    cleaned_batch = []
    returned_ids = set(raw_data.keys())
    
    # Build quick lookup for symbols
    # (Optimization: In a long running process, this map should be built once in the registry class)
    id_to_symbol = {c['id']: c['symbol'] for c in registry.registry}

    # 1. Handle Missing Coins (Requested but not returned)
    missing_ids = set(requested_ids) - returned_ids
    for mid in missing_ids:
        registry.mark_coin_failure(mid)

    # 2. Process Returned Data
    for asset, data in raw_data.items():
        try:
            # Extract Data
            price = data.get('usd')
            market_cap = data.get('usd_market_cap')
            volume = data.get('usd_24h_vol')
            timestamp_raw = data.get('last_updated_at')
            symbol = id_to_symbol.get(asset, "UNK") # Default to UNK if not found

            # Validation
            if price is not None and timestamp_raw is not None:
                price = float(price)
                
                # Handle optional fields (defaults to 0.0 or None based on preference)
                market_cap = float(market_cap) if market_cap is not None else 0.0
                volume = float(volume) if volume is not None else 0.0
                
                timestamp = datetime.fromtimestamp(timestamp_raw)
                
                if price >= 0:
                    # Append Tuple matching database.load_batch signature
                    # (coin_id, symbol, price_usd, market_cap, volume_24h, timestamp)
                    cleaned_batch.append((asset, symbol, price, market_cap, volume, timestamp))
                    
                    # Success! Reset status
                    registry.reset_coin_status(asset)
                else:
                    raise ValueError("Negative Price")
            else:
                raise ValueError("Null Price or Timestamp")
                
        except (TypeError, ValueError) as e:
            # Corrupt data -> Mark failure
            print(f"  [!] Bad Data for {asset}: {e}")
            registry.mark_coin_failure(asset)
            
    return cleaned_batch