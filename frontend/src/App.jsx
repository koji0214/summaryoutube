import { useState, useEffect } from 'react'
import './App.css'

function App() {
  // State for the "Add New Video" form
  const [url, setUrl] = useState('');
  const [tags, setTags] = useState([]);
  const [memo, setMemo] = useState('');
  const [newTag, setNewTag] = useState('');


  // State for the list of videos
  const [videos, setVideos] = useState([]);
  const [allTags, setAllTags] = useState([]);

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

  const fetchTags = () => {
    fetch('/api/tags/')
      .then((res) => res.json())
      .then((data) => setAllTags(data))
      .catch((err) => console.error("Error fetching tags:", err));
  };

  useEffect(() => {
    fetchVideos();
    fetchTags();
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
        body: JSON.stringify({ url, tags: tags.join(','), memo }),
      });
      if (response.ok) {
        setUrl('');
        setTags([]);
        setMemo('');
        fetchVideos();
        fetchTags();
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
        fetchTags();
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
    setCurrentEditData({
      url: video.url,
      tags: video.tags ? video.tags.split(',').map(t => t.trim()) : [],
      memo: video.memo || ''
    });
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
        body: JSON.stringify({ ...currentEditData, tags: currentEditData.tags.join(',') }),
      });
      if (response.ok) {
        setEditingVideoId(null);
        setCurrentEditData({ url: '', tags: '', memo: '' });
        fetchVideos();
        fetchTags();
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

  const handleTagSelect = (e) => {
    const selectedTag = e.target.value;
    if (selectedTag && !tags.includes(selectedTag)) {
      setTags([...tags, selectedTag]);
    }
  };

  const handleAddNewTag = () => {
    if (newTag && !tags.includes(newTag)) {
      setTags([...tags, newTag]);
      if (!allTags.includes(newTag)) {
        setAllTags([...allTags, newTag]);
      }
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleEditTagSelect = (e) => {
    const selectedTag = e.target.value;
    if (selectedTag && !currentEditData.tags.includes(selectedTag)) {
      setCurrentEditData(prev => ({ ...prev, tags: [...prev.tags, selectedTag] }));
    }
  };

  const handleEditAddNewTag = (e) => {
    const newTagValue = e.target.value;
    if (e.key === 'Enter' && newTagValue) {
      e.preventDefault();
      if (!currentEditData.tags.includes(newTagValue)) {
        setCurrentEditData(prev => ({ ...prev, tags: [...prev.tags, newTagValue] }));
        if (!allTags.includes(newTagValue)) {
          setAllTags([...allTags, newTagValue]);
        }
      }
      e.target.value = '';
    }
  };

  const handleEditRemoveTag = (tagToRemove) => {
    setCurrentEditData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
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
          <div className="tag-container">
            {tags.map(tag => (
              <span key={tag} className="tag-item">
                {tag}
                <button type="button" onClick={() => handleRemoveTag(tag)} className="tag-remove-button">x</button>
              </span>
            ))}
          </div>
          <div style={{ marginTop: '5px' }}>
            <select onChange={handleTagSelect} value="">
              <option value="" disabled>Select existing tag</option>
              {allTags.filter(t => !tags.includes(t)).map(tag => (
                <option key={tag} value={tag}>{tag}</option>
              ))}
            </select>
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder="Or add a new tag"
              style={{ marginLeft: '10px' }}
            />
            <button type="button" onClick={handleAddNewTag}>Add Tag</button>
          </div>
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
                    <div>
                      <div className="tag-container">
                        {currentEditData.tags.map(tag => (
                          <span key={tag} className="tag-item">
                            {tag}
                            <button type="button" onClick={() => handleEditRemoveTag(tag)} className="tag-remove-button">x</button>
                          </span>
                        ))}
                      </div>
                      <div style={{ marginTop: '5px' }}>
                        <select onChange={handleEditTagSelect} value="">
                          <option value="" disabled>Select existing tag</option>
                          {allTags.filter(t => !currentEditData.tags.includes(t)).map(tag => (
                            <option key={tag} value={tag}>{tag}</option>
                          ))}
                        </select>
                        <input
                          type="text"
                          placeholder="Add new tag and press Enter"
                          onKeyDown={handleEditAddNewTag}
                          style={{ marginLeft: '10px' }}
                        />
                      </div>
                    </div>
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