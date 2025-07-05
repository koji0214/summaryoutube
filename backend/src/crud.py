from fastapi import HTTPException
from src.database import get_db_connection
from src.youtube_api import extract_video_id, get_youtube_video_details
from src.models import Video
from typing import Optional

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
            "INSERT INTO videos (url, title, channel_name, tags, memo) VALUES (%s, %s, %s, %s, %s) RETURNING id, created_at, updated_at;",
            (video.url, title, channel_name, video.tags, video.memo)
        )
        result = cur.fetchone()
        video_id = result[0]
        created_at = result[1]
        updated_at = result[2]
        conn.commit()
        cur.close()
        return {"id": video_id, "url": video.url, "title": title, "channel_name": channel_name, "tags": video.tags, "memo": video.memo, "created_at": created_at, "updated_at": updated_at}
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
        cur.execute("SELECT id, url, title, channel_name, tags, memo, created_at, updated_at FROM videos ORDER BY id ASC;")
        videos = [{"id": row[0], "url": row[1], "title": row[2], "channel_name": row[3], "tags": row[4], "memo": row[5], "created_at": row[6], "updated_at": row[7]} for row in cur.fetchall()]
        cur.close()
        return videos
    except Exception as e:
        print(f"Error fetching videos: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()

def search_videos_db(title_query: Optional[str] = None, tags_query: Optional[str] = None, sort_by: str = "id", sort_order: str = "asc"):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        sql_query = "SELECT id, url, title, channel_name, tags, memo, created_at, updated_at FROM videos"
        conditions = []
        params = []

        if title_query:
            conditions.append("title ILIKE %s")
            params.append(f"%{title_query}%")
        
        if tags_query:
            conditions.append("string_to_array(tags, ',') @> string_to_array(%s, ',')")
            params.append(tags_query)

        if conditions:
            sql_query += " WHERE " + " AND ".join(conditions)
        
        # Sorting
        valid_sort_columns = {"id", "title", "channel_name", "created_at", "updated_at"}
        if sort_by not in valid_sort_columns:
            sort_by = "id" # Default to id if invalid column is provided
        
        sort_order = sort_order.upper()
        if sort_order not in {"ASC", "DESC"}:
            sort_order = "ASC" # Default to ASC if invalid order is provided

        sql_query += f" ORDER BY {sort_by} {sort_order};"

        cur.execute(sql_query, tuple(params))
        videos = [{"id": row[0], "url": row[1], "title": row[2], "channel_name": row[3], "tags": row[4], "memo": row[5], "created_at": row[6], "updated_at": row[7]} for row in cur.fetchall()]
        cur.close()
        return videos
    except Exception as e:
        print(f"Error searching videos: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()

def update_video_db(video_id: int, video: Video):
    conn = get_db_connection()
    cur = conn.cursor()

    # 現在の動画情報を取得
    cur.execute("SELECT url, title, channel_name FROM videos WHERE id = %s;", (video_id,))
    current_video = cur.fetchone()
    if not current_video:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Video not found")

    current_url, current_title, current_channel_name = current_video

    # URLが変更されたか確認
    if video.url != current_url:
        video_id_extracted = extract_video_id(video.url)
        if not video_id_extracted:
            cur.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        title, channel_name = get_youtube_video_details(video_id_extracted)
        if not title or not channel_name:
            cur.close()
            conn.close()
            raise HTTPException(status_code=500, detail="Could not retrieve video details from YouTube API.")
    else:
        # URLが変更されていない場合は、既存のタイトルとチャンネル名を使用
        title, channel_name = current_title, current_channel_name

    try:
        cur.execute(
            "UPDATE videos SET url = %s, title = %s, channel_name = %s, tags = %s, memo = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING id, created_at, updated_at;",
            (video.url, title, channel_name, video.tags, video.memo, video_id)
        )
        updated_result = cur.fetchone()
        if not updated_result:
            raise HTTPException(status_code=404, detail="Video not found")
        updated_id, created_at, updated_at = updated_result
        conn.commit()
        return {"id": updated_id, "url": video.url, "title": title, "channel_name": channel_name, "tags": video.tags, "memo": video.memo, "created_at": created_at, "updated_at": updated_at}
    except Exception as e:
        conn.rollback()
        print(f"Error updating video: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        cur.close()
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

def get_all_tags_db():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT tags FROM videos;")
        all_tags = []
        rows = cur.fetchall()
        for row in rows:
            if row[0]:
                all_tags.extend([tag.strip() for tag in row[0].split(',')])
        
        # Remove duplicates and sort
        unique_tags = sorted(list(set(all_tags)))
        
        cur.close()
        return unique_tags
    except Exception as e:
        print(f"Error fetching tags: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn.close()