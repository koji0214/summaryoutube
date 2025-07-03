import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/mydatabase")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

async def create_tables():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                title VARCHAR(255) NOT NULL,
                channel_name VARCHAR(255) NOT NULL,
                tags TEXT,
                memo TEXT
            );
        """)
        conn.commit()
        cur.close()
        print("Database table 'videos' ensured.")
    except Exception as e:
        print(f"Error during database startup: {e}")
    finally:
        if conn:
            conn.close()