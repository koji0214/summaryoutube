import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

const VideoDetail = () => {
  const { id } = useParams();
  const [video, setVideo] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVideo = async () => {
      try {
        const response = await fetch(`/api/videos/${id}`);
        if (!response.ok) {
          throw new Error('Video not found');
        }
        const data = await response.json();
        setVideo(data);
      } catch (err) {
        setError(err.message);
      }
    };

    const fetchTranscript = async () => {
      try {
        const response = await fetch(`/api/videos/${id}/transcript`);
        if (!response.ok) {
          throw new Error('Transcript not found');
        }
        const data = await response.json();
        setTranscript(data.transcript);
      } catch (err) {
        // Transcript might not exist, so we don't treat it as a critical error
        console.error("Error fetching transcript:", err);
        setTranscript('No transcript available.');
      }
    };

    const fetchAll = async () => {
      setLoading(true);
      await Promise.all([fetchVideo(), fetchTranscript()]);
      setLoading(false);
    }

    fetchAll();
  }, [id]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!video) {
    return <div>Video not found.</div>;
  }

  return (
    <div>
      <Link to="/">Back to Video List</Link>
      <h1>{video.title}</h1>
      <p><strong>Channel:</strong> {video.channel_name}</p>
      <p><strong>URL:</strong> <a href={video.url} target="_blank" rel="noopener noreferrer">{video.url}</a></p>
      <p><strong>Memo:</strong> {video.memo}</p>
      <p><strong>Tags:</strong> {video.tags}</p>
      
      <h2>Transcript</h2>
      <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
        {transcript}
      </pre>
    </div>
  );
};

export default VideoDetail;