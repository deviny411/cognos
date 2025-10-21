# news_fetcher.py
import requests
from datetime import datetime, timedelta
from config import Config
from typing import List, Dict

class NewsFetcher:
    def __init__(self):
        self.api_key = Config.NEWS_API_KEY
        self.base_url = Config.NEWS_API_BASE_URL
        
    def fetch_by_keyword(self, keyword: str, days_back: int = None) -> List[Dict]:
        """Fetch news articles by keyword"""
        if days_back is None:
            days_back = Config.DAYS_BACK
            
        url = f"{self.base_url}/everything"
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        params = {
            'q': keyword,
            'apiKey': self.api_key,
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': from_date,
            'pageSize': Config.MAX_ARTICLES_PER_TAG,
            'excludeDomains': 'biztoc.com'  # Skip BizToc
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'ok':
                print(f"✅ Fetched {len(data['articles'])} articles for '{keyword}'")
                return self._process_articles(data['articles'])
            else:
                print(f"❌ NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching news: {e}")
            return []
    
    def _process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process and clean article data"""
        processed = []
        
        for article in articles:
            if not article.get('title') or not article.get('url'):
                continue
            
            published_at = None
            if article.get('publishedAt'):
                try:
                    published_at = datetime.strptime(
                        article['publishedAt'], 
                        '%Y-%m-%dT%H:%M:%SZ'
                    )
                except:
                    pass
            
            processed.append({
                'title': article['title'],
                'description': article.get('description', ''),
                'content': article.get('content', ''),
                'url': article['url'],
                'source': article.get('source', {}).get('name', 'Unknown'),
                'author': article.get('author', ''),
                'image_url': article.get('urlToImage', ''),
                'published_at': published_at
            })
        
        return processed
    
    def test_connection(self) -> bool:
        """Test if NewsAPI key is working"""
        try:
            url = f"{self.base_url}/top-headlines"
            params = {'apiKey': self.api_key, 'country': 'us', 'pageSize': 1}
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data['status'] == 'ok':
                print("✅ NewsAPI connection successful!")
                return True
            else:
                print(f"❌ NewsAPI error: {data.get('message')}")
                return False
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
