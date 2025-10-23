import { useState } from 'react';
import { api } from '../api/client';
import CreateTagForm from './CreateTagForm';

function TagList({ tags, selectedTagId, onTagSelect, userId, onRefresh }) {
  const [deletingTagId, setDeletingTagId] = useState(null);

  const handleDelete = async (tagId, tagName) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${tagName}"?\n\nThis will remove the tag and all its article associations.`
    );
    
    if (!confirmed) return;

    setDeletingTagId(tagId);
    
    try {
      await api.deleteTag(tagId);
      console.log('✅ Tag deleted:', tagId);
      
      // If we deleted the selected tag, clear selection
      if (selectedTagId === tagId) {
        onTagSelect(null);
      }
      
      // Refresh tag list
      onRefresh();
    } catch (error) {
      console.error('❌ Error deleting tag:', error);
      alert('Failed to delete tag. Please try again.');
    } finally {
      setDeletingTagId(null);
    }
  };

  return (
    <div className="tag-list">
      <h3>Your Tags</h3>
      
      {userId && <CreateTagForm userId={userId} onTagCreated={onRefresh} />}
      
      {tags.length === 0 ? (
        <p className="empty-message">No tags yet. Create one above!</p>
      ) : (
        <div className="tags">
          {tags.map(tag => (
            <div key={tag.id} className="tag-item">
              <button
                className={`tag-button ${selectedTagId === tag.id ? 'active' : ''}`}
                onClick={() => onTagSelect(tag.id)}
              >
                <span className="tag-name">{tag.tag_name}</span>
                {tag.category && (
                  <span className="tag-category">{tag.category}</span>
                )}
              </button>
              <button
                className="delete-tag-button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(tag.id, tag.tag_name);
                }}
                disabled={deletingTagId === tag.id}
                title="Delete tag"
              >
                {deletingTagId === tag.id ? '...' : 'x'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TagList;
