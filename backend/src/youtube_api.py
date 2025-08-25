import os
import re
import shutil
import tempfile
import yt_dlp
from google.cloud import speech
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi

def get_youtube_video_details(video_id: str):
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    if not youtube_api_key:
        raise ValueError("YouTube API key is not set.")
    
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    
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

def get_transcript_from_youtube(video_id: str):
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id, languages=['ja', 'en'])
        transcript = " ".join([item['text'] for item in transcript_list.to_raw_data()])
        return transcript
    except Exception as e:
        print(f"Could not retrieve transcript for video {video_id}: {e}")
        return None

def get_high_quality_transcript(video_id: str, lang_code: str = "ja-JP"):
    audio_path = None
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav', 'preferredquality': '192'}],
            'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
            'quiet': True,
        }

        print(f"Downloading audio for video: {video_id}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        audio_path = os.path.join(temp_dir, f"{video_id}.wav")
        print(f"Audio downloaded to: {audio_path}")

        if not os.path.exists(audio_path):
            raise FileNotFoundError("Audio file was not created.")

        print("Transcribing with Google Cloud Speech-to-Text...")
        client = speech.SpeechClient()

        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100, # yt-dlp wav is often 44100Hz
            language_code=lang_code,
            enable_automatic_punctuation=True
        )

        operation = client.long_running_recognize(config=config, audio=audio)
        print("Waiting for transcription to complete...")
        response = operation.result(timeout=600)

        transcript = "".join(result.alternatives[0].transcript for result in response.results)
        print("Transcription finished.")
        return transcript

    except Exception as e:
        print(f"An error occurred during high-quality transcription: {e}")
        return None
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Removed temporary directory and its contents: {temp_dir}")


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