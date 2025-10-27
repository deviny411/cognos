from data_fetcher import fetch_and_preprocess
from article_analyzer import ArticleAnalyzer
from content_scraper import enrich_with_content  # OPTIONAL
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

NEWS_API_KEY = os.getenv('NEWS_API_KEY')

def test_analyzer(use_scraping=False):
    """
    Test the article analyzer
    
    Args:
        use_scraping: If True, scrape full article content (slow!)
    """
    
    if not NEWS_API_KEY:
        print("❌ ERROR: NEWS_API_KEY not found!")
        return
    
    print("="*60)
    print("Testing Article Analyzer (AI Features)")
    print("="*60)
    
    # Step 1: Fetch articles
    print("\n📰 Step 1: Fetching articles...")
    articles = fetch_and_preprocess(
        query="Artificial Intelligence",
        api_key=NEWS_API_KEY,
        count=10
    )
    
    if not articles:
        print("❌ No articles fetched!")
        return
    
    print(f"✅ Got {len(articles)} articles")
    
    # Step 1.5: OPTIONAL - Scrape full content
    if use_scraping:
        print("\n🌐 Step 1.5: Enriching with full content (SLOW)...")
        articles = enrich_with_content(articles, max_articles=5)
    
    # Step 2: Analyze with AI
    print("\n🤖 Step 2: Analyzing with AI...")
    analyzer = ArticleAnalyzer()
    analyzed = analyzer.analyze_batch(articles)
    
    # Step 3: Show results
    print("\n" + "="*60)
    print("📊 ANALYSIS RESULTS")
    print("="*60)
    
    sample = analyzed[0]
    print(f"\n📰 Article: {sample['title']}")
    print(f"Source: {sample['source']}")
    print(f"URL: {sample['url']}")
    
    print(f"\n📝 Text Analysis:")
    print(f"  Description length: {len(sample['description'])} chars")
    print(f"  Full text length: {len(sample['full_text'])} chars")
    if 'scraped_content' in sample:
        print(f"  ✅ Scraped content: {len(sample['scraped_content'])} chars")
    
    print(f"\n  Description:")
    print(f"  {sample['description']}")
    
    print(f"\n🔢 Embedding:")
    print(f"  Shape: {sample['embedding'].shape}")
    print(f"  Values: [" + ", ".join(f"{v:.4f}" for v in sample['embedding'][:5]) + "]")
    
    print(f"\n🏷️ Entities Found: {len(sample['entities'])}")
    if sample['entities']:
        for ent in sample['entities'][:10]:
            print(f"  - {ent['text']} ({ent['label']})")
    
    print(f"\n🔑 Keywords Found: {len(sample['keywords'])}")
    if sample['keywords']:
        for kw in sample['keywords'][:15]:
            print(f"  - {kw}")
    
    # Summary stats
    print("\n" + "="*60)
    print("📈 SUMMARY STATISTICS")
    print("="*60)
    
    avg_text = sum(len(a['full_text']) for a in analyzed) / len(analyzed)
    print(f"\nText lengths across {len(analyzed)} articles:")
    print(f"  Average: {avg_text:.0f} chars")
    
    avg_entities = sum(len(a['entities']) for a in analyzed) / len(analyzed)
    avg_keywords = sum(len(a['keywords']) for a in analyzed) / len(analyzed)
    
    print(f"\nAI Features:")
    print(f"  Average entities: {avg_entities:.1f}")
    print(f"  Average keywords: {avg_keywords:.1f}")
    
    # Similarity test
    if len(analyzed) >= 2:
        print("\n" + "="*60)
        print("🔄 SIMILARITY TEST")
        print("="*60)
        
        art1 = analyzed[0]
        art2 = analyzed[1]
        
        similarity = analyzer.calculate_similarity(art1, art2)
        
        print(f"\nArticle 1: {art1['title'][:50]}...")
        print(f"Article 2: {art2['title'][:50]}...")
        print(f"\nSimilarity: {similarity:.3f} ({similarity*100:.1f}%)")

if __name__ == "__main__":
    # Normal mode (fast)
    test_analyzer(use_scraping=True)
    
    # Uncomment to test with scraping (slow!)
    # test_analyzer(use_scraping=True)
