import { useState, useEffect } from 'react';
import './App.css';
import VideoForm from './components/VideoForm';
import VideoList from './components/VideoList';
import TagMultiSelect from './components/TagMultiSelect';

function App() {
  const [videos, setVideos] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [editingVideoId, setEditingVideoId] = useState(null);
  const [currentEditData, setCurrentEditData] = useState({ url: '', tags: [], memo: '' });
  const [showModal, setShowModal] = useState(false); // State for modal visibility
  const [searchTitle, setSearchTitle] = useState('');
  const [searchTags, setSearchTags] = useState([]);

  const fetchVideos = (title = searchTitle, tags = searchTags) => {
    const params = new URLSearchParams();
    if (title) {
      params.append('title_query', title);
    }
    if (tags.length > 0) {
      params.append('tags_query', tags.join(','));
    }
    fetch(`/api/videos/?${params.toString()}`)
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
    fetchVideos(); // Initial fetch without search parameters
    fetchTags();
  }, []);

  const handleAddVideo = async (videoData) => {
    try {
      const response = await fetch('/api/videos/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(videoData),
      });
      if (response.ok) {
        fetchVideos();
        fetchTags();
        setShowModal(false); // Close modal on successful add
      } else {
        console.error("Failed to add video");
      }
    } catch (error) {
      console.error("Error adding video:", error);
    }
  };

  const handleUpdateVideo = async (videoId, videoData) => {
    try {
      const response = await fetch(`/api/videos/${videoId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(videoData),
        }
      );
      if (response.ok) {
        setEditingVideoId(null);
        setCurrentEditData({ url: '', tags: [], memo: '' });
        fetchVideos();
        fetchTags();
      } else {
        console.error("Failed to update video");
      }
    } catch (error) {
      console.error("Error updating video:", error);
    }
  };

  const handleDeleteVideo = async (id) => {
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

  const handleEditVideo = (video) => {
    setEditingVideoId(video.id);
    setCurrentEditData({
      url: video.url,
      tags: video.tags ? video.tags.split(',').map(t => t.trim()) : [],
      memo: video.memo || ''
    });
  };

  const handleCancelEdit = () => {
    setEditingVideoId(null);
    setCurrentEditData({ url: '', tags: [], memo: '' });
  };

  const handleEditFormChange = (data) => {
    setCurrentEditData(data);
  };

  const handleSearch = () => {
    fetchVideos(searchTitle, searchTags);
  };

  return (
    <>
      <h1>YouTube Video List</h1>
      <button onClick={() => setShowModal(true)}>Add New Video</button>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button className="modal-close-button" onClick={() => setShowModal(false)}>X</button>
            <VideoForm onAddVideo={handleAddVideo} allTags={allTags} setAllTags={setAllTags} onCancel={() => setShowModal(false)} />
          </div>
        </div>
      )}

      <h2>Search Videos</h2>
      <div className="search-controls">
        <input
          type="text"
          placeholder="Search by title"
          value={searchTitle}
          onChange={(e) => setSearchTitle(e.target.value)}
        />
        <TagMultiSelect
          allTags={allTags}
          selectedTags={searchTags}
          onTagChange={setSearchTags}
        />
        <button onClick={handleSearch}>Search</button>
        <button onClick={() => {
          setSearchTitle('');
          setSearchTags([]);
          fetchVideos('', []);
        }}>Clear Search</button>
      </div>

      <h2>Videos from Database</h2>
      {videos.length === 0 ? (
        <p>No videos yet.</p>
      ) : (
        <VideoList
          videos={videos}
          allTags={allTags}
          setAllTags={setAllTags}
          onUpdateVideo={handleUpdateVideo}
          onDeleteVideo={handleDeleteVideo}
          onEditVideo={handleEditVideo}
          editingVideoId={editingVideoId}
          currentEditData={currentEditData}
          onCancelEdit={handleCancelEdit}
          onEditFormChange={handleEditFormChange}
        />
      )}
    </>
  );
}

export default App;