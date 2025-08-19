import pytest
from fastapi.testclient import TestClient
from src.main import app, API_PREFIX
from unittest.mock import patch, MagicMock
from src.models import Video

# Mock the startup events to prevent actual table creation and seeding during tests
@pytest.fixture(autouse=True)
def mock_startup_events():
    with patch('src.main.create_tables'), \
         patch('src.main.seed_data'):
        yield

client = TestClient(app)

# Test read_root
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

# Test create_video
@patch('src.routers.videos.create_video_db')
def test_create_video_success(mock_create_video_db):
    mock_create_video_db.return_value = {
        "id": 1,
        "url": "https://www.youtube.com/watch?v=test",
        "title": "Test Video",
        "channel_name": "Test Channel",
        "tags": "tag1,tag2",
        "memo": "Test Memo",
        "transcript": "Test Transcript",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
    }
    video_data = {
        "url": "https://www.youtube.com/watch?v=test",
        "tags": "tag1,tag2",
        "memo": "Test Memo",
        "transcriptionOption": "standard"
    }
    response = client.post(f"{API_PREFIX}/videos/", json=video_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Video"
    mock_create_video_db.assert_called_once()

@patch('src.routers.videos.create_video_db')
def test_create_video_invalid_data(mock_create_video_db):
    # Missing required field 'url'
    video_data = {
        "tags": "tag1,tag2",
        "memo": "Test Memo",
        "transcriptionOption": "standard"
    }
    response = client.post(f"{API_PREFIX}/videos/", json=video_data)
    assert response.status_code == 422 # Unprocessable Entity for validation errors
    mock_create_video_db.assert_not_called()

# Test read_videos (search_videos_db)
@patch('src.routers.videos.search_videos_db')
def test_read_videos_no_params(mock_search_videos_db):
    mock_search_videos_db.return_value = [
        {"id": 1, "title": "Video 1"},
        {"id": 2, "title": "Video 2"}
    ]
    response = client.get(f"{API_PREFIX}/videos/")
    assert response.status_code == 200
    assert len(response.json()) == 2
    mock_search_videos_db.assert_called_once_with(None, None, "id", "asc")

@patch('src.routers.videos.search_videos_db')
def test_read_videos_with_params(mock_search_videos_db):
    mock_search_videos_db.return_value = [
        {"id": 1, "title": "Filtered Video"}
    ]
    response = client.get(f"{API_PREFIX}/videos/?title_query=filtered&tags_query=tag1&sort_by=title&sort_order=desc")
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_search_videos_db.assert_called_once_with("filtered", "tag1", "title", "desc")

# Test read_tags
@patch('src.routers.tags.get_all_tags_db')
def test_read_tags_success(mock_get_all_tags_db):
    mock_get_all_tags_db.return_value = ["tag1", "tag2", "tag3"]
    response = client.get(f"{API_PREFIX}/tags/")
    assert response.status_code == 200
    assert response.json() == ["tag1", "tag2", "tag3"]
    mock_get_all_tags_db.assert_called_once()

# Test update_video
@patch('src.routers.videos.update_video_db')
def test_update_video_success(mock_update_video_db):
    mock_update_video_db.return_value = {
        "id": 1,
        "url": "https://www.youtube.com/watch?v=updated",
        "title": "Updated Video",
        "channel_name": "Updated Channel",
        "tags": "new_tag",
        "memo": "Updated Memo",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-02T00:00:00"
    }
    video_data = {
        "url": "https://www.youtube.com/watch?v=updated",
        "tags": "new_tag",
        "memo": "Updated Memo",
        "transcriptionOption": "none"
    }
    response = client.put(f"{API_PREFIX}/videos/1", json=video_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Video"
    mock_update_video_db.assert_called_once_with(1, Video(**video_data))

@patch('src.routers.videos.update_video_db')
def test_update_video_not_found(mock_update_video_db):
    from fastapi import HTTPException
    mock_update_video_db.side_effect = HTTPException(status_code=404, detail="Video not found")
    video_data = {
        "url": "https://www.youtube.com/watch?v=test",
        "tags": "tag",
        "memo": "memo",
        "transcriptionOption": "none"
    }
    response = client.put(f"{API_PREFIX}/videos/999", json=video_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Video not found"

# Test delete_video
@patch('src.routers.videos.delete_video_db')
def test_delete_video_success(mock_delete_video_db):
    mock_delete_video_db.return_value = {"message": "Video deleted successfully"}
    response = client.delete(f"{API_PREFIX}/videos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Video deleted successfully"
    mock_delete_video_db.assert_called_once_with(1)

@patch('src.routers.videos.delete_video_db')
def test_delete_video_not_found(mock_delete_video_db):
    from fastapi import HTTPException
    mock_delete_video_db.side_effect = HTTPException(status_code=404, detail="Video not found")
    response = client.delete(f"{API_PREFIX}/videos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Video not found"
