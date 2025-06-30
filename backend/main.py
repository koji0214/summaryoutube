from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

# Pydanticモデルの定義
class Item(BaseModel):
    name: str

# データベース接続情報
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/mydatabase")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.on_event("startup")
async def startup_event():
    # アプリケーション起動時にテーブルを作成
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            );
        """)
        conn.commit()
        cur.close()
        print("Database table 'items' ensured.")
    except Exception as e:
        print(f"Error during database startup: {e}")
    finally:
        if conn:
            conn.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/items/")
def create_item(item: Item):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO items (name) VALUES (%s) RETURNING id;", (item.name,))
        item_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return {"id": item_id, "name": item.name}
    except Exception as e:
        print(f"Error inserting item: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()

@app.get("/items/")
def read_items():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM items;")
        items = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
        cur.close()
        return items
    except Exception as e:
        print(f"Error fetching items: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()