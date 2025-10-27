from sentence_transformers import SentenceTransformer
import spacy
from typing import Dict, List
import numpy as np

class ArticleAnalyzer:
    """Analyzes articles and extracts AI features"""
    
    def __init__(self):
        print("🤖 Loading AI models...")
        # Load sentence transformer for embeddings
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        # Load spaCy for entity extraction
        self.nlp = spacy.load('en_core_web_sm')
        print("✅ AI models loaded")
    
    def analyze_article(self, article: Dict) -> Dict:
        """
        Analyze a single article with AI
        
        Args:
            article: Dict with 'title', 'description', 'full_text'
        
        Returns:
            Enhanced article dict with AI features
        """
        # Generate embedding (semantic vector representation)
        embedding = self.embedder.encode(
            article['full_text'], 
            convert_to_numpy=True
        )
        
        # Extract named entities
        doc = self.nlp(article['full_text'])
        entities = self._extract_entities(doc)
        
        # Extract keywords (noun phrases)
        keywords = self._extract_keywords(doc)
        
        # Add AI features to article
        article['embedding'] = embedding
        article['entities'] = entities
        article['keywords'] = keywords
        
        return article
    
    def _extract_entities(self, doc) -> List[Dict]:
        """Extract named entities from spaCy doc"""
        entities = []
        
        for ent in doc.ents:
            # Filter for important entity types
            if ent.label_ in ['PERSON', 'ORG', 'PRODUCT', 'GPE', 'EVENT', 'TECH']:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
        
        return entities
    
    def _extract_keywords(self, doc) -> List[str]:
        """Extract keyword phrases (noun chunks)"""
        keywords = []
        
        for chunk in doc.noun_chunks:
            # Filter out very short or very common phrases
            if len(chunk.text) > 3 and not chunk.text.lower() in ['the', 'a', 'an']:
                keywords.append(chunk.text.lower())
        
        return keywords
    
    def analyze_batch(self, articles: List[Dict]) -> List[Dict]:
        """
        Analyze multiple articles
        
        Args:
            articles: List of article dicts
        
        Returns:
            List of analyzed articles with AI features
        """
        print(f"🔬 Analyzing {len(articles)} articles with AI...")
        
        analyzed = []
        for i, article in enumerate(articles, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(articles)}")
            
            analyzed_article = self.analyze_article(article)
            analyzed.append(analyzed_article)
        
        print(f"✅ Analysis complete!")
        return analyzed
    
    def calculate_similarity(self, article1: Dict, article2: Dict) -> float:
        """
        Calculate semantic similarity between two articles
        
        Args:
            article1, article2: Analyzed articles with embeddings
        
        Returns:
            Similarity score (0-1, higher = more similar)
        """
        from sklearn.metrics.pairwise import cosine_similarity
        
        emb1 = article1['embedding'].reshape(1, -1)
        emb2 = article2['embedding'].reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
