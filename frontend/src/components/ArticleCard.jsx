function ArticleCard({ article }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  return (
    <div className="article-card">
      <div className="article-header">
        <h3>{article.title}</h3>
        {article.relevance_score && (
          <span className="relevance-badge">
            {Math.round(article.relevance_score * 100)}%
          </span>
        )}
      </div>
      
      <p className="article-meta">
        <span className="source">{article.source}</span>
        {article.published_at && (
          <>
            <span className="separator">•</span>
            <span>{formatDate(article.published_at)}</span>
          </>
        )}
      </p>
      
      {article.description && (
        <p className="article-description">{article.description}</p>
      )}
      
      <a 
        href={article.url} 
        target="_blank" 
        rel="noopener noreferrer"
        className="read-more"
      >
        Read Full Article →
      </a>
    </div>
  );
}

export default ArticleCard;
