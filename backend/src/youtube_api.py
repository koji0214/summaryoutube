import os
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

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