# --- CONFIGURATION LIMITS ---
# Hard Bulk Limits ("Vertical" Limit)
CG_MAX_PER_PAGE = 250        # Official markets limit (for /coins/markets)
CG_CHUNKS_SIMPLE = 150       # Safety limit for URL length (for /simple/price)
CG_TICKERS_PER_PAGE = 100    # Official limit for /coins/{id}/tickers

# Rate Limits ("Horizontal" Limit)
CG_RATE_LIMIT_MIN = 30       # Official demo rate limit (calls per minute)
CG_MONTHLY_QUOTA = 10000     # Monthly call quota for Demo plan

# --- CACHE AWARENESS ---
# CoinGecko Demo Plan cache updates every 60 seconds.
# Polling more frequently will likely result in a 304 Not Modified status.


# --- CALCULATED LOGIC ---
# For ~19,000 coins:
# Total Pages = 19,000 / 250 = 76 requests
# Time to complete = 76 / 30 = ~2.5 minutes

# If syncing 4 times a day:
# 76 * 4 = 304 calls/day
# 304 * 30 = 9,120 calls/month (Safe within 10k quota)
