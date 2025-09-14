from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import Video
from src.youtube_api import extract_video_id, get_youtube_video_details

def seed_data():
    db = SessionLocal()
    try:
        # Check if the videos table is empty
        count = db.query(Video).count()

        if count == 0:
            print("Seeding initial data...")
            
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
                video_id_yt = extract_video_id(video_data["url"])
                if video_id_yt:
                    title, channel_name = get_youtube_video_details(video_id_yt)
                    if title and channel_name:
                        db_video = Video(
                            url=video_data["url"],
                            title=title,
                            channel_name=channel_name,
                            tags=video_data["tags"],
                            memo=video_data["memo"],
                            status='completed' # Default status for seeded data
                        )
                        db.add(db_video)
                        print(f"Staged for insertion: {title} by {channel_name}")
                    else:
                        print(f"Could not retrieve details for {video_data['url']}. Skipping.")
                else:
                    print(f"Invalid URL: {video_data['url']}. Skipping.")
            
            db.commit()
            print("Seeding complete.")
        else:
            print("Videos table is not empty. Skipping seeding.")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()