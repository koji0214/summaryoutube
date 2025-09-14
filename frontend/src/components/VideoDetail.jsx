import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';

const StatusBadge = ({ status }) => {
  if (!status || status === 'completed') return null;

  const badgeStyle = {
    marginLeft: '10px',
    padding: '2px 8px',
    borderRadius: '12px',
    color: 'white',
    fontWeight: 'bold',
    fontSize: '0.8em',
  };

  let style = {};
  let text = '';

  switch (status) {
    case 'processing':
      style = { ...badgeStyle, backgroundColor: '#f0ad4e' };
      text = 'Processing...';
      break;
    case 'failed':
      style = { ...badgeStyle, backgroundColor: '#d9534f' };
      text = 'Failed';
      break;
    default:
      return null;
  }

  return <span style={style}>{text}</span>;
};

const VideoDetail = () => {
  const { id } = useParams();
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Ref to hold the interval ID
  const pollingInterval = useRef(null);

  const fetchVideo = async () => {
    try {
      const response = await fetch(`/api/videos/${id}`);
      if (!response.ok) {
        throw new Error('Video not found');
      }
      const data = await response.json();
      setVideo(data);

      // If the process is finished, stop polling
      if (data.status === 'completed' || data.status === 'failed') {
        if (pollingInterval.current) {
          clearInterval(pollingInterval.current);
          pollingInterval.current = null;
        }
      }
      return data; // Return data for initial setup
    } catch (err) {
      setError(err.message);
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
        pollingInterval.current = null;
      }
      return null;
    }
  };

  useEffect(() => {
    const startPolling = (videoData) => {
      if (videoData && videoData.status === 'processing' && !pollingInterval.current) {
        pollingInterval.current = setInterval(() => {
          console.log('Polling for video status...');
          fetchVideo();
        }, 5000); // Poll every 5 seconds
      }
    };

    const initialFetch = async () => {
      setLoading(true);
      const videoData = await fetchVideo();
      setLoading(false);
      startPolling(videoData);
    };

    initialFetch();

    // Cleanup function to clear interval when component unmounts or id changes
    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
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

  const getTranscriptText = () => {
    if (video.status === 'processing') {
      return 'Transcript is being generated...';
    }
    if (video.status === 'failed') {
      return 'Transcript generation failed.';
    }
    return video.transcript || 'No transcript available.';
  }

  return (
    <div>
      <Link to="/">Back to Video List</Link>
      <h1>{video.title} <StatusBadge status={video.status} /></h1>
      <p><strong>Channel:</strong> {video.channel_name}</p>
      <p><strong>URL:</strong> <a href={video.url} target="_blank" rel="noopener noreferrer">{video.url}</a></p>
      <p><strong>Memo:</strong> {video.memo}</p>
      <p><strong>Tags:</strong> {video.tags}</p>
      
      <h2>Transcript</h2>
      <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
        {getTranscriptText()}
      </pre>
    </div>
  );
};

export default VideoDetail;
