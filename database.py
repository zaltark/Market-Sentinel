import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import safe_zone

# Load environment variables
load_dotenv()

def get_db_connection():
    """Establishes a connection to the Neon server."""
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        print(f"❌ Database Connection Failed: {e}")
        raise e

def init_db():
    """
    Idempotent function to create the table if it doesn't exist.
    Run this at the start of every ingestion cycle.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS market_data (
        id SERIAL PRIMARY KEY,
        coin_id VARCHAR(255) NOT NULL,
        symbol VARCHAR(50) NOT NULL,
        price NUMERIC,
        market_cap NUMERIC,
        volume_24h NUMERIC,
        timestamp TIMESTAMPTZ NOT NULL,
        UNIQUE(coin_id, timestamp) -- Critical for preventing duplicates
    );
    
    -- Index for faster time-series queries (for your future dashboard)
    CREATE INDEX IF NOT EXISTS idx_timestamp ON market_data(timestamp);
    """
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(create_table_query)
        conn.commit()
        print("✅ Database Schema Validated")
    except Exception as e:
        print(f"❌ Schema Validation Failed: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def load_batch(records):
    """
    Upserts a batch of records efficiently.
    Expects a list of tuples: (coin_id, symbol, price, cap, volume, timestamp)
    """
    if not records:
        return

    # The "UPSERT" Logic:
    # 1. Try to Insert.
    # 2. If (coin_id + timestamp) conflict, Update the values instead.
    upsert_query = """
    INSERT INTO market_data (coin_id, symbol, price, market_cap, volume_24h, timestamp)
    VALUES %s
    ON CONFLICT (coin_id, timestamp) 
    DO UPDATE SET
        price = EXCLUDED.price,
        market_cap = EXCLUDED.market_cap,
        volume_24h = EXCLUDED.volume_24h;
    """

    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # execute_values is faster than looping through inserts manually
        execute_values(cur, upsert_query, records)
        conn.commit()
        print(f"📦 Batch Loaded: {len(records)} records upserted.")
    except Exception as e:
        print(f"❌ Failed to load batch: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def enforce_retention_policy():
    """
    Deletes data older than configured retention period (default 60 days).
    """
    retention_query = f"DELETE FROM market_data WHERE timestamp < NOW() - INTERVAL '{safe_zone.RETENTION_DAYS} days';"
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(retention_query)
        deleted_count = cur.rowcount
        conn.commit()
        if deleted_count > 0:
            print(f"🧹 Retention Policy: Purged {deleted_count} old records (>{safe_zone.RETENTION_DAYS} days).")
    except Exception as e:
        print(f"❌ Retention Policy Failed: {e}")
    finally:
        cur.close()
        conn.close()