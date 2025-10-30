from data_fetcher import fetch_and_preprocess
from article_analyzer import ArticleAnalyzer
from content_scraper import enrich_with_content
from article_clusterer import ArticleClusterer
import os
from pathlib import Path
from dotenv import load_dotenv
from collections import Counter

# Load .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

NEWS_API_KEY = os.getenv('NEWS_API_KEY')

def test_clustering(topic: str = "Artificial Intelligence", use_scraping: bool = False):
    """Test article clustering"""
    
    if not NEWS_API_KEY:
        print("❌ ERROR: NEWS_API_KEY not found!")
        return
    
    print("="*60)
    print(f"🚀 ARTICLE CLUSTERING TEST: '{topic}'")
    print("="*60)
    
    # Step 1: Fetch articles
    print("\n📰 Step 1: Fetching articles...")
    articles = fetch_and_preprocess(
        query=topic,
        api_key=NEWS_API_KEY,
        count=30  # Get more for better clustering
    )
    
    if not articles:
        print("❌ No articles fetched!")
        return
    
    print(f"✅ Got {len(articles)} articles")
    
    # Step 2: Optional scraping
    if use_scraping:
        print("\n🌐 Step 2: Enriching with full content...")
        articles = enrich_with_content(articles, max_articles=15)
    
    # Step 3: AI Analysis
    print("\n🤖 Step 3: Analyzing articles with AI...")
    analyzer = ArticleAnalyzer()
    analyzed = analyzer.analyze_batch(articles)
    
    # Step 4: Clustering
    print("\n🔄 Step 4: Clustering articles...")
    clusterer = ArticleClusterer(
        similarity_threshold=0.4,  # Articles need 40% similarity
        min_cluster_size=3
    )
    clusters = clusterer.cluster_articles(analyzed)
    
    # Display results
    print("\n" + "="*60)
    print("📊 CLUSTERING RESULTS")
    print("="*60)
    
    print(f"\nGrouped {len(analyzed)} articles into {len(clusters)} clusters\n")
    
    for i, cluster in enumerate(clusters, 1):
        print(f"{'='*60}")
        print(f"CLUSTER {i} ({cluster['size']} articles)")
        print(f"{'='*60}")
        
        # Calculate coherence
        coherence = clusterer.calculate_cluster_coherence(cluster)
        print(f"Coherence: {coherence:.3f} (higher = more similar articles)")
        
        # Show common entities
        all_entities = []
        for article in cluster['articles']:
            all_entities.extend([e['text'] for e in article.get('entities', [])])
        
        if all_entities:
            entity_counts = Counter(all_entities)
            print(f"\nCommon entities:")
            for entity, count in entity_counts.most_common(5):
                print(f"  - {entity} ({count} mentions)")
        
        # Show common keywords
        all_keywords = []
        for article in cluster['articles']:
            all_keywords.extend(article.get('keywords', []))
        
        if all_keywords:
            keyword_counts = Counter(all_keywords)
            print(f"\nCommon keywords:")
            for keyword, count in keyword_counts.most_common(5):
                print(f"  - {keyword} ({count} mentions)")
        
        # Show articles
        print(f"\nArticles in this cluster:")
        for j, article in enumerate(cluster['articles'], 1):
            print(f"  {j}. {article['title'][:70]}...")
            print(f"     Source: {article['source']}")
        
        print()
    
    # Summary stats
    print("="*60)
    print("📈 SUMMARY STATISTICS")
    print("="*60)
    
    avg_coherence = sum(clusterer.calculate_cluster_coherence(c) for c in clusters) / len(clusters)
    print(f"\nAverage cluster coherence: {avg_coherence:.3f}")
    print(f"Total clusters: {len(clusters)}")
    print(f"Articles clustered: {sum(c['size'] for c in clusters)}")
    print(f"Unclustered articles: {len(analyzed) - sum(c['size'] for c in clusters)}")
    
    return clusters

if __name__ == "__main__":
    # Test clustering
    test_clustering("Artificial Intelligence", use_scraping=False)
    
    # Uncomment to test other topics:
    # test_clustering("Climate Change", use_scraping=False)
    # test_clustering("Space Exploration", use_scraping=False)
