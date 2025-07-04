import { useState, useEffect } from 'react';
import './App.css';
import VideoForm from './components/VideoForm';
import VideoList from './components/VideoList';

function App() {
  const [videos, setVideos] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [editingVideoId, setEditingVideoId] = useState(null);
  const [currentEditData, setCurrentEditData] = useState({ url: '', tags: [], memo: '' });

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

  return (
    <>
      <h1>YouTube Video List</h1>
      <VideoForm onAddVideo={handleAddVideo} allTags={allTags} setAllTags={setAllTags} />
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