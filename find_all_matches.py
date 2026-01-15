import json

def find_all_matches(symbol_to_find):
    symbol_to_find = symbol_to_find.lower()
    with open("coin_registry.json", "r") as f:
        registry = json.load(f)
    
    matches = [coin for coin in registry if coin['symbol'].lower() == symbol_to_find]
    
    print(f"--- All matches for symbol: '{symbol_to_find.upper()}' ---")
    if not matches:
        print("No matches found.")
    else:
        print(f"Found {len(matches)} matches:")
        for coin in matches:
            print(f"ID: {coin['id']:<30} | Name: {coin['name']}")
    print("-" * 50)

if __name__ == "__main__":
    find_all_matches("BTC")
    find_all_matches("BTX")
