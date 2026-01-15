"""
Centralized library of CoinGecko API endpoints.
Reference: https://docs.coingecko.com/v3.0.1/reference/

Usage Tip: Endpoints with '{id}' or other placeholders are format strings.
Example: CoinGeckoEndpoints.COINS_ID.format(id='bitcoin')

PRO vs FREE:
- Free (Demo) API Root: https://api.coingecko.com/api/v3 (Rate Limit: ~30 calls/min)
- Pro (Paid) API Root:  https://pro-api.coingecko.com/api/v3 (Rate Limit: 500+ calls/min)
- Headers:
    - Free: x-cg-demo-api-key
    - Pro:  x-cg-pro-api-key
"""

class CoinGeckoEndpoints:
    # --- CONFIGURATION ---
    BASE_URL_DEMO = "https://api.coingecko.com/api/v3"
    BASE_URL_PRO = "https://pro-api.coingecko.com/api/v3"
    
    # Default to Demo (Free)
    BASE_URL = BASE_URL_DEMO
    
    # --- GENERAL (Public) ---
    PING = "/ping"
    
    # --- SIMPLE (Public) ---
    SIMPLE_PRICE = "/simple/price"
    SIMPLE_TOKEN_PRICE = "/simple/token_price/{id}"
    SIMPLE_SUPPORTED_VS_CURRENCIES = "/simple/supported_vs_currencies"
    
    # --- COINS (Public) ---
    COINS_LIST = "/coins/list"
    COINS_MARKETS = "/coins/markets"
    COINS_ID = "/coins/{id}"
    COINS_TICKERS = "/coins/{id}/tickers"
    COINS_HISTORY = "/coins/{id}/history"
    COINS_MARKET_CHART = "/coins/{id}/market_chart"
    COINS_MARKET_CHART_RANGE = "/coins/{id}/market_chart/range"
    COINS_OHLC = "/coins/{id}/ohlc"
    
    # --- CONTRACT (Public) ---
    # COINS_CONTRACT = "/coins/{id}/contract/{contract_address}"
    # COINS_CONTRACT_MARKET_CHART = "/coins/{id}/contract/{contract_address}/market_chart"
    # COINS_CONTRACT_MARKET_CHART_RANGE = "/coins/{id}/contract/{contract_address}/market_chart/range"
    
    # --- CATEGORIES (Public) ---
    COINS_CATEGORIES_LIST = "/coins/categories/list"
    COINS_CATEGORIES = "/coins/categories"
    
    # --- ASSET PLATFORMS (Public) ---
    ASSET_PLATFORMS = "/asset_platforms"
    
    # --- EXCHANGES (Public) ---
    EXCHANGES = "/exchanges"
    EXCHANGES_LIST = "/exchanges/list"
    EXCHANGES_ID = "/exchanges/{id}"
    EXCHANGES_TICKERS = "/exchanges/{id}/tickers"
    EXCHANGES_VOLUME_CHART = "/exchanges/{id}/volume_chart"
    
    # --- DERIVATIVES (Public) ---
    # DERIVATIVES = "/derivatives"
    # DERIVATIVES_EXCHANGES = "/derivatives/exchanges"
    # DERIVATIVES_EXCHANGES_ID = "/derivatives/exchanges/{id}"
    # DERIVATIVES_EXCHANGES_LIST = "/derivatives/exchanges/list"
    
    # --- NFTS (Public) ---
    # NFTS_LIST = "/nfts/list"
    # NFTS_ID = "/nfts/{id}"
    # NFTS_CONTRACT = "/nfts/{asset_platform_id}/contract/{contract_address}"
    
    # --- PUBLIC TREASURY (Public) ---
    # ENTITIES_LIST = "/entities/list"
    # PUBLIC_TREASURY_COIN = "/companies/public_treasury/{coin_id}"
    # PUBLIC_TREASURY_ENTITY = "/public_treasury/{entity_id}"
    
    # --- GLOBAL (Public) ---
    GLOBAL = "/global"
    GLOBAL_DEFI = "/global/decentralized_finance_defi"
    EXCHANGE_RATES = "/exchange_rates"
    SEARCH = "/search"
    SEARCH_TRENDING = "/search/trending"
    
    # --- ONCHAIN / GECKOTERMINAL (Public) ---
    # ONCHAIN_NETWORKS = "/onchain/networks"
    # ONCHAIN_DEXES = "/onchain/networks/{network}/dexes"
    # ONCHAIN_POOLS = "/onchain/networks/{network}/pools"
    # ONCHAIN_POOLS_ADDRESS = "/onchain/networks/{network}/pools/{address}"
    # ONCHAIN_TOKENS_ADDRESS = "/onchain/networks/{network}/tokens/{address}"

    # --- IMPORTED FROM JSON (Specialized / DEX Layer - Commented out for now) ---
    # TOKEN_LISTS_BY_ASSET_PLATFORM_ID = "/token_lists/ethereum/all.json"
    # CRYPTO_TREASURY_HOLDINGS_BY_COIN_ID = "/{entity}/public_treasury/bitcoin"
    # CRYPTO_TREASURY_HOLDINGS_HISTORICAL_CHART_DATA_BY_ID = "/public_treasury/strategy/bitcoin/holding_chart"
    # CRYPTO_TREASURY_TRANSACTION_HISTORY_BY_ENTITY_ID = "/public_treasury/strategy/transaction_history"
    # TOKEN_PRICE_BY_TOKEN_ADDRESSES = "/onchain/simple/networks/eth/token_price/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    # MULTIPLE_POOLS_DATA_BY_POOL_ADDRESSES = "/onchain/networks/eth/pools/multi/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
    # TRENDING_POOLS_LIST = "/onchain/networks/trending_pools"
    # TRENDING_POOLS_BY_NETWORK = "/onchain/networks/eth/trending_pools"
    # TOP_POOLS_BY_DEX = "/onchain/networks/eth/dexes/sushiswap/pools"
    # NEW_POOLS_LIST = "/onchain/networks/new_pools"
    # NEW_POOLS_BY_NETWORK = "/onchain/networks/eth/new_pools"
    # SEARCH_POOLS = "/onchain/search/pools"
    # TOP_POOLS_BY_TOKEN_ADDRESS = "/onchain/networks/eth/tokens/0xdac17f958d2ee523a2206206994597c13d831ec7/pools"
    # TOKENS_DATA_BY_TOKEN_ADDRESSES = "/onchain/networks/solana/tokens/multi/6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN%2C2g4LS3y2myPe6vj9wTvoBE1wKqxvhnZPoZA9QU9upump"
    # TOKEN_INFO_BY_TOKEN_ADDRESS = "/onchain/networks/eth/tokens/0xdac17f958d2ee523a2206206994597c13d831ec7/info"
    # POOL_TOKENS_INFO_BY_POOL_ADDRESS = "/onchain/networks/eth/pools/0x06da0fd433c1a5d7a4faa01111c044910a184553/info"
    # MOST_RECENTLY_UPDATED_TOKENS_LIST = "/onchain/tokens/info_recently_updated"
    # POOL_OHLCV_CHART_BY_POOL_ADDRESS = "/onchain/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}"
    # PAST_24_HOUR_TRADES_BY_POOL_ADDRESS = "/onchain/networks/eth/pools/0x06da0fd433c1a5d7a4faa01111c044910a184553/trades"
    
    # --- PRO ONLY (Examples - Not exhaustive) ---
    # These endpoints typically require a Paid Plan
    PRO_COINS_LIST_NEW = "/coins/list/new"
    PRO_TOP_GAINERS_LOSERS = "/coins/top_gainers_losers"
    PRO_GLOBAL_MARKET_CAP_CHART = "/global/market_cap_chart"
    
    @classmethod
    def get_auth_config(cls):
        """
        Retrieves API Key and determine the correct header from Environment.
        Returns: (header_name, api_key) or (None, None)
        """
        api_key = os.getenv("COINGECKO_API_KEY")
        is_pro = os.getenv("COINGECKO_IS_PRO", "false").lower() == "true"
        
        if not api_key:
            return None, None
            
        header = "x-cg-pro-api-key" if is_pro else "x-cg-demo-api-key"
        return header, api_key

    @classmethod
    def build_url(cls, endpoint, is_pro=False):
        """
        Constructs the full API URL.
        
        Args:
            endpoint (str): The endpoint path (e.g., CoinGeckoEndpoints.SIMPLE_PRICE)
            is_pro (bool): If True, uses the Pro Base URL. Defaults to False.
        """
        base = cls.BASE_URL_PRO if is_pro else cls.BASE_URL_DEMO
        return f"{base}{endpoint}"
