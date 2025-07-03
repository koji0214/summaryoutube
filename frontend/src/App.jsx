import { useState, useEffect } from 'react'
import './App.css'

function App() {
  // State for the "Add New Video" form
  const [url, setUrl] = useState('');
  const [tags, setTags] = useState('');
  const [memo, setMemo] = useState('');

  // State for the list of videos
  const [videos, setVideos] = useState([]);

  // State for inline editing
  const [editingVideoId, setEditingVideoId] = useState(null);
  const [currentEditData, setCurrentEditData] = useState({ url: '', tags: '', memo: '' });

  // Helper function to extract video ID from YouTube URL
  const extractVideoId = (url) => {
    const patterns = [
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)/,
      /(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)/,
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)/,
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^?]+)/
    ];
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) {
        return match[1];
      }
    }
    return null;
  };

  // Fetch video list from the backend
  const fetchVideos = () => {
    fetch('/api/videos/')
      .then((res) => res.json())
      .then((data) => setVideos(data))
      .catch((err) => console.error("Error fetching videos:", err));
  };

  useEffect(() => {
    fetchVideos();
  }, []);

  // Handle submission of the "Add New Video" form
  const handleAddSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/videos/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, tags, memo }),
      });
      if (response.ok) {
        setUrl('');
        setTags('');
        setMemo('');
        fetchVideos();
      } else {
        console.error("Failed to add video");
      }
    } catch (error) {
      console.error("Error adding video:", error);
    }
  };

  // Handle video deletion
  const handleDelete = async (id) => {
    try {
      const response = await fetch(`/api/videos/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        fetchVideos();
      } else {
        console.error("Failed to delete video");
      }
    } catch (error) {
      console.error("Error deleting video:", error);
    }
  };

  // Handle clicking the "Edit" button
  const handleEditClick = (video) => {
    setEditingVideoId(video.id);
    setCurrentEditData({ url: video.url, tags: video.tags || '', memo: video.memo || '' });
  };

  // Handle submission of the inline edit form
  const handleUpdateSubmit = async (e, videoId) => {
    e.preventDefault();
    try {
      const response = await fetch(`/api/videos/${videoId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(currentEditData),
      });
      if (response.ok) {
        setEditingVideoId(null);
        setCurrentEditData({ url: '', tags: '', memo: '' });
        fetchVideos();
      } else {
        console.error("Failed to update video");
      }
    } catch (error) {
      console.error("Error updating video:", error);
    }
  };

  // Handle canceling the edit
  const handleCancelEdit = () => {
    setEditingVideoId(null);
    setCurrentEditData({ url: '', tags: '', memo: '' });
  };

  // Handle changes in the inline edit form
  const handleEditFormChange = (e) => {
    const { name, value } = e.target;
    setCurrentEditData(prev => ({ ...prev, [name]: value }));
  };


  return (
    <>
      <h1>YouTube Video List</h1>

      <h2>Add New Video</h2>
      <form onSubmit={handleAddSubmit}>
        <div>
          <label>YouTube URL: </label>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter YouTube URL"
            required
            style={{ width: '400px' }}
          />
        </div>
        <div>
          <label>Tags: </label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="Enter tags (comma-separated)"
            style={{ width: '400px' }}
          />
        </div>
        <div>
          <label>Memo: </label>
          <textarea
            value={memo}
            onChange={(e) => setMemo(e.target.value)}
            placeholder="Enter a memo"
            style={{ width: '400px', height: '80px' }}
          />
        </div>
        <button type="submit">Add Video</button>
      </form>

      <h2>Videos from Database</h2>
      {videos.length === 0 ? (
        <p>No videos yet.</p>
      ) : (
        <ul>
          {videos.map((video) => {
            const videoId = extractVideoId(video.url);
            const isEditing = editingVideoId === video.id;

            return (
              <li key={video.id}>
                <strong>Title:</strong> {video.title}<br />
                <strong>Channel:</strong> {video.channel_name}<br />

                {isEditing ? (
                  <form onSubmit={(e) => handleUpdateSubmit(e, video.id)}>
                    <strong>URL: </strong>
                    <input
                      type="text"
                      name="url"
                      value={currentEditData.url}
                      onChange={handleEditFormChange}
                      required
                      style={{ width: '400px' }}
                    /><br />
                    <strong>Tags: </strong>
                    <input
                      type="text"
                      name="tags"
                      value={currentEditData.tags}
                      onChange={handleEditFormChange}
                      placeholder="Enter tags (comma-separated)"
                      style={{ width: '400px' }}
                    /><br />
                    <strong>Memo: </strong>
                    <textarea
                      name="memo"
                      value={currentEditData.memo}
                      onChange={handleEditFormChange}
                      placeholder="Enter a memo"
                      style={{ width: '400px', height: '60px' }}
                    /><br />
                    <button type="submit">Save</button>
                    <button type="button" onClick={handleCancelEdit}>Cancel</button>
                  </form>
                ) : (
                  <>
                    <a href={video.url} target="_blank" rel="noopener noreferrer">{video.url}</a><br />
                    <strong>Tags:</strong> {video.tags || 'N/A'}<br />
                    <strong>Memo:</strong> {video.memo || 'N/A'}<br />
                    <button onClick={() => handleEditClick(video)}>Edit</button>
                    <button onClick={() => handleDelete(video.id)}>Delete</button>
                  </>
                )}
                <br />
                {videoId && (
                  <iframe
                    width="560"
                    height="315"
                    src={`https://www.youtube.com/embed/${videoId}`}
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    title={video.title}
                  ></iframe>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </>
  )
}

export default App