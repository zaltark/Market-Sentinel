# --- API LIMITS & SAFETY ---
CG_MAX_PER_PAGE = 250         # CoinGecko API limit per page
CG_CHUNKS_SIMPLE = 500        # Chunk size for simple price endpoint (Max 500)
RETRY_ATTEMPTS = 5            # Max retries for API calls
BACKOFF_FACTOR = 1            # Initial backoff in seconds

# --- DATA TRANSFORMATION ---
MAX_PRICE = 1_000_000_000     # Sanity check: Price > $1B is suspicious
MIN_PRICE = 0                 # Sanity check: Price cannot be negative

# --- STORAGE & RETENTION ---
RETENTION_DAYS = 60           # Data older than this is purged
DB_BATCH_SIZE = 1000          # Upsert batch size

# --- BUDGET MONITORING (Neon Free Tier) ---
MONTHLY_QUOTA_CU_HOURS = 100  # Free tier limit
MIN_COMPUTE_CU = 0.25         # Minimum Compute Unit usage
AUTOSUSPEND_MINUTES = 5       # Time endpoint stays active after query
USAGE_LOG_FILE = "usage_log.json"

# --- FILES ---
REGISTRY_FILE = "coin_registry.json"
INGEST_CONFIG_FILE = "ingest_config.json"