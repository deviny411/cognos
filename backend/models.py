# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tags = relationship('Tag', back_populates='user', cascade='all, delete-orphan')

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tag_name = Column(String, nullable=False)
    category = Column(String)
    keywords = Column(JSON, default=list)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='tags')
    matched_articles = relationship('ArticleTag', back_populates='tag')

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text)
    url = Column(String, unique=True, nullable=False)
    source = Column(String)
    author = Column(String)
    image_url = Column(String)
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    matched_tags = relationship('ArticleTag', back_populates='article')

class ArticleTag(Base):
    __tablename__ = 'article_tags'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False)
    relevance_score = Column(Float, default=0.0)
    matched_at = Column(DateTime, default=datetime.utcnow)
    
    article = relationship('Article', back_populates='matched_tags')
    tag = relationship('Tag', back_populates='matched_articles')
