from coin_registry import CoinRegistry
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_registry_resolution():
    print("--- Testing Coin Registry Resolution ---")
    
    registry = CoinRegistry()
    
    # Mix of symbols to test
    # Common, Stablecoins, Top/Bottom of lists (conceptually), and randoms
    test_symbols = [
        'BTC',          # The King
        'ETH',          # The Queen
        'BNB',          # Previously failed
        'USDC',         # Previously failed
        'XRP',          # Previously failed
        'DOGE',         # Meme
        'PEPE',         # Modern Meme
        'SOL',          # High volume
        'USDT',         # Tether
        'LINK',         # Oracle
        'AAVE',         # DeFi
        'NONEXISTENTCOIN123' # Should fail
    ]
    
    print(f"\nResolving IDs for: {test_symbols}")
    resolved_ids = registry.validate_asset_list(test_symbols)
    
    print(f"\n[RESULTS] Resolved {len(resolved_ids)} out of {len(test_symbols)} symbols.")
    print("-" * 50)
    
    # Manually check and print mappings to verify correctness
    for symbol in test_symbols:
        coin_id = registry.get_coin_id(symbol)
        status = f"✅ {coin_id}" if coin_id else "❌ Not Found"
        print(f"{symbol:<10} -> {status}")
        
    print("-" * 50)

if __name__ == "__main__":
    test_registry_resolution()
