from newspaper import Article
from typing import Dict, List
import time

def scrape_article_content(url: str, timeout: int = 10) -> str:
    """
    Scrape full article content from URL
    
    Args:
        url: Article URL
        timeout: Max time to wait
    
    Returns:
        Full article text (or empty string if failed)
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text if article.text else ""
    except Exception as e:
        return ""

def enrich_with_content(articles: List[Dict], max_articles: int = None) -> List[Dict]:
    """
    Add scraped full content to articles (OPTIONAL)
    
    Args:
        articles: List of articles from NewsAPI
        max_articles: Limit how many to scrape (None = all)
    
    Returns:
        Articles with enriched 'full_text' field
    """
    if max_articles is None:
        max_articles = len(articles)
    
    to_scrape = min(len(articles), max_articles)
    print(f"🌐 Scraping full content from {to_scrape} articles...")
    print(f"⏱️  This may take {to_scrape} seconds (1 req/sec)...")
    
    scraped_count = 0
    failed_count = 0
    
    for i, article in enumerate(articles[:max_articles], 1):
        if i % 5 == 0:
            print(f"  Progress: {i}/{to_scrape}")
        
        # Scrape content
        scraped = scrape_article_content(article['url'])
        
        if scraped and len(scraped) > 200:
            # Success! Replace full_text with scraped content
            article['scraped_content'] = scraped
            article['full_text'] = f"{article['title']} {scraped}"
            scraped_count += 1
        else:
            # Failed - keep original
            failed_count += 1
        
        # Rate limiting: 1 request per second
        time.sleep(1)
    
    print(f"✅ Scraped {scraped_count} articles successfully")
    if failed_count > 0:
        print(f"⚠️  Failed to scrape {failed_count} articles (kept originals)")
    
    return articles
