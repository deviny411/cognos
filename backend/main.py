# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ADD THIS
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database import get_db, init_db
from models import User, Tag, Article, ArticleTag
from news_fetcher import NewsFetcher
from fastapi.responses import HTMLResponse
from semantic_matcher import SemanticMatcher
from config import Config

semantic_matcher = SemanticMatcher()

app = FastAPI(title="Cognos", description="Intelligent conversation context platform")

# ADD CORS MIDDLEWARE - ADD THIS ENTIRE SECTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TagCreate(BaseModel):
    tag_name: str
    keywords: List[str] = []

class TagResponse(BaseModel):
    id: int
    tag_name: str
    keywords: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

@app.on_event("startup")
def startup_event():
    init_db()
    print("🚀 Cognos API started!")

@app.get("/")
def read_root():
    return {"app": "Cognos", "status": "running", "version": "0.1.0"}

@app.get("/test/newsapi")
def test_newsapi():
    fetcher = NewsFetcher()
    if fetcher.test_connection():
        return {"status": "success", "message": "NewsAPI connected"}
    else:
        raise HTTPException(status_code=500, detail="NewsAPI connection failed")

@app.post("/users")
def create_user(email: str, name: str, db: Session = Depends(get_db)):
    user = User(email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "name": user.name}

# ADD THIS NEW ENDPOINT
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return [{"id": user.id, "email": user.email, "name": user.name} for user in users]

# ADD THIS NEW ENDPOINT
@app.get("/tags")
def get_all_tags(db: Session = Depends(get_db)):
    """Get all tags (for frontend)"""
    tags = db.query(Tag).all()
    return [
        {
            "id": tag.id,
            "tag_name": tag.tag_name,
            "category": tag.category,
            "keywords": tag.keywords,
            "user_id": tag.user_id,
            "created_at": tag.created_at
        }
        for tag in tags
    ]

@app.post("/users/{user_id}/tags", response_model=TagResponse)
def create_tag(user_id: int, tag_data: TagCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tag = Tag(
        user_id=user_id,
        tag_name=tag_data.tag_name,
        category=None,  # Set to None for now, AI will fill later
        keywords=tag_data.keywords
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@app.get("/users/{user_id}/tags", response_model=List[TagResponse])
def get_user_tags(user_id: int, db: Session = Depends(get_db)):
    tags = db.query(Tag).filter(Tag.user_id == user_id).all()
    return tags

@app.get("/tags/{tag_id}/fetch-news")
def fetch_news_for_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    fetcher = NewsFetcher()
    articles = fetcher.fetch_by_keyword(tag.tag_name)
    
    # Prepare tag text for embedding
    tag_text = semantic_matcher.create_tag_text(
        tag.tag_name, 
        tag.keywords or [], 
        tag.category or ""
    )
    tag_embedding = semantic_matcher.get_embedding(tag_text)
    
    saved_count = 0
    matched_count = 0
    
    for article_data in articles:
        # Check if article already exists
        existing = db.query(Article).filter(Article.url == article_data['url']).first()
        if existing:
            article = existing
        else:
            article = Article(**article_data)
            db.add(article)
            db.commit()
            db.refresh(article)
            saved_count += 1
        
        # Prepare article text for embedding
        article_text = semantic_matcher.create_article_text(
            article.title,
            article.description or "",
            article.content or ""
        )
        article_embedding = semantic_matcher.get_embedding(article_text)
        similarity = semantic_matcher.calculate_similarity(article_embedding, tag_embedding)
        print(f"Article: {article.title[:60]}... | Similarity: {similarity:.3f}")

        # Only link if similarity is above threshold
        if similarity >= Config.SIMILARITY_THRESHOLD:
            # Check if link already exists
            existing_link = db.query(ArticleTag).filter(
                ArticleTag.article_id == article.id,
                ArticleTag.tag_id == tag.id
            ).first()
            if not existing_link:
                article_tag = ArticleTag(
                    article_id=article.id,
                    tag_id=tag.id,
                    relevance_score=similarity
                )
                db.add(article_tag)
                matched_count += 1
    
    db.commit()
    return {
        "tag": tag.tag_name,
        "fetched": len(articles),
        "new_articles": saved_count,
        "matched_articles": matched_count,
        "threshold": Config.SIMILARITY_THRESHOLD
    }

@app.get("/news/search")
def search_news_by_keyword(keyword: str, page_size: int = 10):
    """
    Quick search for news articles by keyword
    Returns articles with clickable URLs
    """
    fetcher = NewsFetcher()
    articles = fetcher.fetch_by_keyword(keyword, days_back=7)
    
    # Format for easy viewing
    results = []
    for article in articles[:page_size]:
        results.append({
            "title": article['title'],
            "description": article['description'],
            "url": article['url'],
            "source": article['source'],
            "published_at": article['published_at']
        })
    
    return {
        "keyword": keyword,
        "total_results": len(results),
        "articles": results
    }

@app.get("/tags/{tag_id}/articles")
def get_tag_articles(tag_id: int, min_score: float = 0.0, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    links = db.query(ArticleTag).filter(
        ArticleTag.tag_id == tag_id,
        ArticleTag.relevance_score >= min_score
    ).order_by(ArticleTag.relevance_score.desc()).all()
    results = []
    for link in links:
        article = db.query(Article).filter(Article.id == link.article_id).first()
        if article:
            results.append({
                "id": article.id,  # ADD THIS
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "description": article.description,
                "published_at": article.published_at,
                "relevance_score": link.relevance_score
            })
    return results  # SIMPLIFIED - just return the list

@app.get("/news/search-view", response_class=HTMLResponse)
def search_news_view(keyword: str, page_size: int = 5):
    """
    Returns a nice HTML page with clickable article links
    """
    fetcher = NewsFetcher()
    articles = fetcher.fetch_by_keyword(keyword, days_back=7)
    
    html = f"""
    <html>
        <head>
            <title>Cognos News Search - {keyword}</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                h1 {{ color: #333; }}
                .article {{ border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .article h3 {{ margin-top: 0; color: #0066cc; }}
                .article a {{ color: #0066cc; text-decoration: none; }}
                .article a:hover {{ text-decoration: underline; }}
                .meta {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <h1>News Search: "{keyword}"</h1>
            <p>Found {len(articles[:page_size])} articles</p>
    """
    
    for article in articles[:page_size]:
        html += f"""
            <div class="article">
                <h3><a href="{article['url']}" target="_blank">{article['title']}</a></h3>
                <p class="meta">Source: {article['source']} | Published: {article['published_at']}</p>
                <p>{article['description']}</p>
            </div>
        """
    
    html += """
        </body>
    </html>
    """
    
    return html

@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete a tag and all its associated article links"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Delete associated article-tag links first
    db.query(ArticleTag).filter(ArticleTag.tag_id == tag_id).delete()
    
    # Delete the tag
    db.delete(tag)
    db.commit()
    
    return {"message": f"Tag '{tag.tag_name}' deleted successfully", "id": tag_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
