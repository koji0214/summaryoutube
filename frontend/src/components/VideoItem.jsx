import React from 'react';

const VideoItem = ({ video, allTags, setAllTags, onUpdateVideo, onDeleteVideo, onEditVideo, isEditing, currentEditData, onCancelEdit, onEditFormChange }) => {
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

  const videoId = extractVideoId(video.url);

  const handleUpdateSubmit = (e) => {
    e.preventDefault();
    onUpdateVideo(video.id, { ...currentEditData, tags: currentEditData.tags.join(',') });
  };

  const handleEditTagSelect = (e) => {
    const selectedTag = e.target.value;
    if (selectedTag && !currentEditData.tags.includes(selectedTag)) {
      onEditFormChange({ ...currentEditData, tags: [...currentEditData.tags, selectedTag] });
    }
  };

  const handleEditAddNewTag = (e) => {
    const newTagValue = e.target.value;
    if (e.key === 'Enter' && newTagValue) {
      e.preventDefault();
      if (!currentEditData.tags.includes(newTagValue)) {
        onEditFormChange({ ...currentEditData, tags: [...currentEditData.tags, newTagValue] });
        if (!allTags.includes(newTagValue)) {
          setAllTags([...allTags, newTagValue]);
        }
      }
      e.target.value = '';
    }
  };

  const handleEditRemoveTag = (tagToRemove) => {
    onEditFormChange({ ...currentEditData, tags: currentEditData.tags.filter(tag => tag !== tagToRemove) });
  };

  return (
    <li className={`video-item ${isEditing ? 'editing' : ''}`}>
      <strong>Title:</strong> {video.title}<br />
      <strong>Channel:</strong> {video.channel_name}<br />

      {isEditing ? (
        <form onSubmit={handleUpdateSubmit}>
          <strong>URL: </strong>
          <input
            type="text"
            name="url"
            value={currentEditData.url}
            onChange={(e) => onEditFormChange({ ...currentEditData, url: e.target.value })}
            required
            style={{ width: '400px' }}
          /><br />
          <strong>Tags: </strong>
          <div className="tag-input-section" style={{ marginBottom: '1rem' }}>
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
            onChange={(e) => onEditFormChange({ ...currentEditData, memo: e.target.value })}
            placeholder="Enter a memo"
            style={{ width: '400px', height: '60px' }}
          /><br />
          <div className="actions">
            <button type="submit">Save</button>
            <button type="button" onClick={onCancelEdit}>Cancel</button>
          </div>
        </form>
      ) : (
        <>
          <a href={video.url} target="_blank" rel="noopener noreferrer">{video.url}</a><br />
          <strong>Tags:</strong> {video.tags || 'N/A'}<br />
          <strong>Memo:</strong> {video.memo || 'N/A'}<br />
          <div className="actions">
            <button onClick={() => onEditVideo(video)}>Edit</button>
            <button onClick={() => onDeleteVideo(video.id)}>Delete</button>
          </div>
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
};

export default VideoItem;