import { useState, useEffect } from 'react';
import { api } from '../api/client';
import ArticleCard from '../components/ArticleCard';

function TagView({ tagId }) {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState(null);
  const [fetchResult, setFetchResult] = useState(null);

  useEffect(() => {
    if (tagId) {
      loadArticles();
    }
  }, [tagId]);

  const loadArticles = () => {
    setLoading(true);
    setError(null);
    api.getArticlesForTag(tagId)
      .then(response => {
        setArticles(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error loading articles:', error);
        setError('Failed to load articles. Please try again.');
        setLoading(false);
      });
  };

  const handleFetchNews = () => {
    setFetching(true);
    setError(null);
    setFetchResult(null);
    
    api.fetchNewsForTag(tagId)
      .then(response => {
        console.log('Fetch result:', response.data);
        setFetchResult(response.data);
        setFetching(false);
        setTimeout(() => loadArticles(), 1000);
      })
      .catch(error => {
        console.error('Error fetching news:', error);
        setError('Failed to fetch news. Please try again.');
        setFetching(false);
      });
  };

  if (loading) {
    return <div className="loading">Loading articles...</div>;
  }

  return (
    <div className="tag-view">
      <div className="tag-header">
        <h2>Latest Articles</h2>
        <button 
          onClick={handleFetchNews} 
          disabled={fetching}
          className="fetch-button"
        >
          {fetching ? '🔄 Fetching...' : '🔄 Refresh News'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {fetchResult && (
        <div className="fetch-result">
          <p>✅ Fetched {fetchResult.fetched} articles</p>
          <p>📰 {fetchResult.new_articles} new articles added</p>
          <p>🎯 {fetchResult.matched_articles} articles matched (threshold: {fetchResult.threshold})</p>
        </div>
      )}

      {articles.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📰</div>
          <h3>No articles yet</h3>
          <p>Click "Refresh News" to fetch articles for this tag!</p>
        </div>
      ) : (
        <>
          <div className="articles-count">
            Showing {articles.length} article{articles.length !== 1 ? 's' : ''}
          </div>
          <div className="articles-grid">
            {articles.map(article => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default TagView;
