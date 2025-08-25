import React, { useState } from 'react';

const VideoForm = ({ onAddVideo, allTags, setAllTags, onCancel }) => {
  const [url, setUrl] = useState('');
  const [tags, setTags] = useState([]);
  const [memo, setMemo] = useState('');
  const [newTag, setNewTag] = useState('');
  const [isHovering, setIsHovering] = useState(false);
  const [transcriptionOption, setTranscriptionOption] = useState('standard');

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    setIsHovering(true);
    setTimeout(() => setIsHovering(false), 500); // Remove hover effect after 0.5 seconds
    await onAddVideo({ url, tags: tags.join(','), memo, transcriptionOption });
    setUrl('');
    setTags([]);
    setMemo('');
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

  return (
    <form onSubmit={handleAddSubmit} className={`video-form ${isHovering ? 'hover-effect' : ''}`}>
      <h2>Add New Video</h2>
      <div>
        <label>YouTube URL:</label>
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
        <label>Tags:</label>
        <div className="tag-container">
          {tags.map(tag => (
            <span key={tag} className="tag-item">
              {tag}
              <button type="button" onClick={() => handleRemoveTag(tag)} className="tag-remove-button">x</button>
            </span>
          ))}
        </div>
        <div className="tag-input-controls" style={{ marginTop: '5px' }}>
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
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.nativeEvent.isComposing) {
                e.preventDefault();
                handleAddNewTag();
                setNewTag(''); // Always clear the input after Enter is pressed
              }
            }}
            placeholder="Or add a new tag"
            style={{ marginLeft: '10px' }}
          />
        </div>
      </div>
      <div>
        <label>Transcription Option:</label>
        <div className="transcription-options">
          <label>
            <input
              type="radio"
              value="standard"
              checked={transcriptionOption === 'standard'}
              onChange={(e) => setTranscriptionOption(e.target.value)}
            />
            Standard (Free)
          </label>
          <label style={{ marginLeft: '10px' }}>
            <input
              type="radio"
              value="high_quality"
              checked={transcriptionOption === 'high_quality'}
              onChange={(e) => setTranscriptionOption(e.target.value)}
            />
            High-Quality (Paid)
          </label>
        </div>
      </div>
      <div>
        <label>Memo:</label>
        <textarea
          value={memo}
          onChange={(e) => setMemo(e.target.value)}
          placeholder="Enter a memo"
          style={{ width: '400px', height: '80px' }}
        />
      </div>
      <div className="form-actions">
        <button type="submit">Add Video</button>
        {onCancel && <button type="button" onClick={onCancel} style={{ marginLeft: '10px' }}>Cancel</button>}
      </div>
    </form>
  );
};

export default VideoForm;