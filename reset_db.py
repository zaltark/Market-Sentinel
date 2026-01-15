import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def reset_table():
    print("⚠️  DANGER ZONE: This will wipe ALL data from 'market_data'.")
    confirm = input("Are you sure? Type 'DELETE' to confirm: ")
    
    if confirm == "DELETE":
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS market_data;")
            conn.commit()
            print("✅ Table 'market_data' has been DROPPED.")
            cur.close()
            conn.close()
            
            # Recreate using the latest schema in database.py
            import database
            database.init_db()
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Operation cancelled.")

if __name__ == "__main__":
    reset_table()
