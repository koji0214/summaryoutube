from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = FastAPI()

# Pydanticモデルの定義
class Item(BaseModel):
    url: str

# データベース接続情報
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/mydatabase")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def get_youtube_video_details(video_id: str):
    if not YOUTUBE_API_KEY:
        raise ValueError("YouTube API key is not set.")
    
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    try:
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        
        if not response.get("items"):
            return None, None

        video_snippet = response["items"][0]["snippet"]
        title = video_snippet["title"]
        channel_title = video_snippet["channelTitle"]
        
        return title, channel_title
        
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return None, None

def extract_video_id(url: str):
    # YouTubeのURLから動画IDを抽出する正規表現
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^?]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.on_event("startup")
async def startup_event():
    # アプリケーション起動時にテーブルを再作成
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # 既存のテーブルを削除
        cur.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                title VARCHAR(255) NOT NULL,
                channel_name VARCHAR(255) NOT NULL
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
    video_id = extract_video_id(item.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    title, channel_name = get_youtube_video_details(video_id)
    if not title or not channel_name:
        raise HTTPException(status_code=500, detail="Could not retrieve video details from YouTube API.")

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO items (url, title, channel_name) VALUES (%s, %s, %s) RETURNING id;",
            (item.url, title, channel_name)
        )
        item_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return {"id": item_id, "url": item.url, "title": title, "channel_name": channel_name}
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
        cur.execute("SELECT id, url, title, channel_name FROM items;")
        items = [{"id": row[0], "url": row[1], "title": row[2], "channel_name": row[3]} for row in cur.fetchall()]
        cur.close()
        return items
    except Exception as e:
        print(f"Error fetching items: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    video_id = extract_video_id(item.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    title, channel_name = get_youtube_video_details(video_id)
    if not title or not channel_name:
        raise HTTPException(status_code=500, detail="Could not retrieve video details from YouTube API.")

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE items SET url = %s, title = %s, channel_name = %s WHERE id = %s RETURNING id;",
            (item.url, title, channel_name, item_id)
        )
        updated_id = cur.fetchone()
        conn.commit()
        cur.close()
        if not updated_id:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"id": item_id, "url": item.url, "title": title, "channel_name": channel_name}
    except Exception as e:
        print(f"Error updating item: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM items WHERE id = %s RETURNING id;", (item_id,))
        deleted_id = cur.fetchone()
        conn.commit()
        cur.close()
        if not deleted_id:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item deleted successfully"}
    except Exception as e:
        print(f"Error deleting item: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()