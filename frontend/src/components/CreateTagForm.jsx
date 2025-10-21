import { useState } from 'react';
import { api } from '../api/client';

function CreateTagForm({ userId, onTagCreated }) {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    tag_name: '',
    keywords: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Convert comma-separated keywords to array
    const keywordsArray = formData.keywords
      .split(',')
      .map(k => k.trim())
      .filter(k => k.length > 0);

    const tagData = {
      tag_name: formData.tag_name,
      keywords: keywordsArray
    };

    console.log('📤 Creating tag:', tagData);

    api.createTag(userId, tagData)
      .then(response => {
        console.log('✅ Tag created:', response.data);
        setFormData({ tag_name: '', keywords: '' });
        setIsOpen(false);
        setLoading(false);
        if (onTagCreated) onTagCreated();
      })
      .catch(error => {
        console.error('❌ Error creating tag:', error);
        setError(error.response?.data?.detail || 'Failed to create tag');
        setLoading(false);
      });
  };

  if (!isOpen) {
    return (
      <button onClick={() => setIsOpen(true)} className="create-tag-button">
        + New Tag
      </button>
    );
  }

  return (
    <div className="create-tag-form">
      <h4>Create New Tag</h4>
      {error && <div className="form-error">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Tag Name *</label>
          <input
            type="text"
            value={formData.tag_name}
            onChange={(e) => setFormData({ ...formData, tag_name: e.target.value })}
            placeholder="e.g., artificial intelligence"
            required
          />
        </div>

        <div className="form-group">
          <label>Keywords (comma-separated)</label>
          <input
            type="text"
            value={formData.keywords}
            onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
            placeholder="e.g., AI, machine learning, neural networks"
          />
          <small style={{ color: '#666', fontSize: '0.85rem' }}>
            These help find relevant articles
          </small>
        </div>

        <div className="form-buttons">
          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'Creating...' : 'Create Tag'}
          </button>
          <button 
            type="button" 
            onClick={() => {
              setIsOpen(false);
              setError(null);
            }} 
            className="cancel-button"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default CreateTagForm;
