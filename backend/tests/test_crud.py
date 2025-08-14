import pytest
from src.crud import (
    create_video_db, get_videos_db, search_videos_db,
    update_video_db, delete_video_db, get_all_tags_db
)
from src.models import Video
from fastapi import HTTPException
from unittest.mock import MagicMock, patch

# Mock for database connection
@pytest.fixture
def mock_db_connection():
    with patch('src.database.get_db_connection') as mock_get_db_conn:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_conn, mock_cursor

# Mock for youtube_api functions
@pytest.pytest.fixture
def mock_youtube_api():
    with patch('src.crud.extract_video_id') as mock_extract_video_id, \
         patch('src.crud.get_youtube_video_details') as mock_get_youtube_video_details, \
         patch('src.crud.get_transcript_from_youtube') as mock_get_transcript_from_youtube:
        yield mock_extract_video_id, mock_get_youtube_video_details, mock_get_transcript_from_youtube

# Test create_video_db
def test_create_video_db_success(mock_db_connection, mock_youtube_api):
    mock_conn, mock_cursor = mock_db_connection
    mock_extract_video_id, mock_get_youtube_video_details, mock_get_transcript_from_youtube = mock_youtube_api

    mock_extract_video_id.return_value = "test_video_id"
    mock_get_youtube_video_details.return_value = ("Test Title", "Test Channel")
    mock_get_transcript_from_youtube.return_value = "Test Transcript"
    mock_cursor.fetchone.return_value = (1, "2023-01-01", "2023-01-01") # id, created_at, updated_at

    video_data = Video(
        url="https://www.youtube.com/watch?v=test_video_id",
        tags="tag1,tag2",
        memo="Test Memo",
        transcriptionOption="standard"
    )
    result = create_video_db(video_data)

    mock_extract_video_id.assert_called_once_with(video_data.url)
    mock_get_youtube_video_details.assert_called_once_with("test_video_id")
    mock_get_transcript_from_youtube.assert_called_once_with("test_video_id")
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    assert result["title"] == "Test Title"
    assert result["channel_name"] == "Test Channel"
    assert result["transcript"] == "Test Transcript"

def test_create_video_db_invalid_url(mock_db_connection, mock_youtube_api):
    mock_conn, mock_cursor = mock_db_connection
    mock_extract_video_id, _, _ = mock_youtube_api

    mock_extract_video_id.return_value = None

    video_data = Video(
        url="invalid_url",
        tags="tag1",
        memo="Test Memo",
        transcriptionOption="none"
    )
    with pytest.raises(HTTPException) as exc_info:
        create_video_db(video_data)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid YouTube URL"

def test_create_video_db_youtube_details_failure(mock_db_connection, mock_youtube_api):
    mock_conn, mock_cursor = mock_db_connection
    mock_extract_video_id, mock_get_youtube_video_details, _ = mock_youtube_api

    mock_extract_video_id.return_value = "test_video_id"
    mock_get_youtube_video_details.return_value = (None, None)

    video_data = Video(
        url="https://www.youtube.com/watch?v=test_video_id",
        tags="tag1",
        memo="Test Memo",
        transcriptionOption="none"
    )
    with pytest.raises(HTTPException) as exc_info:
        create_video_db(video_data)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Could not retrieve video details from YouTube API."

def test_create_video_db_db_error(mock_db_connection, mock_youtube_api):
    mock_conn, mock_cursor = mock_db_connection
    mock_extract_video_id, mock_get_youtube_video_details, mock_get_transcript_from_youtube = mock_youtube_api

    mock_extract_video_id.return_value = "test_video_id"
    mock_get_youtube_video_details.return_value = ("Test Title", "Test Channel")
    mock_get_transcript_from_youtube.return_value = "Test Transcript"
    mock_cursor.execute.side_effect = Exception("DB connection error")

    video_data = Video(
        url="https://www.youtube.com/watch?v=test_video_id",
        tags="tag1",
        memo="Test Memo",
        transcriptionOption="standard"
    )
    with pytest.raises(HTTPException) as exc_info:
        create_video_db(video_data)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"
    mock_conn.rollback.assert_called_once() # Ensure rollback is called on error

# Test get_videos_db
def test_get_videos_db_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        (1, "url1", "title1", "channel1", "tag1", "memo1", "2023-01-01", "2023-01-01"),
        (2, "url2", "title2", "channel2", "tag2", "memo2", "2023-01-02", "2023-01-02"),
    ]
    videos = get_videos_db()
    mock_cursor.execute.assert_called_once_with("SELECT id, url, title, channel_name, tags, memo, created_at, updated_at FROM videos ORDER BY id ASC;")
    assert len(videos) == 2
    assert videos[0]["title"] == "title1"

def test_get_videos_db_db_error(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.execute.side_effect = Exception("DB error")
    with pytest.raises(HTTPException) as exc_info:
        get_videos_db()
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"

# Test search_videos_db
@pytest.mark.parametrize("title_query, tags_query, sort_by, sort_order, expected_sql_part, expected_params", [
    (None, None, "id", "asc", "ORDER BY id ASC;", ())
    ( "test", None, "id", "asc", "WHERE title ILIKE %s ORDER BY id ASC;", ("%test%",)),
    (None, "tag1", "id", "asc", "WHERE string_to_array(tags, ",") @> string_to_array(%s, ",") ORDER BY id ASC;", ("tag1",)),
    ("test", "tag1", "title", "desc", "WHERE title ILIKE %s AND string_to_array(tags, ",") @> string_to_array(%s, ",") ORDER BY title DESC;", ("%test%", "tag1")),
    (None, None, "invalid_col", "invalid_order", "ORDER BY id ASC;", ()), # Test invalid sort
])
def test_search_videos_db_success(mock_db_connection, title_query, tags_query, sort_by, sort_order, expected_sql_part, expected_params):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [] # Return empty list for simplicity

    search_videos_db(title_query, tags_query, sort_by, sort_order)
    
    called_sql = mock_cursor.execute.call_args[0][0]
    called_params = mock_cursor.execute.call_args[0][1]

    assert expected_sql_part in called_sql
    assert called_params == expected_params

def test_search_videos_db_db_error(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.execute.side_effect = Exception("DB error")
    with pytest.raises(HTTPException) as exc_info:
        search_videos_db()
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"

# Test update_video_db
def test_update_video_db_success(mock_db_connection, mock_youtube_api):
    mock_conn, mock_cursor = mock_db_connection
    mock_extract_video_id, mock_get_youtube_video_details, _ = mock_youtube_api

    # Mock initial fetch for current video
    mock_cursor.fetchone.side_effect = [
        ("old_url", "old_title", "old_channel"), # For SELECT
        (1, "2023-01-01", "2023-01-02") # For UPDATE RETURNING
    ]

    mock_extract_video_id.return_value = "new_video_id"
    mock_get_youtube_video_details.return_value = ("New Title", "New Channel")

    video_data = Video(
        url="https://www.youtube.com/watch?v=new_video_id",
        tags="new_tag",
        memo="New Memo",
        transcriptionOption="none"
    )
    result = update_video_db(1, video_data)

    assert result["title"] == "New Title"
    assert result["channel_name"] == "New Channel"
    mock_conn.commit.assert_called_once()

def test_update_video_db_no_url_change(mock_db_connection, mock_youtube_api):
    mock_conn, mock_cursor = mock_db_connection
    mock_extract_video_id, mock_get_youtube_video_details, _ = mock_youtube_api

    # Mock initial fetch for current video
    mock_cursor.fetchone.side_effect = [
        ("same_url", "same_title", "same_channel"), # For SELECT
        (1, "2023-01-01", "2023-01-02") # For UPDATE RETURNING
    ]

    video_data = Video(
        url="same_url",
        tags="new_tag",
        memo="New Memo",
        transcriptionOption="none"
    )
    result = update_video_db(1, video_data)

    mock_extract_video_id.assert_not_called()
    mock_get_youtube_video_details.assert_not_called()
    assert result["title"] == "same_title"
    assert result["channel_name"] == "same_channel"
    mock_conn.commit.assert_called_once()

def test_update_video_db_video_not_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None # No video found for SELECT

    video_data = Video(
        url="https://www.youtube.com/watch?v=test",
        tags="tag",
        memo="memo",
        transcriptionOption="none"
    )
    with pytest.raises(HTTPException) as exc_info:
        update_video_db(999, video_data)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Video not found"

def test_update_video_db_invalid_url_on_update(mock_db_connection, mock_youtube_api):
    mock_conn, mock_cursor = mock_db_connection
    mock_extract_video_id, _, _ = mock_youtube_api

    mock_cursor.fetchone.side_effect = [
        ("old_url", "old_title", "old_channel"), # For SELECT
    ]
    mock_extract_video_id.return_value = None

    video_data = Video(
        url="invalid_url",
        tags="tag",
        memo="memo",
        transcriptionOption="none"
    )
    with pytest.raises(HTTPException) as exc_info:
        update_video_db(1, video_data)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid YouTube URL"

def test_update_video_db_db_error(mock_db_connection, mock_youtube_api):
    mock_conn, mock_cursor = mock_db_connection
    mock_extract_video_id, mock_get_youtube_video_details, _ = mock_youtube_api

    mock_cursor.fetchone.side_effect = [
        ("old_url", "old_title", "old_channel"), # For SELECT
    ]
    mock_extract_video_id.return_value = "test_video_id"
    mock_get_youtube_video_details.return_value = ("New Title", "New Channel")
    mock_cursor.execute.side_effect = Exception("DB update error")

    video_data = Video(
        url="https://www.youtube.com/watch?v=new_video_id",
        tags="new_tag",
        memo="New Memo",
        transcriptionOption="none"
    )
    with pytest.raises(HTTPException) as exc_info:
        update_video_db(1, video_data)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"
    mock_conn.rollback.assert_called_once()

# Test delete_video_db
def test_delete_video_db_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = (1,) # Return deleted ID
    result = delete_video_db(1)
    mock_cursor.execute.assert_called_once_with("DELETE FROM videos WHERE id = %s RETURNING id;", (1,))
    mock_conn.commit.assert_called_once()
    assert result == {"message": "Video deleted successfully"}

def test_delete_video_db_not_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None # No video found
    with pytest.raises(HTTPException) as exc_info:
        delete_video_db(999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Video not found"

def test_delete_video_db_db_error(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.execute.side_effect = Exception("DB error")
    with pytest.raises(HTTPException) as exc_info:
        delete_video_db(1)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"

# Test get_all_tags_db
def test_get_all_tags_db_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        ("tag1,tag2",),
        ("tag2,tag3",),
        ("tag4",),
        (None,) # Test with None tags
    ]
    tags = get_all_tags_db()
    mock_cursor.execute.assert_called_once_with("SELECT tags FROM videos;")
    assert sorted(tags) == ["tag1", "tag2", "tag3", "tag4"]

def test_get_all_tags_db_db_error(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.execute.side_effect = Exception("DB error")
    with pytest.raises(HTTPException) as exc_info:
        get_all_tags_db()
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"
