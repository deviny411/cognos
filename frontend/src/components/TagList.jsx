import CreateTagForm from './CreateTagForm';

function TagList({ tags, selectedTagId, onTagSelect, userId, onRefresh }) {
  return (
    <div className="tag-list">
      <h3>Your Tags</h3>
      
      {userId && <CreateTagForm userId={userId} onTagCreated={onRefresh} />}
      
      {tags.length === 0 ? (
        <p className="empty-message">No tags yet. Create one above!</p>
      ) : (
        <div className="tags">
          {tags.map(tag => (
            <button
              key={tag.id}
              className={`tag-button ${selectedTagId === tag.id ? 'active' : ''}`}
              onClick={() => onTagSelect(tag.id)}
            >
              <span className="tag-name">{tag.tag_name}</span>
              {tag.category && (
                <span className="tag-category">{tag.category}</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default TagList;
