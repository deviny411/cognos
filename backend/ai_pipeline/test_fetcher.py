from data_fetcher import fetch_and_preprocess
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get your News API key from environment
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

def test_fetch():
    """Test the data fetcher"""
    
    if not NEWS_API_KEY:
        print("❌ ERROR: NEWS_API_KEY not found in .env file!")
        print("Make sure you have a .env file with NEWS_API_KEY=your_key")
        return
    
    print("="*60)
    print("Testing Article Fetcher")
    print("="*60)
    print(f"Using API key: {NEWS_API_KEY[:10]}...{NEWS_API_KEY[-4:]}")
    
    # Test with a topic
    articles = fetch_and_preprocess(
        query="Artificial Intelligence",
        api_key=NEWS_API_KEY,
        count=50
    )
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTS")
    print(f"{'='*60}")
    print(f"Total articles fetched and processed: {len(articles)}")
    
    if articles:
        print(f"\n{'='*60}")
        print(f"📰 SAMPLE ARTICLE")
        print(f"{'='*60}")
        sample = articles[0]
        print(f"\nTitle: {sample['title']}")
        print(f"Source: {sample['source']}")
        print(f"Published: {sample['published_at']}")
        print(f"\nDescription: {sample['description'][:200]}...")
        print(f"\nURL: {sample['url']}")
        
        print(f"\n{'='*60}")
        print(f"📋 ALL ARTICLE TITLES")
        print(f"{'='*60}")
        for i, article in enumerate(articles[:10], 1):
            print(f"{i}. {article['title']} ({article['source']})")
        
        if len(articles) > 10:
            print(f"... and {len(articles) - 10} more")
    else:
        print("\n❌ No articles fetched. Check your API key!")

if __name__ == "__main__":
    test_fetch()
