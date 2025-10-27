from newsapi import NewsApiClient
from datetime import datetime, timedelta
from typing import List, Dict
import hashlib

class ArticleFetcher:
    """Fetches and preprocesses articles from News API"""
    
    def __init__(self, api_key: str):
        self.newsapi = NewsApiClient(api_key=api_key)
    
    def fetch_articles(
        self, 
        query: str, 
        count: int = 100,
        days_back: int = 29
    ) -> List[Dict]:
        """
        Fetch articles from News API
        
        Args:
            query: Search query (topic name)
            count: Number of articles to fetch
            days_back: How far back to search
        
        Returns:
            List of article dictionaries
        """
        print(f"🔍 Fetching {count} articles for '{query}'...")
        
        try:
            # Calculate date range - use YYYY-MM-DD format
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Fetch from News API
            response = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='relevancy',
                from_param=from_date,
                page_size=min(count, 100)
            )
            
            articles = response.get('articles', [])
            print(f"✅ Fetched {len(articles)} articles")
            
            return articles
            
        except Exception as e:
            print(f"❌ Error fetching articles: {e}")
            return []
    
    def preprocess_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Clean and preprocess raw articles
        
        Removes duplicates, filters low-quality, standardizes format
        """
        print(f"🧹 Preprocessing {len(articles)} articles...")
        
        processed = []
        seen_urls = set()
        seen_content_hashes = set()
        
        for article in articles:
            # Skip if missing critical fields
            if not article.get('title') or not article.get('url'):
                continue
            
            # Skip if no description
            if not article.get('description') or len(article.get('description', '')) < 50:
                continue
            
            # Skip duplicates by URL
            url = article['url']
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Skip duplicates by content
            content = f"{article['title']} {article.get('description', '')}"
            content_hash = self._hash_content(content)
            if content_hash in seen_content_hashes:
                continue
            seen_content_hashes.add(content_hash)
            
            # Create cleaned article
            cleaned = {
                'title': article['title'].strip(),
                'description': article.get('description', '').strip(),
                'url': url,
                'source': article.get('source', {}).get('name', 'Unknown'),
                'published_at': article.get('publishedAt'),
                'author': article.get('author'),
                'url_to_image': article.get('urlToImage'),
                'full_text': f"{article['title']} {article.get('description', '')}"
            }
            
            processed.append(cleaned)
        
        print(f"✅ Kept {len(processed)} unique, quality articles")
        return processed
    
    def _hash_content(self, text: str) -> str:
        """Generate hash for duplicate detection"""
        normalized = text.lower().strip()
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def filter_by_quality(
        self, 
        articles: List[Dict],
        min_title_length: int = 20,
        min_description_length: int = 80
    ) -> List[Dict]:
        """
        Filter articles by basic quality criteria
        
        Args:
            articles: List of preprocessed articles
            min_title_length: Minimum title length
            min_description_length: Minimum description length
        
        Returns:
            Filtered list of articles
        """
        print(f"🎯 Applying quality filters...")
        
        filtered = []
        
        for article in articles:
            # Must have decent title
            if len(article['title']) < min_title_length:
                continue
            
            # Must have decent description
            if len(article.get('description', '')) < min_description_length:
                continue
            
            # Must not be spam
            if self._is_spam(article):
                continue
            
            # Must have a real source
            if article.get('source', '').lower() in ['removed', 'unknown', '']:
                continue
            
            filtered.append(article)
        
        print(f"✅ {len(filtered)} articles passed quality filter ({len(articles) - len(filtered)} filtered out)")
        return filtered
    
    def _is_spam(self, article: Dict) -> bool:
        """Detect spam/low-quality content"""
        text = article['full_text'].lower()
        
        spam_patterns = [
            'click here', 'buy now', 'limited time', 'act now',
            'subscribe now', 'sign up today', 'special offer',
            'free download', 'earn money'
        ]
        
        spam_count = sum(1 for pattern in spam_patterns if pattern in text)
        
        return spam_count >= 2


def fetch_and_preprocess(
    query: str,
    api_key: str,
    count: int = 100,
    quality_filter: bool = True
) -> List[Dict]:
    """
    Convenience function to fetch and preprocess articles
    
    Usage:
        articles = fetch_and_preprocess("Artificial Intelligence", NEWS_API_KEY)
    """
    fetcher = ArticleFetcher(api_key)
    
    # Fetch raw articles
    raw_articles = fetcher.fetch_articles(query, count=count)
    
    if not raw_articles:
        return []
    
    # Preprocess
    processed = fetcher.preprocess_articles(raw_articles)
    
    # Apply quality filter
    if quality_filter:
        processed = fetcher.filter_by_quality(processed)
    
    return processed
