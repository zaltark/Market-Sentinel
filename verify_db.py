import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_db_state():
    print("🔍 DIAGNOSTIC: Database State Verification")
    print("-" * 40)
    
    try:
        # Connect to Neon
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        
        # 1. Check Total Count
        cur.execute("SELECT COUNT(*) FROM market_data;")
        count = cur.fetchone()[0]
        print(f"📊 Total Records:   {count}")

        if count > 0:
            # 2. Check Data Freshness
            cur.execute("SELECT MAX(timestamp) FROM market_data;")
            latest_time = cur.fetchone()[0]
            print(f"🕒 Latest Update:   {latest_time} (UTC)")
            
            # 3. Inspect Top Assets
            print("-" * 40)
            print("🏆 Top 5 Assets by Market Cap:")
            query = """
            SELECT symbol, price_usd, market_cap, volume_24h, timestamp 
            FROM market_data 
            ORDER BY market_cap DESC 
            LIMIT 5;
            """
            # Using pandas for pretty printing
            df = pd.read_sql(query, conn)
            # Format columns for readability
            pd.options.display.float_format = '{:,.2f}'.format
            print(df.to_string(index=False))
        else:
            print("⚠️  Database is empty.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Verification Failed: {e}")
    print("-" * 40)

if __name__ == "__main__":
    verify_db_state()
