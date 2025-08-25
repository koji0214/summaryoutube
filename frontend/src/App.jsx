import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import VideoForm from './components/VideoForm';
import VideoList from './components/VideoList';
import TagMultiSelect from './components/TagMultiSelect';
import VideoDetail from './components/VideoDetail';

const MainPage = () => {
  const [videos, setVideos] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [editingVideoId, setEditingVideoId] = useState(null);
  const [currentEditData, setCurrentEditData] = useState({ url: '', tags: [], memo: '' });
  const [showModal, setShowModal] = useState(false);
  const [searchTitle, setSearchTitle] = useState('');
  const [searchTags, setSearchTags] = useState([]);
  const [sortBy, setSortBy] = useState('id');
  const [sortOrder, setSortOrder] = useState('asc');

  const fetchVideos = (title = searchTitle, tags = searchTags, sort_by = sortBy, sort_order = sortOrder) => {
    const params = new URLSearchParams();
    if (title) {
      params.append('title_query', title);
    }
    if (tags.length > 0) {
      params.append('tags_query', tags.join(','));
    }
    params.append('sort_by', sort_by);
    params.append('sort_order', sort_order);
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
    fetchVideos();
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
        setShowModal(false);
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
    fetchVideos(searchTitle, searchTags, sortBy, sortOrder);
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
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="id">Sort by ID</option>
          <option value="title">Sort by Title</option>
          <option value="channel_name">Sort by Channel</option>
          <option value="created_at">Sort by Created Date</option>
          <option value="updated_at">Sort by Updated Date</option>
        </select>
        <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>
        <button onClick={handleSearch}>Search</button>
        <button onClick={() => {
          setSearchTitle('');
          setSearchTags([]);
          setSortBy('id');
          setSortOrder('asc');
          fetchVideos('', [], 'id', 'asc');
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


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/video/:id" element={<VideoDetail />} />
      </Routes>
    </Router>
  );
}

export default App;