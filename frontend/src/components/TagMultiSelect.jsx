import React, { useState, useRef, useEffect } from 'react';

const TagMultiSelect = ({ allTags, selectedTags, onTagChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const handleTagToggle = (tag) => {
    const newSelectedTags = selectedTags.includes(tag)
      ? selectedTags.filter((t) => t !== tag)
      : [...selectedTags, tag];
    onTagChange(newSelectedTags);
  };

  const handleRemoveTag = (tagToRemove) => {
    const newSelectedTags = selectedTags.filter((tag) => tag !== tagToRemove);
    onTagChange(newSelectedTags);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="tag-multi-select" ref={dropdownRef}>
      <div className="selected-tags-display" onClick={() => setIsOpen(!isOpen)}>
        {selectedTags.length > 0 ? (
          selectedTags.map((tag) => (
            <span key={tag} className="selected-tag-pill">
              {tag}
              <button type="button" onClick={(e) => { e.stopPropagation(); handleRemoveTag(tag); }}>x</button>
            </span>
          ))
        ) : (
          <span>Select Tags...</span>
        )}
      </div>

      {isOpen && (
        <div className="tag-dropdown">
          {allTags.length > 0 ? (
            allTags.map((tag) => (
              <label key={tag} className="tag-dropdown-item" onClick={() => handleTagToggle(tag)}>
                <span className="tag-checkbox-indicator">
                {selectedTags.includes(tag) && '✓'}
              </span>
              {tag}
              </label>
            ))
          ) : (
            <div className="tag-dropdown-item">No tags available</div>
          )}
        </div>
      )}
    </div>
  );
};

export default TagMultiSelect;
