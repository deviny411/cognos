import { useState, useEffect } from 'react';
import { api } from './api/client';
import TagList from './components/TagList';
import TagView from './pages/TagView';
import './App.css';

function App() {
  const [userId, setUserId] = useState(null);
  const [tags, setTags] = useState([]);
  const [selectedTagId, setSelectedTagId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = () => {
  console.log('🔍 Loading users...');
  
  api.getUsers()
    .then(response => {
      console.log('✅ Users response:', response.data);
      console.log('📊 Number of users:', response.data.length);
      
      if (response.data.length > 0) {
        const firstUser = response.data[0];
        console.log('👤 Using user:', firstUser);
        setUserId(firstUser.id);
        loadTags();
      } else {
        console.error('❌ No users found in response');
        setLoading(false);
      }
    })
    .catch(error => {
      console.error('❌ Error loading users:', error);
      console.error('❌ Error details:', error.response?.data);
      setLoading(false);
    });
};


  const loadTags = () => {
    api.getTags()
      .then(response => {
        setTags(response.data);
        if (response.data.length > 0 && !selectedTagId) {
          setSelectedTagId(response.data[0].id);
        }
        setLoading(false);
      })
      .catch(error => {
        console.error('Error loading tags:', error);
        setLoading(false);
      });
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">Loading Cognos...</div>
      </div>
    );
  }

  if (!userId) {
    return (
      <div className="app">
        <header className="header">
          <div className="header-content">
            <h1>🧠 Cognos</h1>
            <p>Your Semantic News Intelligence Platform</p>
          </div>
        </header>
        
        <div className="empty-state" style={{ marginTop: '4rem' }}>
          <div className="empty-icon">👤</div>
          <h3>No users found</h3>
          <p>Create a user in the API first to get started</p>
          <a 
            href="http://localhost:8000/docs" 
            target="_blank" 
            rel="noopener noreferrer"
            className="api-link"
          >
            Open API Docs →
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>🧠 Cognos</h1>
          <p>Your Semantic News Intelligence Platform</p>
        </div>
      </header>
      
      <div className="layout">
        <aside className="sidebar">
          <TagList 
            tags={tags}
            selectedTagId={selectedTagId}
            onTagSelect={setSelectedTagId}
            userId={userId}
            onRefresh={loadTags}
          />
        </aside>

        <main className="main-content">
          {selectedTagId ? (
            <TagView tagId={selectedTagId} />
          ) : (
            <div className="empty-state">
              <div className="empty-icon">🏷️</div>
              <h3>No tags found</h3>
              <p>Create your first tag using the button in the sidebar!</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
