import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
from typing import List, Dict

class ArticleClusterer:
    """Clusters articles by semantic similarity"""
    
    def __init__(
        self,
        similarity_threshold: float = 0.5,
        min_cluster_size: int = 3,
        max_cluster_size: int = 25
    ):
        """
        Initialize clusterer
        
        Args:
            similarity_threshold: Min similarity for same cluster (0-1)
            min_cluster_size: Minimum articles per cluster
            max_cluster_size: Maximum articles per cluster
        """
        self.similarity_threshold = similarity_threshold
        self.min_cluster_size = min_cluster_size
        self.max_cluster_size = max_cluster_size
    
    def cluster_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Cluster articles by semantic similarity
        
        Args:
            articles: List of analyzed articles with embeddings
        
        Returns:
            List of clusters, each containing articles and metadata
        """
        if len(articles) < self.min_cluster_size:
            print(f"⚠️ Not enough articles to cluster (need {self.min_cluster_size}, got {len(articles)})")
            return [{
                'articles': articles,
                'cluster_id': 0,
                'size': len(articles)
            }]
        
        print(f"🔄 Clustering {len(articles)} articles...")
        
        # Extract embeddings
        embeddings = np.array([article['embedding'] for article in articles])
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(embeddings)
        
        # Convert to distance matrix (1 - similarity)
        distance_matrix = 1 - similarity_matrix
        
        # Use hierarchical clustering
        distance_threshold = 1 - self.similarity_threshold
        
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=distance_threshold,
            metric='precomputed',
            linkage='average'
        )
        
        labels = clustering.fit_predict(distance_matrix)
        
        # Group articles by cluster
        clusters = self._group_by_cluster(articles, labels)
        
        # Filter and validate clusters
        clusters = self._filter_clusters(clusters)
        
        print(f"✅ Created {len(clusters)} clusters")
        
        return clusters
    
    def _group_by_cluster(self, articles: List[Dict], labels: np.ndarray) -> List[Dict]:
        """Group articles by cluster label"""
        cluster_dict = {}
        
        for article, label in zip(articles, labels):
            if label not in cluster_dict:
                cluster_dict[label] = []
            cluster_dict[label].append(article)
        
        # Convert to list of cluster objects
        clusters = []
        for cluster_id, cluster_articles in cluster_dict.items():
            clusters.append({
                'cluster_id': int(cluster_id),
                'articles': cluster_articles,
                'size': len(cluster_articles)
            })
        
        return clusters
    
    def _filter_clusters(self, clusters: List[Dict]) -> List[Dict]:
        """Filter out clusters that are too small or too large"""
        filtered = []
        
        for cluster in clusters:
            size = cluster['size']
            
            # Skip if too small
            if size < self.min_cluster_size:
                print(f"  ⚠️ Skipping cluster {cluster['cluster_id']} (too small: {size} articles)")
                continue
            
            # If too large, might need splitting (future enhancement)
            if size > self.max_cluster_size:
                print(f"  ⚠️ Large cluster {cluster['cluster_id']} ({size} articles)")
            
            filtered.append(cluster)
        
        return filtered
    
    def calculate_cluster_coherence(self, cluster: Dict) -> float:
        """
        Calculate how coherent/tight a cluster is
        
        Args:
            cluster: Cluster dict with articles
        
        Returns:
            Coherence score (0-1, higher = more coherent)
        """
        articles = cluster['articles']
        
        if len(articles) < 2:
            return 1.0
        
        # Get all embeddings
        embeddings = np.array([a['embedding'] for a in articles])
        
        # Calculate pairwise similarities
        similarities = cosine_similarity(embeddings)
        
        # Average similarity (excluding diagonal)
        n = len(articles)
        total_similarity = (similarities.sum() - n) / (n * (n - 1))
        
        return float(total_similarity)
