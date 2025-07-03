from fastapi import HTTPException
from src.database import get_db_connection
from src.youtube_api import extract_video_id, get_youtube_video_details
from src.models import Video

def create_video_db(video: Video):
    video_id = extract_video_id(video.url)
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
            "INSERT INTO videos (url, title, channel_name, tags, memo) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
            (video.url, title, channel_name, video.tags, video.memo)
        )
        video_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return {"id": video_id, "url": video.url, "title": title, "channel_name": channel_name, "tags": video.tags, "memo": video.memo}
    except Exception as e:
        print(f"Error inserting video: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()

def get_videos_db():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, url, title, channel_name, tags, memo FROM videos ORDER BY id ASC;")
        videos = [{"id": row[0], "url": row[1], "title": row[2], "channel_name": row[3], "tags": row[4], "memo": row[5]} for row in cur.fetchall()]
        cur.close()
        return videos
    except Exception as e:
        print(f"Error fetching videos: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()

def update_video_db(video_id: int, video: Video):
    video_id_extracted = extract_video_id(video.url)
    if not video_id_extracted:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    title, channel_name = get_youtube_video_details(video_id_extracted)
    if not title or not channel_name:
        raise HTTPException(status_code=500, detail="Could not retrieve video details from YouTube API.")

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE videos SET url = %s, title = %s, channel_name = %s, tags = %s, memo = %s WHERE id = %s RETURNING id;",
            (video.url, title, channel_name, video.tags, video.memo, video_id)
        )
        updated_id = cur.fetchone()
        conn.commit()
        cur.close()
        if not updated_id:
            raise HTTPException(status_code=404, detail="Video not found")
        return {"id": video_id, "url": video.url, "title": title, "channel_name": channel_name, "tags": video.tags, "memo": video.memo}
    except Exception as e:
        print(f"Error updating video: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()

def delete_video_db(video_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM videos WHERE id = %s RETURNING id;", (video_id,))
        deleted_id = cur.fetchone()
        conn.commit()
        cur.close()
        if not deleted_id:
            raise HTTPException(status_code=404, detail="Video not found")
        return {"message": "Video deleted successfully"}
    except Exception as e:
        print(f"Error deleting video: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()