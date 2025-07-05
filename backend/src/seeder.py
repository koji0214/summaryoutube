from src.database import get_db_connection
from src.youtube_api import extract_video_id, get_youtube_video_details
import os

def seed_data():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the videos table is empty
        cur.execute("SELECT COUNT(*) FROM videos;")
        count = cur.fetchone()[0]

        if count == 0:
            print("Seeding initial data...")
            
            # Sample YouTube video URLs
            videos_to_seed = [
                {
                    "url": "https://youtu.be/aESY2UfxbNg?si=wZZM2SieVYv482yh", 
                    "tags": "music, rickroll", 
                    "memo": "Never gonna give you up"
                },
                {
                    "url": "https://youtu.be/MAz_oROjyEM?si=7TZnx96AW7EGRhBc", 
                    "tags": "programming, python", 
                    "memo": "Python tutorial for beginners"
                },
                {
                    "url": "https://youtu.be/6trwaTXyBkI?si=OjMQ7gJ9gIRRzvRb", 
                    "tags": "travel, japan", 
                    "memo": "Exploring Tokyo"
                }
            ]

            for video_data in videos_to_seed:
                video_id = extract_video_id(video_data["url"])
                if video_id:
                    title, channel_name = get_youtube_video_details(video_id)
                    if title and channel_name:
                        cur.execute(
                            "INSERT INTO videos (url, title, channel_name, tags, memo) VALUES (%s, %s, %s, %s, %s);",
                            (video_data["url"], title, channel_name, video_data["tags"], video_data["memo"])
                        )
                        print(f"Inserted: {title} by {channel_name}")
                    else:
                        print(f"Could not retrieve details for {video_data['url']}. Skipping.")
                else:
                    print(f"Invalid URL: {video_data['url']}. Skipping.")
            
            conn.commit()
            print("Seeding complete.")
        else:
            print("Videos table is not empty. Skipping seeding.")

    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # This part is for local testing of the seeder
    # In a real container build, it will be called from main.py
    # For local testing, ensure DATABASE_URL is set in your environment
    seed_data()
