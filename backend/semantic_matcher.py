# semantic_matcher.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict

class SemanticMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize semantic matcher with a pre-trained model.
        all-MiniLM-L6-v2 is fast, small, and accurate for news matching.
        """
        print(f"Loading semantic model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("✅ Semantic model loaded!")
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Convert text to embedding vector.
        """
        if not text or not text.strip():
            return np.zeros(384)  # Return zero vector for empty text
        return self.model.encode(text, convert_to_numpy=True)
    
    def get_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Convert multiple texts to embeddings (more efficient).
        """
        valid_texts = [t if t and t.strip() else " " for t in texts]
        return self.model.encode(valid_texts, convert_to_numpy=True)
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        Returns a score between -1 and 1 (higher = more similar).
        """
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def match_article_to_tags(
        self, 
        article_text: str, 
        tag_texts: List[str], 
        threshold: float = 0.3
    ) -> List[Dict]:
        """
        Match an article to multiple tags and return matches above threshold.
        Returns a list of dicts with {tag_index, similarity_score}.
        """
        article_embedding = self.get_embedding(article_text)
        tag_embeddings = self.get_embeddings_batch(tag_texts)
        matches = []
        for idx, tag_embedding in enumerate(tag_embeddings):
            similarity = self.calculate_similarity(article_embedding, tag_embedding)
            if similarity >= threshold:
                matches.append({
                    'tag_index': idx,
                    'similarity_score': similarity
                })
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return matches
    
    def create_tag_text(self, tag_name: str, keywords: List[str], category: str = "") -> str:
        """
        Combine tag information into text for embedding.
        """
        parts = [tag_name]
        if keywords:
            parts.append(" ".join(keywords))
        if category:
            parts.append(category)
        return " ".join(parts)
    
    def create_article_text(self, title: str, description: str = "", content: str = "") -> str:
        """
        Combine article information into text for embedding.
        Prioritize title and description (content is often truncated by NewsAPI).
        """
        parts = []
        if title:
            parts.append(title)
        if description:
            parts.append(description)
        if content:
            parts.append(content[:500])  # Limit length
        return " ".join(parts)
