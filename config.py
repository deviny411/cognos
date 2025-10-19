# config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./cognos.db')
    NEWS_API_BASE_URL = 'https://newsapi.org/v2'
    MAX_ARTICLES_PER_TAG = 5
    DAYS_BACK = 7

    # Semantic matching settings
    SEMANTIC_MODEL = 'all-MiniLM-L6-v2'  # Model name for sentence-transformers
    SIMILARITY_THRESHOLD = 0.3           # Minimum similarity score to link article to tag
