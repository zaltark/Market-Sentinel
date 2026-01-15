import os
import requests
import logging
from ingest import MarketSentinel

# Configure logging to see the output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_restricted_endpoint():
    print("--- Testing Restricted Endpoint Error Handling ---")
    
    # We will temporarily point a Sentinel instance to the restricted endpoint
    restricted_url = "https://api.coingecko.com/api/v3/coins/top_gainers_losers"
    
    # Initialize Sentinel
    sentinel = MarketSentinel()
    
    # We simulate hitting the restricted endpoint by manually calling the logic 
    # but using the restricted URL
    params = {
        'vs_currency': 'usd'
    }
    
    print(f"Attempting to hit restricted endpoint: {restricted_url}")
    
    try:
        # Note: We are using a fake API key header if available, or none
        headers = {}
        api_key = os.getenv("CG_API_KEY")
        if api_key:
            headers["x-cg-demo-api-key"] = api_key
            
        response = requests.get(restricted_url, params=params, headers=headers, timeout=10)
        
        # This should trigger our detailed logging
        if response.status_code >= 400:
            print(f"\n[INTERCEPTED] API returned status {response.status_code}")
            sentinel._log_api_error_details(response)
            
            # Verify if it raises (it should)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                print("\n[SUCCESS] HTTPError raised as expected after logging details.")
        else:
            print(f"\n[UNEXPECTED] Request succeeded with status {response.status_code}. Maybe your API key has access?")
            print(response.json())

    except Exception as e:
        print(f"\n[ERROR in test] {e}")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_restricted_endpoint()
