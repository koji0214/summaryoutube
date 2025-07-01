from fastapi import HTTPException
from src.database import get_db_connection
from src.youtube_api import extract_video_id, get_youtube_video_details

def create_item_db(url: str):
    video_id = extract_video_id(url)
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
            (url, title, channel_name)
        )
        item_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return {"id": item_id, "url": url, "title": title, "channel_name": channel_name}
    except Exception as e:
        print(f"Error inserting item: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()

def get_items_db():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, url, title, channel_name FROM items ORDER BY id ASC;")
        items = [{"id": row[0], "url": row[1], "title": row[2], "channel_name": row[3]} for row in cur.fetchall()]
        cur.close()
        return items
    except Exception as e:
        print(f"Error fetching items: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()

def update_item_db(item_id: int, url: str):
    video_id = extract_video_id(url)
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
            (url, title, channel_name, item_id)
        )
        updated_id = cur.fetchone()
        conn.commit()
        cur.close()
        if not updated_id:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"id": item_id, "url": url, "title": title, "channel_name": channel_name}
    except Exception as e:
        print(f"Error updating item: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()

def delete_item_db(item_id: int):
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