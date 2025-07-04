import React from 'react';
import VideoItem from './VideoItem';

const VideoList = ({ videos, allTags, setAllTags, onUpdateVideo, onDeleteVideo, onEditVideo, editingVideoId, currentEditData, onCancelEdit, onEditFormChange }) => {
  return (
    <ul className="video-list">
      {videos.map((video) => (
        <VideoItem
          key={video.id}
          video={video}
          allTags={allTags}
          setAllTags={setAllTags}
          onUpdateVideo={onUpdateVideo}
          onDeleteVideo={onDeleteVideo}
          onEditVideo={onEditVideo}
          isEditing={editingVideoId === video.id}
          currentEditData={currentEditData}
          onCancelEdit={onCancelEdit}
          onEditFormChange={onEditFormChange}
        />
      ))}
    </ul>
  );
};

export default VideoList;