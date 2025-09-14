import pytest
from src.youtube_api import extract_video_id, get_youtube_video_details, get_transcript_from_youtube, get_high_quality_transcript
import os
from unittest.mock import patch, MagicMock, mock_open
from youtube_transcript_api import FetchedTranscriptSnippet

# テスト実行時に.envファイルの影響を受けないようにする
# モジュールレベルで環境変数をクリア
if 'YOUTUBE_API_KEY' in os.environ:
    del os.environ['YOUTUBE_API_KEY']

# Test cases for extract_video_id
@pytest.mark.parametrize("url, expected_id", [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=youtu.be", "dQw4w9WgXcQ"),
    ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("not_a_youtube_url", None),
    ("", None),
    # (None, None), URLがNoneはフロントで弾いているのでテストしない
])
def test_extract_video_id(url, expected_id):
    assert extract_video_id(url) == expected_id

# Test cases for get_youtube_video_details
@patch('src.youtube_api.build')
@patch.dict(os.environ, {'YOUTUBE_API_KEY': 'test_key'})
def test_get_youtube_video_details_success(mock_build):
    mock_videos = mock_build.return_value.videos.return_value
    mock_videos.list.return_value.execute.return_value = {
        "items": [{
            "snippet": {
                "title": "Test Video Title",
                "channelTitle": "Test Channel Name"
            }
        }]
    }
    title, channel = get_youtube_video_details("test_video_id")
    assert title == "Test Video Title"
    assert channel == "Test Channel Name"

@patch('src.youtube_api.build')
@patch.dict(os.environ, {'YOUTUBE_API_KEY': 'test_key'})
def test_get_youtube_video_details_no_items(mock_build):
    mock_videos = mock_build.return_value.videos.return_value
    mock_videos.list.return_value.execute.return_value = {
        "items": []
    }
    title, channel = get_youtube_video_details("test_video_id")
    assert title is None
    assert channel is None

@patch('src.youtube_api.build')
@patch.dict(os.environ, {'YOUTUBE_API_KEY': 'test_key'})
def test_get_youtube_video_details_http_error(mock_build):
    from googleapiclient.errors import HttpError
    from unittest.mock import Mock
    
    # より簡単なMockオブジェクトを作成
    mock_resp = Mock()
    mock_resp.status = 404
    
    mock_videos = mock_build.return_value.videos.return_value
    mock_videos.list.return_value.execute.side_effect = HttpError(mock_resp, b'Not Found')
    title, channel = get_youtube_video_details("test_video_id")
    assert title is None
    assert channel is None

@patch.dict(os.environ, {}, clear=True) # Ensure YOUTUBE_API_KEY is not set
def test_get_youtube_video_details_no_api_key():
    with pytest.raises(ValueError, match="YouTube API key is not set."):
        get_youtube_video_details("test_video_id")

# Test cases for get_transcript_from_youtube
@patch('src.youtube_api.YouTubeTranscriptApi')
def test_get_transcript_from_youtube_success(mock_youtube_api_class):
    from youtube_transcript_api import FetchedTranscript, FetchedTranscriptSnippet
    from unittest.mock import Mock
    
    # FetchedTranscriptSnippetオブジェクトを作成
    snippet1 = FetchedTranscriptSnippet("Hello", 0.0, 1.0)
    snippet2 = FetchedTranscriptSnippet("world", 1.0, 1.0)
    
    # 辞書形式でアクセスできるようにモック
    snippet1.__getitem__ = lambda self, key: {"text": "Hello", "start": 0, "duration": 1}[key]
    snippet2.__getitem__ = lambda self, key: {"text": "world", "start": 1, "duration": 1}[key]
    
    # FetchedTranscriptオブジェクトを作成
    mock_transcript = FetchedTranscript(
        snippets=[snippet1, snippet2],
        video_id="test_video_id",
        language="English",
        language_code="en",
        is_generated=False
    )
    
    # モックインスタンスを作成
    mock_api_instance = mock_youtube_api_class.return_value
    mock_api_instance.fetch.return_value = mock_transcript
    
    transcript = get_transcript_from_youtube("test_video_id")
    assert transcript == "Hello world"

@patch('src.youtube_api.YouTubeTranscriptApi')
def test_get_transcript_from_youtube_failure(mock_youtube_api_class):
    mock_api_instance = mock_youtube_api_class.return_value
    mock_api_instance.fetch.side_effect = Exception("No transcript available")
    transcript = get_transcript_from_youtube("test_video_id")
    assert transcript is None

# Test cases for get_high_quality_transcript
@patch('src.youtube_api.shutil.rmtree')
@patch('src.youtube_api.tempfile.mkdtemp')
@patch('src.youtube_api.speech.SpeechClient')
@patch('src.youtube_api.yt_dlp.YoutubeDL')
@patch('src.youtube_api.os.path.exists')
@patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
def test_get_high_quality_transcript_success(
    mock_file_open,
    mock_path_exists,
    mock_youtube_dl,
    mock_speech_client,
    mock_mkdtemp,
    mock_rmtree
):
    # Arrange
    mock_path_exists.return_value = True
    mock_mkdtemp.return_value = '/fake/temp/dir'
    
    # speech.SpeechClient().long_running_recognize().result()
    mock_result = MagicMock()
    mock_result.alternatives = [MagicMock()]
    mock_result.alternatives[0].transcript = "This is a high quality transcript."
    
    mock_operation = MagicMock()
    mock_operation.result.return_value = MagicMock(results=[mock_result])
    
    mock_speech_client.return_value.long_running_recognize.return_value = mock_operation

    # Act
    transcript = get_high_quality_transcript('fake_video_id')

    # Assert
    assert transcript == "This is a high quality transcript."
    
    # Check if mocks were called
    mock_mkdtemp.assert_called_once()
    mock_youtube_dl.assert_called_once()
    mock_speech_client.assert_called_once()
    
    # Check that the audio file was opened
    mock_file_open.assert_called_once_with('/fake/temp/dir/fake_video_id.wav', 'rb')
    
    # Check if cleanup was called
    mock_rmtree.assert_called_once_with('/fake/temp/dir')
