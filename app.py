#!/usr/bin/env python3
"""
Mawney Partners API with Full Daily News System Integration
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import urllib.request
import xml.etree.ElementTree as ET
import re
import json
import os
import feedparser  # Re-enabled for article monitoring
from email.utils import parsedate_to_datetime
import base64
import json

# Import AI Assistant System
from custom_ai_assistant import process_ai_query, process_ai_query_with_files
from ai_memory_system import store_interaction, get_memory_summary
from file_analyzer import file_analyzer

app = Flask(__name__)
CORS(app)

# Track sent notifications to prevent duplicates
sent_article_ids = set()
notification_queue = []

# Advanced AI memory system for learning and knowledge storage
ai_memory = {
    'user_preferences': {},
    'conversation_patterns': {},
    'learned_knowledge': {},
    'industry_insights': {},
    'user_interactions': {},
    'feedback_history': {},
    'expertise_areas': {},
    'context_memory': {}
}

# Chat system storage (in production, this would be a database)
chat_sessions = {
    'default': {
        'id': 'default',
        'name': 'General Chat',
        'topic': 'General AI assistance',
        'created_at': datetime.now().isoformat(),
        'user_id': 'system'
    }
}
chat_conversations = {
    'default': []
}
current_chat_sessions = {}  # Track current chat per user

# User data storage (in production, this would be a database)
user_profiles = {
    'hg@mawneypartners.com': {
        'email': 'hg@mawneypartners.com',
        'name': 'Hope Gilbert',
        'avatar': None,
        'preferences': {},
        'created_at': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat()
    },
    'jt@mawneypartners.com': {
        'email': 'jt@mawneypartners.com',
        'name': 'Joshua Trister',
        'avatar': None,
        'preferences': {},
        'created_at': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat()
    },
    'finance@mawneypartners.com': {
        'email': 'finance@mawneypartners.com',
        'name': 'Rachel Trister',
        'avatar': None,
        'preferences': {},
        'created_at': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat()
    },
    'jd@mawneypartners.com': {
        'email': 'jd@mawneypartners.com',
        'name': 'Jack Dalby',
        'avatar': None,
        'preferences': {},
        'created_at': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat()
    },
    'he@mawneypartners.com': {
        'email': 'he@mawneypartners.com',
        'name': 'Harry Edleman',
        'avatar': None,
        'preferences': {},
        'created_at': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat()
    },
    'tjt@mawneypartners.com': {
        'email': 'tjt@mawneypartners.com',
        'name': 'Tyler Johnson Thomas',
        'avatar': None,
        'preferences': {},
        'created_at': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat()
    }
}

# User-specific data storage
user_todos = {}  # user_email -> todos
user_call_notes = {}  # user_email -> call_notes
user_saved_jobs = {}  # user_email -> saved_jobs

# Shared compensation data (shared across all users)
compensations = []  # List of compensation entries

# Rate limiting for compensation endpoint
compensation_rate_limits = {}  # email -> {count: int, reset_time: datetime}
MAX_COMPENSATIONS_PER_REQUEST = 1000  # Maximum compensations that can be saved at once
MAX_COMPENSATION_VALUE = 100000000  # Maximum salary/bonus value (100 million)
MIN_COMPENSATION_VALUE = 0  # Minimum salary/bonus value
MAX_JOB_TITLE_LENGTH = 200
MAX_PERSON_NAME_LENGTH = 100

# User-to-user chat storage
user_chats = {}  # user_email -> list of chats
user_messages = {}  # chat_id -> list of messages
device_tokens = {}  # user_email -> device_token (for push notifications)

def check_for_new_articles():
    """Check for new articles and create notifications for ones not yet sent"""
    try:
        # Get current articles
        articles = get_daily_news_articles() if DAILY_NEWS_AVAILABLE else get_comprehensive_rss_articles()
        
        new_articles = []
        for article in articles:
            article_id = article['id']
            if article_id not in sent_article_ids:
                new_articles.append(article)
                sent_article_ids.add(article_id)
        
        # Create notifications for new articles
        for article in new_articles:
            notification = {
                'id': f"notif_{article['id']}",
                'title': '📰 New Credit Article',
                'body': f"{article['title']}\n\nSource: {article['source']}\nCategory: {article['category']}",
                'data': {
                    'type': 'article',
                    'articleId': article['id'],
                    'title': article['title'],
                    'content': article['content'],
                    'articleUrl': article['link'],
                    'source': article['source'],
                    'category': article['category'],
                    'relevanceScore': article['relevanceScore'],
                    'timestamp': datetime.now().isoformat()
                }
            }
            notification_queue.append(notification)
        
        print(f"🔔 Found {len(new_articles)} new articles, created {len(new_articles)} notifications")
        return new_articles
        
    except Exception as e:
        print(f"❌ Error checking for new articles: {e}")
        return []

# Import the full Daily News system
try:
    from config import Config
    from data_collector import DataCollector
    from data_processor import DataProcessor
    DAILY_NEWS_AVAILABLE = True
except ImportError:
    DAILY_NEWS_AVAILABLE = False
    print("Daily News system not available, using fallback RSS feeds")

def deduplicate_ft_articles(articles):
    """Aggressively deduplicate Financial Times articles that appear in multiple feeds"""
    if not articles:
        return articles
    
    # Track seen articles by title similarity and content
    seen_articles = []
    
    for article in articles:
        title = article.get('title', '').lower().strip()
        content = article.get('content', '').lower().strip()
        source = article.get('source', '')
        
        # Skip if we've seen a very similar article
        is_duplicate = False
        for seen in seen_articles:
            seen_title = seen.get('title', '').lower().strip()
            seen_content = seen.get('content', '').lower().strip()
            seen_source = seen.get('source', '')
            
            # Check for exact title match
            if title == seen_title:
                is_duplicate = True
                break
            
            # Check for very similar titles (90%+ similarity for FT)
            if calculate_title_similarity(title, seen_title) > 0.9:
                is_duplicate = True
                # Keep the one with higher relevance score
                if article.get('relevance_score', 0) > seen.get('relevance_score', 0):
                    seen_articles.remove(seen)
                    seen_articles.append(article)
                break
            
            # Check for same source and very similar content
            if source == seen_source and calculate_title_similarity(content, seen_content) > 0.95:
                is_duplicate = True
                break
        
        if not is_duplicate:
            seen_articles.append(article)
    
    return seen_articles

def aggressive_deduplicate(articles):
    """Final aggressive deduplication to catch any remaining duplicates"""
    if not articles:
        return articles
    
    # Use a dictionary to track unique articles by title
    unique_articles = {}
    
    for article in articles:
        title = article.get('title', '').strip()
        if not title:
            continue
            
        # Use normalized title as key
        normalized_title = title.lower().strip()
        
        # If we haven't seen this title, or if this article has higher relevance score
        if normalized_title not in unique_articles or article.get('relevance_score', 0) > unique_articles[normalized_title].get('relevance_score', 0):
            unique_articles[normalized_title] = article
    
    return list(unique_articles.values())

def calculate_title_similarity(title1, title2):
    """Calculate similarity between two titles"""
    if not title1 or not title2:
        return 0.0
    
    # Convert to sets of words
    words1 = set(title1.split())
    words2 = set(title2.split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def generate_professional_job_ad(query, job_examples):
    """Generate a professional job ad using the learned examples"""
    # Extract job title from query
    job_title = query.replace('write a job ad for', '').replace('create a job ad for', '').replace('generate a job ad for', '').strip()
    if not job_title:
        job_title = "Credit Investment Professional"
    
    # Use the professional style from the examples
    job_ad = f"""Our client, a top-performing credit fund are seeking to add a talented {job_title.lower()} to their growing team in London. This is a key hire for the fund, following several years of strong performance and AuM growth.

This individual will sit within a highly talented investment team to focus on investing in both public and private credit opportunities in Europe. The ideal candidate will therefore be able to demonstrate the following attributes:

• Origination, analysis and execution of credit investment opportunities on a pan-European basis
• In-depth knowledge of the high yield, distressed debt, and special situations in public and private markets
• Strong communication in presenting investment/trade ideas to senior individuals and the investment committee
• Using a developed sourcing network to originate investment ideas - amongst the restructuring firms, advisors, law firms, bank desks, etc.

Whilst our client would be seeking an individual at the Vice President-level and above, they do not wish to exclude any talented more junior candidates that may be able to demonstrate the above abilities. This will therefore suit an investment analyst who has gained experience within a similar credit strategy – or indeed, a background in opportunistic credit, distressed debt, or capital solutions investing.

This is a fantastic opportunity for a driven professional to join a highly regarded investment team."""

    return job_ad

def generate_basic_job_ad(query):
    """Generate a basic job ad template"""
    job_title = query.replace('write a job ad for', '').replace('create a job ad for', '').replace('generate a job ad for', '').strip()
    if not job_title:
        job_title = "Credit Investment Professional"
    
    return f"""**{job_title}**

**Company:** Mawney Partners
**Location:** London, UK
**Type:** Full-time

**About the Role:**
We are seeking a highly motivated professional to join our dynamic team. This role offers excellent opportunities for career growth and development in the financial services sector.

**Key Responsibilities:**
• Analyze market trends and provide strategic insights
• Collaborate with cross-functional teams
• Develop and maintain client relationships
• Contribute to business development initiatives

**Requirements:**
• Bachelor's degree in Finance, Economics, or related field
• 2+ years of relevant experience
• Strong analytical and communication skills
• Proficiency in financial modeling and analysis

**Benefits:**
• Competitive salary and bonus structure
• Comprehensive health and retirement benefits
• Professional development opportunities
• Collaborative and innovative work environment

**How to Apply:**
Please submit your CV and cover letter to careers@mawneypartners.com

*This is an AI-generated job advertisement based on your request.*"""

def search_online_articles(query):
    """Search for relevant articles using Daily News sources and logic"""
    try:
        print(f"🔍 Searching online for: {query}")
        
        # Extract search terms from query
        search_terms = extract_search_terms(query)
        print(f"🔍 Search terms: {search_terms}")
        
        # Get current articles from our comprehensive RSS feeds
        articles = get_comprehensive_rss_articles()
        
        # Filter articles based on search terms
        relevant_articles = filter_articles_by_search_terms(articles, search_terms)
        
        # Sort by relevance and recency
        relevant_articles.sort(key=lambda x: (
            x.get('relevanceScore', 0),
            datetime.fromisoformat(x.get('publishedAt', x.get('date', datetime.now().isoformat())).replace('Z', ''))
        ), reverse=True)
        
        # Take ALL relevant articles - no limit
        top_articles = relevant_articles
        
        if not top_articles:
            return f"""**No recent articles found for: "{query}"**

I searched through our comprehensive database of credit industry sources including Financial Times, Bloomberg, Creditflux, GlobalCapital, and more, but didn't find any recent articles matching your query.

**Suggestions:**
• Try different keywords or terms
• Check if the topic might be covered under different terminology
• Ask about broader market trends or specific companies

*Search performed across 30+ RSS feeds from leading financial sources.*"""
        
        # Format the response
        response = f"""**Latest Articles for: "{query}"**

I found {len(top_articles)} relevant articles from our comprehensive database of credit industry sources:

"""
        
        for i, article in enumerate(top_articles, 1):
            title = article.get('title', 'Untitled')
            source = article.get('source', 'Unknown Source')
            date = article.get('publishedAt', article.get('date', ''))
            link = article.get('link', '#')
            relevance = article.get('relevanceScore', 0)
            
            # Format date
            try:
                if date:
                    article_date = datetime.fromisoformat(date.replace('Z', ''))
                    formatted_date = article_date.strftime('%B %d, %Y')
                else:
                    formatted_date = 'Recent'
            except:
                formatted_date = 'Recent'
            
            response += f"""**{i}. {title}**
• **Source:** {source}
• **Date:** {formatted_date}
• **Relevance:** {relevance}/10
• **Link:** {link}

"""
        
        response += f"""*Search performed across 30+ RSS feeds including Financial Times, Bloomberg, Creditflux, GlobalCapital, Private Debt Investor, and more. Results sorted by relevance and recency.*"""
        
        return response
        
    except Exception as e:
        print(f"❌ Error in online search: {e}")
        return f"""**Search Error**

I encountered an error while searching for articles about "{query}". Please try again or rephrase your query.

*Error: {str(e)}*"""

def extract_search_terms(query):
    """Extract relevant search terms from user query"""
    # Remove common words and extract key terms
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'find', 'search', 'latest', 'news', 'articles', 'about', 'on', 'for', 'what', 'how', 'when', 'where', 'why'}
    
    # Convert to lowercase and split
    words = query.lower().split()
    
    # Filter out stop words and short words
    search_terms = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Add the original query as a fallback
    if not search_terms:
        search_terms = [query.lower()]
    
    # Add common credit industry terms if the query seems related
    credit_terms = ['credit', 'debt', 'bond', 'loan', 'leverage', 'distressed', 'special', 'situations', 'high', 'yield', 'investment', 'fund', 'market', 'financial', 'banking', 'finance']
    if any(term in query.lower() for term in credit_terms):
        # Add some relevant credit terms to improve search
        for term in credit_terms:
            if term not in search_terms and term in query.lower():
                search_terms.append(term)
    
    return search_terms

def filter_articles_by_search_terms(articles, search_terms):
    """Filter articles based on search terms"""
    relevant_articles = []
    
    for article in articles:
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        combined_text = f"{title} {content}"
        
        # Check if any search term appears in the article
        relevance_score = 0
        for term in search_terms:
            if term in title:
                relevance_score += 3  # Title matches are more important
            if term in content:
                relevance_score += 1  # Content matches are less important
        
        if relevance_score > 0:
            article['relevanceScore'] = relevance_score
            relevant_articles.append(article)
    
    return relevant_articles

def is_credit_relevant(title, content=""):
    """Check if article is relevant to credit industry using STRICT filtering"""
    if not title:
        return False, 0
    
    title_lower = title.lower()
    content_lower = content.lower()
    combined_text = f"{title_lower} {content_lower}"
    
    # EXCLUSION TERMS - Articles with these terms are automatically rejected
    exclusion_terms = [
        # Entertainment & Media
        'cinema', 'movie', 'film', 'theater', 'theatre', 'entertainment', 'sports', 'football', 'soccer',
        'cricket', 'tennis', 'golf', 'rugby', 'basketball', 'baseball', 'hockey', 'olympics',
        'everyman', 'odeon', 'cineworld', 'imax', 'netflix', 'disney', 'hbo', 'streaming',
        'patriots', 'new england', 'nfl', 'nba', 'mlb', 'nhl', 'team', 'player', 'coach',
        
        # Food & Hospitality
        'restaurant', 'food', 'dining', 'cooking', 'recipe', 'chef', 'hotel', 'travel', 'tourism',
        'vacation', 'holiday', 'flight', 'airline', 'cruise', 'shopping', 'retail', 'fashion',
        'clothing', 'beauty', 'cosmetics', 'supermarket', 'grocery', 'delivery', 'takeaway',
        'starbucks', 'coffee', 'mcdonalds', 'kfc', 'subway', 'pizza', 'burger', 'fast food',
        'lay off', 'layoff', 'layoffs', 'workers', 'employees', 'staff', 'job cuts',
        
        # Health & Medical
        'health', 'medical', 'pharmaceutical', 'drug', 'medicine', 'hospital', 'doctor', 'patient',
        'covid', 'vaccine', 'treatment', 'therapy', 'surgery', 'clinical', 'diagnosis',
        
        # Technology (Non-Financial)
        'technology', 'gaming', 'video game', 'smartphone', 'computer', 'software', 'app',
        'social media', 'facebook', 'twitter', 'instagram', 'tiktok', 'youtube', 'google',
        'apple', 'microsoft', 'tesla', 'space', 'nasa', 'ai', 'artificial intelligence',
        'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'nft', 'metaverse',
        'dell', 'intel', 'lithium', 'transocean', 'offshore', 'driller', 'drilling',
        
        # Energy & Environment
        'climate', 'environment', 'renewable', 'solar', 'wind', 'energy', 'oil', 'gas', 'mining',
        'carbon', 'emissions', 'green', 'sustainability', 'electric vehicle', 'ev',
        
        # Real Estate & Construction
        'real estate', 'property', 'housing', 'construction', 'architecture', 'design',
        'mortgage', 'rental', 'landlord', 'tenant', 'property market', 'house prices',
        
        # Arts & Culture
        'art', 'music', 'culture', 'literature', 'book', 'author', 'museum', 'gallery',
        'concert', 'festival', 'exhibition', 'theatre', 'drama', 'comedy',
        
        # Politics & Government
        'politics', 'election', 'government', 'parliament', 'congress', 'senate', 'president',
        'prime minister', 'minister', 'mp', 'senator', 'vote', 'voting', 'campaign',
        
        # Education & Research
        'education', 'school', 'university', 'college', 'student', 'teacher', 'research',
        'science', 'study', 'academic', 'professor', 'lecture', 'course', 'degree',
        
        # Legal & Crime
        'law', 'legal', 'court', 'judge', 'lawyer', 'attorney', 'crime', 'police', 'security',
        'military', 'defense', 'war', 'conflict', 'terrorism', 'fraud', 'scam',
        
        # General Business (Non-Credit) - Very relaxed to allow financial articles
        'startup', 'entrepreneur', 'innovation', 'product', 'service', 'customer', 'marketing',
        'advertising', 'brand', 'sales', 'revenue', 'profit', 'earnings', 'quarterly',
        # Removed 'ipo', 'merger', 'acquisition', 'takeover', 'deal', 'transaction' to allow financial deals
        # Removed 'equity', 'stock', 'shares', 'dividend', 'shareholder' to allow credit articles that mention these
        'venture capital', 'growth capital', 'seed funding',
        'series a', 'series b', 'series c', 'funding round', 'valuation',
        'unicorn', 'decacorn', 'exit', 'liquidity event', 'public offering',
        
        # Non-Financial Industries
        'automotive', 'car', 'vehicle', 'truck', 'manufacturing', 'production',
        'retail', 'consumer', 'shopping', 'e-commerce', 'online shopping',
        'telecommunications', 'telecom', 'mobile', 'wireless', 'broadband',
        'media', 'publishing', 'broadcasting', 'journalism', 'news media',
        'transportation', 'logistics', 'shipping', 'freight', 'delivery',
        'agriculture', 'farming', 'crop', 'livestock', 'food production',
        'pharmaceuticals', 'biotech', 'healthcare', 'medical device',
        'aerospace', 'defense', 'military', 'aviation', 'aircraft',
        
        # Technology (Non-Financial)
        'software', 'hardware', 'cloud', 'saas', 'paas', 'iaas', 'api',
        'database', 'server', 'network', 'cybersecurity', 'data center',
        'machine learning', 'deep learning', 'neural network', 'algorithm',
        'robotics', 'automation', 'iot', 'internet of things', 'smart device',
        'wearable', 'fitness tracker', 'smartwatch', 'smart home',
        
        # Entertainment & Lifestyle
        'gaming', 'esports', 'video game', 'console', 'pc gaming', 'mobile game',
        'streaming', 'podcast', 'youtube', 'twitch', 'social media',
        'influencer', 'content creator', 'vlogger', 'blogger',
        'fashion', 'beauty', 'lifestyle', 'wellness', 'fitness', 'gym',
        'travel', 'vacation', 'hotel', 'airline', 'cruise', 'tourism',
        
        # Sports & Recreation
        'football', 'soccer', 'basketball', 'baseball', 'tennis', 'golf',
        'cricket', 'rugby', 'hockey', 'olympics', 'world cup', 'championship',
        'tournament', 'league', 'team', 'player', 'coach', 'stadium',
        'fitness', 'workout', 'exercise', 'marathon', 'triathlon',
        
        # Food & Dining
        'restaurant', 'cafe', 'coffee', 'food', 'dining', 'cuisine', 'chef',
        'recipe', 'cooking', 'baking', 'kitchen', 'menu', 'delivery',
        'fast food', 'fine dining', 'catering', 'food truck', 'bar',
        'wine', 'beer', 'cocktail', 'beverage', 'drink',
        
        # Arts & Culture
        'art', 'painting', 'sculpture', 'gallery', 'museum', 'exhibition',
        'music', 'concert', 'festival', 'album', 'song', 'artist', 'band',
        'theater', 'drama', 'comedy', 'film', 'movie', 'cinema', 'actor',
        'director', 'producer', 'script', 'screenplay', 'award', 'oscar',
        
        # Education & Research
        'university', 'college', 'school', 'education', 'student', 'teacher',
        'professor', 'research', 'study', 'academic', 'scholarship', 'degree',
        'curriculum', 'course', 'lecture', 'seminar', 'conference', 'paper',
        'thesis', 'dissertation', 'publication', 'journal', 'textbook',
        
        # Commodities & Precious Metals
        'gold', 'silver', 'platinum', 'palladium', 'precious metal', 'precious metals',
        'commodity', 'commodities', 'ounce', 'per ounce', 'bullion', 'ingot',
        'mining', 'miner', 'copper', 'aluminum', 'steel', 'iron', 'lithium',
        'crude oil', 'oil price', 'gas price', 'natural gas', 'petroleum'
    ]
    
    # Check for exclusion terms first - if found, reject immediately
    # But be much more selective about what we exclude
    strict_exclusions = [
        # Only exclude truly non-financial content
        'cinema', 'movie', 'film', 'theater', 'theatre', 'entertainment', 'sports', 'football', 'soccer',
        'cricket', 'tennis', 'golf', 'rugby', 'basketball', 'baseball', 'hockey', 'olympics',
        'everyman', 'odeon', 'cineworld', 'imax', 'netflix', 'disney', 'hbo', 'streaming',
        'restaurant', 'food', 'dining', 'cooking', 'recipe', 'chef', 'hotel', 'travel', 'tourism',
        'vacation', 'holiday', 'flight', 'airline', 'cruise', 'shopping', 'retail', 'fashion',
        'clothing', 'beauty', 'cosmetics', 'supermarket', 'grocery', 'delivery', 'takeaway',
        'health', 'medical', 'pharmaceutical', 'drug', 'medicine', 'hospital', 'doctor', 'patient',
        'covid', 'vaccine', 'treatment', 'therapy', 'surgery', 'clinical', 'diagnosis',
        'gaming', 'video game', 'smartphone', 'computer', 'software', 'app',
        'social media', 'facebook', 'twitter', 'instagram', 'tiktok', 'youtube', 'google',
        'apple', 'microsoft', 'tesla', 'space', 'nasa', 'ai', 'artificial intelligence',
        'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'nft', 'metaverse',
        'climate', 'environment', 'renewable', 'solar', 'wind', 'energy', 'oil', 'gas', 'mining',
        'carbon', 'emissions', 'green', 'sustainability', 'electric vehicle', 'ev',
        'real estate', 'property', 'housing', 'construction', 'architecture', 'design',
        'mortgage', 'rental', 'landlord', 'tenant', 'property market', 'house prices',
        'art', 'music', 'culture', 'literature', 'book', 'author', 'museum', 'gallery',
        'concert', 'festival', 'exhibition', 'theatre', 'drama', 'comedy',
        'politics', 'election', 'government', 'parliament', 'congress', 'senate', 'president',
        'prime minister', 'minister', 'mp', 'senator', 'vote', 'voting', 'campaign',
        'education', 'school', 'university', 'college', 'student', 'teacher', 'research',
        'science', 'study', 'academic', 'professor', 'lecture', 'course', 'degree',
        'law', 'legal', 'court', 'judge', 'lawyer', 'attorney', 'crime', 'police', 'security',
        'military', 'defense', 'war', 'conflict', 'terrorism', 'fraud', 'scam',
        'gold', 'silver', 'platinum', 'palladium', 'precious metal', 'commodity',
        'ounce', 'per ounce', 'bullion', 'mining', 'copper', 'aluminum', 'steel'
    ]
    
    for exclusion in strict_exclusions:
        if exclusion in combined_text:
            return False, 0
    
    # Core credit terms - must contain these for high relevance
    core_credit_terms = [
        # Credit Markets & Trading
        'corporate credit', 'credit markets', 'credit spreads', 'credit rating', 'credit default', 'credit risk',
        'credit default swap', 'credit derivatives', 'credit portfolio', 'credit analysis', 'credit trading',
        'credit fund', 'credit strategy', 'credit investment', 'credit manager', 'credit analyst',
        'credit trader', 'credit research', 'credit desk', 'credit team', 'credit division',
        'credit hedge fund', 'credit long short', 'credit arbitrage', 'credit alpha',
        
        # Bonds & Debt Instruments
        'corporate bonds', 'bond issuance', 'bond market', 'bond trading', 'bond portfolio',
        'debt issuance', 'debt refinancing', 'debt restructuring', 'debt capital markets',
        'high yield bonds', 'investment grade bonds', 'distressed debt', 'debt securities',
        'bond yields', 'bond spreads', 'bond prices', 'bond indices', 'bond funds',
        'junk bonds', 'fallen angels', 'crossover bonds', 'convertible bonds',
        'perpetual bonds', 'subordinated debt', 'senior debt', 'mezzanine debt',
        
        # Leveraged Finance
        'leveraged finance', 'leveraged loans', 'leveraged buyout', 'leveraged credit',
        'leveraged debt', 'leveraged lending', 'leveraged fund', 'leveraged portfolio',
        'leveraged loan market', 'leveraged loan index', 'leveraged loan fund',
        'covenant lite', 'covenant heavy', 'unitranche', 'first lien', 'second lien',
        
        # Private Credit & Direct Lending
        'private credit', 'private debt', 'direct lending', 'private lending',
        'credit lending', 'debt lending', 'loan origination', 'credit origination',
        'middle market lending', 'sponsor finance', 'cash flow lending',
        'asset based lending', 'working capital lending', 'term loan',
        
        # Structured Credit
        'clo', 'collateralised loan obligation', 'collateralized loan obligation',
        'securitised finance', 'securitized finance', 'asset backed securities',
        'abs', 'structured credit', 'structured debt', 'credit securitization',
        'cdo', 'collateralized debt obligation', 'synthetic cdo', 'cash flow cdo',
        'rmbs', 'cmbs', 'auto abs', 'credit card abs', 'student loan abs',
        
        # Specialized Credit
        'specialty finance', 'special situations', 'distressed credit', 'distressed lending',
        'credit restructuring', 'debt restructuring', 'workout', 'credit workout',
        'debt advisory', 'turnaround', 'bankruptcy', 'insolvency', 'liquidation',
        'debt for equity', 'debt exchange', 'debt buyback', 'debt tender',
        
        # Fixed Income & Treasury
        'fixed income', 'treasury', 'government bonds', 'sovereign debt',
        'gilts', 'treasuries', 'bunds', 'oats', 'bonds', 'yield curve',
        'duration', 'convexity', 'credit curve', 'swap spread', 'basis',
        
        # Credit Risk & Analytics
        'credit risk', 'credit scoring', 'credit assessment', 'credit monitoring',
        'credit surveillance', 'credit metrics', 'credit models', 'credit stress testing',
        'pd', 'probability of default', 'lgd', 'loss given default', 'ead', 'exposure at default',
        'var', 'value at risk', 'credit var', 'expected loss', 'unexpected loss',
        
        # Credit Instruments & Products
        'credit facility', 'credit line', 'revolving credit', 'term credit', 'bridge loan',
        'credit agreement', 'credit facility agreement', 'credit documentation',
        'credit enhancement', 'credit guarantee', 'credit insurance', 'credit protection',
        'credit derivative', 'credit swap', 'total return swap', 'credit linked note',
        'credit default swap', 'cds', 'credit event', 'credit trigger',
        
        # Credit Markets & Trading
        'credit trading', 'credit desk', 'credit trader', 'credit sales', 'credit research',
        'credit analyst', 'credit strategist', 'credit portfolio manager',
        'credit market making', 'credit liquidity', 'credit bid', 'credit ask',
        'credit spread trading', 'credit basis trading', 'credit curve trading',
        
        # Credit Funds & Investment
        'credit fund', 'credit hedge fund', 'credit mutual fund', 'credit etf',
        'credit long short', 'credit arbitrage', 'credit alpha', 'credit beta',
        'credit allocation', 'credit selection', 'credit timing', 'credit rotation',
        'credit overweight', 'credit underweight', 'credit neutral',
        
        # Credit Ratings & Agencies
        'credit rating', 'credit rating agency', 'rating action', 'rating change',
        'rating upgrade', 'rating downgrade', 'rating outlook', 'rating watch',
        'investment grade', 'speculative grade', 'high grade', 'low grade',
        'rating methodology', 'rating criteria', 'rating scale',
        
        # Credit Events & Distress
        'credit event', 'credit default', 'credit impairment', 'credit loss',
        'credit write-off', 'credit provision', 'credit charge-off',
        'credit recovery', 'credit workout', 'credit restructuring',
        'credit forbearance', 'credit modification', 'credit amendment',
        
        # Credit Regulation & Compliance
        'credit regulation', 'credit compliance', 'credit governance', 'credit policy',
        'credit limit', 'credit exposure', 'credit concentration', 'credit diversification',
        'credit monitoring', 'credit reporting', 'credit disclosure', 'credit transparency'
    ]
    
    # Secondary credit terms - need at least 2 matches AND must be in financial context
    # Made much more restrictive to avoid general business articles
    secondary_terms = [
        # Core credit terms only
        'credit', 'debt', 'bond', 'loan', 'lending', 'finance', 'financial', 'fund', 'investment',
        'bank', 'banking', 'capital', 'yield', 'spread', 'rating', 'default', 'risk', 'leverage', 
        'private', 'corporate', 'structured', 'securitization', 'distressed', 'restructuring', 
        'advisory', 'fixed income', 'covenant', 'collateral', 'guarantee', 'insurance', 
        'protection', 'enhancement', 'analyst', 'manager', 'trader', 'desk', 'strategy', 
        'alpha', 'beta', 'duration', 'convexity', 'basis', 'swap', 'derivative', 'hedge',
        'allocation', 'selection', 'timing', 'rotation', 'overweight', 'underweight',
        'upgrade', 'downgrade', 'outlook', 'watch', 'methodology', 'criteria',
        'impairment', 'loss', 'write-off', 'provision', 'charge-off', 'recovery',
        'forbearance', 'modification', 'amendment', 'compliance', 'governance',
        'exposure', 'concentration', 'diversification', 'monitoring', 'reporting',
        'disclosure', 'transparency', 'regulation', 'policy', 'limit',
        # Credit-specific financial terms only
        'securities', 'portfolio', 'issuance', 'refinancing', 'asset', 'assets', 
        'institutional', 'pension', 'endowment', 'sovereign', 'treasury', 'central bank',
        'monetary', 'fiscal', 'economic', 'economy', 'gdp', 'inflation', 'interest rate',
        'currency', 'forex', 'fx', 'derivatives', 'options', 'futures', 'forwards', 
        'swaps', 'cds', 'abs', 'mbs', 'rmbs', 'cmbs', 'reit', 'reits', 'etf', 'etfs', 
        'mutual fund', 'hedge fund', 'private equity', 'venture capital', 'growth capital', 
        'mezzanine', 'senior', 'subordinated', 'convertible', 'perpetual', 'floating', 
        'fixed', 'variable', 'margin', 'liquidity', 'solvency', 'gearing', 'debt to equity', 
        'debt ratio', 'creditworthiness', 'credit quality', 'credit risk', 'market risk', 
        'operational risk', 'regulatory', 'compliance', 'basel', 'capital adequacy', 
        'stress test', 'rating agency', 'moody', 's&p', 'fitch', 'investment grade', 
        'speculative grade', 'high yield', 'junk', 'fallen angel', 'crossover', 
        'special situations', 'workout', 'bankruptcy', 'insolvency', 'liquidation', 
        'administration', 'receivership', 'cva', 'iva', 'scheme of arrangement', 
        'debt for equity', 'debt exchange', 'tender offer', 'buyback', 'amend and extend',
        'covenant waiver', 'covenant reset', 'standstill', 'moratorium'
    ]
    
    # Credit company names - Major credit-focused firms
    credit_companies = [
        # Credit-Focused Asset Managers
        'oaktree', 'apollo', 'ares', 'carlyle', 'kkr', 'blackstone', 'silver point', 
        'king street', 'blue owl', 'eldridge', 'pimco', 'golub capital', 'antares capital',
        'tpg', 'bain capital', 'brookfield', 'centerbridge', 'cerberus', 'fortress',
        'gso', 'hps', 'intermediate capital', 'marlin equity', 'monroe capital',
        'new mountain', 'oaktree capital', 'pennantpark', 'prospect capital',
        'sixth street', 'stone point', 'tpg credit', 'vista equity', 'warburg pincus',
        
        # Traditional Asset Managers (Credit Divisions)
        'blackrock', 'fidelity', 'vanguard', 'invesco', 'franklin templeton',
        'allianz', 'axa', 'legal & general', 'prudential', 'aegon', 'metlife',
        
        # Investment Banks (Credit Divisions)
        'goldman sachs', 'morgan stanley', 'jpmorgan', 'bank of america', 'wells fargo',
        'citigroup', 'barclays', 'deutsche bank', 'credit suisse', 'ubs',
        'bnp paribas', 'societe generale', 'hsbc', 'standard chartered',
        'nomura', 'mizuho', 'sumitomo mitsui', 'mitsubishi ufj',
        
        # Credit Rating Agencies
        'moody', 's&p', 'standard & poor', 'fitch', 'db', 'dow jones',
        
        # Credit Exchanges & Platforms
        'tradeweb', 'marketaxess', 'bloomberg', 'refinitiv', 'ice', 'intercontinental exchange',
        
        # Credit Insurance & Guarantees
        'ambac', 'mbia', 'assured guaranty', 'berkshire hathaway', 'aig'
    ]
    
    # Check for core credit terms first
    core_matches = [term for term in core_credit_terms if term.lower() in combined_text]
    
    # Check for secondary credit terms
    secondary_matches = [term for term in secondary_terms if term.lower() in combined_text and term not in core_credit_terms]
    
    # Check for credit company names
    company_matches = [company for company in credit_companies if company.lower() in combined_text]
    
    # Calculate relevance score
    relevance_score = 0
    is_relevant = False
    
    if core_matches:
        # Core terms get highest priority - must have at least 1 core term
        relevance_score = len(core_matches) * 4  # Increased multiplier
        is_relevant = True
        print(f"✅ Core credit term match: {core_matches} (Score: {relevance_score})")
    elif len(secondary_matches) >= 2:  # Need at least 2 secondary terms for relevance
        relevance_score = len(secondary_matches) + 2
        is_relevant = True
        print(f"✅ Secondary credit terms match: {secondary_matches} (Score: {relevance_score})")
    elif len(secondary_matches) == 1:
        print(f"⚠️ Only 1 secondary term found: {secondary_matches} - requiring 2+ for relevance")
    elif company_matches:
        # Credit company mentions - much more permissive context check
        # Check if company mention is accompanied by any financial terms
        financial_context_terms = ['credit', 'debt', 'bond', 'loan', 'lending', 'fund', 'investment', 'portfolio', 'finance', 'financial', 'bank', 'banking', 'capital', 'market', 'trading', 'securities', 'yield', 'spread', 'rating', 'default', 'risk', 'leverage', 'private', 'corporate', 'equity', 'stock', 'shares', 'dividend', 'issuance', 'refinancing', 'deal', 'transaction', 'acquisition', 'merger', 'ipo', 'asset', 'assets', 'revenue', 'profit', 'earnings', 'quarterly', 'annual', 'institutional', 'pension', 'endowment', 'sovereign', 'treasury', 'central bank', 'monetary', 'fiscal', 'economic', 'economy', 'gdp', 'inflation', 'interest rate', 'currency', 'forex', 'fx', 'commodity', 'commodities', 'derivatives', 'options', 'futures', 'forwards', 'swaps', 'cds', 'abs', 'mbs', 'rmbs', 'cmbs', 'reit', 'reits', 'etf', 'etfs', 'mutual fund', 'hedge fund', 'private equity', 'venture capital', 'growth capital', 'mezzanine', 'senior', 'subordinated', 'convertible', 'perpetual', 'floating', 'fixed', 'variable', 'spread', 'margin', 'liquidity', 'solvency', 'leverage', 'gearing', 'debt to equity', 'debt ratio', 'creditworthiness', 'credit quality', 'credit risk', 'market risk', 'operational risk', 'regulatory', 'compliance', 'basel', 'solvency', 'capital adequacy', 'stress test', 'rating agency', 'moody', 's&p', 'fitch', 'investment grade', 'speculative grade', 'high yield', 'junk', 'fallen angel', 'crossover', 'distressed', 'special situations', 'workout', 'bankruptcy', 'insolvency', 'liquidation', 'administration', 'receivership', 'cva', 'iva', 'scheme of arrangement', 'debt for equity', 'debt exchange', 'tender offer', 'buyback', 'refinancing', 'restructuring', 'amend and extend', 'covenant waiver', 'covenant reset', 'forbearance', 'standstill', 'moratorium']
        has_financial_context = any(term in combined_text for term in financial_context_terms)
        
        if has_financial_context:
            relevance_score = len(company_matches) * 3  # Increased multiplier
            is_relevant = True
            print(f"✅ Credit company with financial context: {company_matches} (Score: {relevance_score})")
        else:
            print(f"❌ Company mention without financial context: {company_matches}")
    
    # STRICT FALLBACK - only accept articles with strong financial/credit context
    if not is_relevant:
        # Check for strong financial/credit terms that indicate relevance
        strong_financial_terms = [
            'credit', 'debt', 'bond', 'loan', 'lending', 'treasury', 'yield', 'spread', 'rating', 'default',
            'leverage', 'collateral', 'securitization', 'cdo', 'cmo', 'abs', 'mbs', 'rmbs', 'cmbs', 'clo',
            'cfo', 'cbo', 'synthetic', 'derivative', 'swap', 'cds', 'credit default', 'credit risk', 'credit fund',
            'credit manager', 'credit trader', 'credit analyst', 'private credit', 'direct lending', 'distressed debt',
            'high yield', 'investment grade', 'speculative grade', 'fallen angel', 'crossover', 'special situations',
            'workout', 'restructuring', 'bankruptcy', 'insolvency', 'liquidation', 'administration', 'receivership',
            'debt for equity', 'debt exchange', 'tender offer', 'buyback', 'refinancing', 'amend and extend',
            'covenant waiver', 'covenant reset', 'forbearance', 'standstill', 'moratorium', 'credit facility',
            'credit line', 'credit limit', 'credit score', 'credit rating', 'credit report', 'credit bureau',
            'credit union', 'credit card', 'credit check', 'credit history', 'credit worthiness', 'credit quality',
            'credit exposure', 'credit loss', 'credit provision', 'credit reserve', 'credit charge', 'credit cost',
            'credit margin', 'credit spread', 'credit curve', 'credit market', 'credit cycle', 'credit event',
            'credit crisis', 'credit crunch', 'credit freeze', 'credit thaw', 'credit recovery', 'credit growth',
            'credit expansion', 'credit contraction', 'credit tightening', 'credit easing', 'credit stimulus',
            'credit support', 'credit enhancement', 'credit guarantee', 'credit insurance', 'credit protection',
            'credit hedge', 'credit arbitrage', 'credit strategy', 'credit investment', 'credit allocation',
            'credit selection', 'credit timing', 'credit rotation', 'credit rebalancing', 'credit optimization',
            'credit performance', 'credit return', 'credit alpha', 'credit beta', 'credit correlation',
            'credit volatility', 'credit liquidity', 'credit duration', 'credit convexity', 'credit sensitivity',
            'credit attribution', 'credit analysis', 'credit research', 'credit modeling', 'credit valuation',
            'credit pricing', 'credit structuring', 'credit origination', 'credit underwriting', 'credit approval',
            'credit monitoring', 'credit surveillance', 'credit reporting', 'credit disclosure', 'credit transparency',
            'credit regulation', 'credit compliance', 'credit governance', 'credit risk management',
            'credit portfolio management', 'credit asset management', 'credit fund management',
            'credit investment management', 'credit wealth management', 'credit private banking',
            'credit institutional', 'credit corporate', 'credit commercial', 'credit retail', 'credit consumer',
            'credit mortgage', 'credit auto', 'credit student', 'credit personal', 'credit business',
            'credit small business', 'credit middle market', 'credit large corporate', 'credit investment grade',
            'credit high yield', 'credit distressed', 'credit special situations', 'credit event driven',
            'credit long short', 'credit market neutral', 'credit relative value', 'credit absolute return',
            'credit total return', 'credit income', 'credit growth', 'credit value', 'credit equity',
            'credit hybrid', 'credit convertible', 'credit preferred', 'credit subordinated', 'credit senior',
            'credit junior', 'credit mezzanine', 'credit bridge', 'credit acquisition', 'credit buyout',
            'credit recapitalization', 'credit restructuring', 'credit workout', 'credit recovery',
            'credit turnaround', 'credit distressed', 'credit special situations', 'credit event driven',
            'credit merger arbitrage', 'credit activist', 'credit shareholder', 'credit proxy',
            'credit governance', 'credit esg', 'credit sustainability', 'credit impact', 'credit responsible',
            'credit ethical', 'credit social', 'credit environmental', 'credit governance', 'credit stewardship',
            'credit engagement', 'credit voting', 'credit proxy', 'credit shareholder', 'credit activist',
            'credit hedge fund', 'credit private equity', 'credit venture capital', 'credit real estate',
            'credit infrastructure', 'credit natural resources', 'credit commodities', 'credit energy',
            'credit utilities', 'credit telecommunications', 'credit technology', 'credit healthcare',
            'credit biotechnology', 'credit pharmaceuticals', 'credit consumer', 'credit retail',
            'credit industrial', 'credit manufacturing', 'credit automotive', 'credit aerospace',
            'credit defense', 'credit government', 'credit municipal', 'credit sovereign',
            'credit emerging markets', 'credit developed markets', 'credit global', 'credit international',
            'credit domestic', 'credit regional', 'credit local', 'credit cross border', 'credit offshore',
            'credit onshore', 'credit tax efficient', 'credit tax advantaged', 'credit tax exempt',
            'credit taxable', 'credit tax deferred', 'credit tax free', 'credit tax sheltered',
            'credit tax optimized', 'credit tax managed', 'credit tax aware', 'credit tax sensitive'
        ]
        
        # Check if article has strong financial/credit context
        has_strong_context = any(term in combined_text for term in strong_financial_terms)
        
        if has_strong_context:
            relevance_score = 1
            is_relevant = True
            print(f"✅ Article accepted by strict financial fallback: '{title[:50]}...' (Score: {relevance_score})")
        else:
            print(f"❌ Article rejected by strict fallback: '{title[:50]}...' (No strong financial context)")
    
    if not is_relevant:
        print(f"❌ Article filtered out: '{title[:50]}...' (No financial relevance)")
    
    return is_relevant, relevance_score

def fetch_authenticated_rss_feed(feed_url, username=None, password=None):
    """Fetch RSS feed with authentication if credentials provided"""
    try:
        if username and password:
            # Create authenticated request
            import base64
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            
            req = urllib.request.Request(feed_url)
            req.add_header('Authorization', f'Basic {credentials}')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8')
        else:
            # Regular request without authentication
            with urllib.request.urlopen(feed_url, timeout=10) as response:
                return response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ Error fetching authenticated feed {feed_url}: {e}")
        return None

def get_comprehensive_rss_articles():
    """Get articles from comprehensive RSS feeds with credit-specific filtering"""
    articles = []
    
    # Comprehensive RSS feeds from Daily News system - Updated with working feeds
    feeds = [
        # Financial Times (working feeds)
        'https://www.ft.com/rss/markets',
        'https://www.ft.com/rss/home',
        'https://www.ft.com/rss/companies',
        'https://www.ft.com/rss/world',
        
        # Bloomberg (working feeds)
        'https://feeds.bloomberg.com/markets/news.rss',
        'https://feeds.bloomberg.com/news.rss',
        'https://feeds.bloomberg.com/politics.rss',
        
        # Other Financial Sources (working)
        'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114',
        'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
        'https://feeds.marketwatch.com/marketwatch/marketpulse/',
        'https://feeds.marketwatch.com/marketwatch/topstories/',
        'https://feeds.marketwatch.com/marketwatch/marketpulse/',
        
        # Additional Working Financial Sources
        'https://feeds.finance.yahoo.com/rss/2.0/headline',
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC',
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^IXIC',
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^DJI',
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^VIX',
        
        # Business News Sources
        'https://feeds.npr.org/1001/rss.xml',  # NPR Business
        'https://feeds.npr.org/1006/rss.xml',  # NPR Economy
        'https://feeds.npr.org/1007/rss.xml',  # NPR Money
        
        # Financial News
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL',
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=MSFT',
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=GOOGL',
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=AMZN',
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=TSLA',
        
        # With Intelligence (Premium Credit Industry Sources)
        'https://www.withintelligence.com/rss',
        'https://www.withintelligence.com/feed',
        'https://www.withintelligence.com/rss.xml',
        'https://www.withintelligence.com/feeds/rss',
        'https://www.withintelligence.com/news/rss',
        'https://www.withintelligence.com/content/rss',
        
        # Creditflux (Premium Credit Industry News) - Updated URLs
        'https://www.creditflux.com/rss',
        'https://www.creditflux.com/feed',
        'https://www.creditflux.com/rss.xml',
        'https://www.creditflux.com/news/rss',
        'https://www.creditflux.com/content/rss',
        'https://www.creditflux.com/feeds/rss',
        
        # eFinancialCareers (Credit Job Moves & Team Changes)
        'https://www.efinancialcareers.com/rss',
        'https://www.efinancialcareers.com/feed',
        'https://www.efinancialcareers.com/rss.xml',
        
        # HedgeWeek (Credit Fund & Trading News)
        'https://www.hedgeweek.com/rss',
        'https://www.hedgeweek.com/feed',
        'https://www.hedgeweek.com/rss.xml',
        
        # PR Newswire (Credit Industry Press Releases)
        'https://www.prnewswire.com/rss',
        'https://www.prnewswire.com/feed',
        'https://www.prnewswire.com/rss.xml',
        
        # Additional Premium Credit Industry Sources
        'https://www.globalcapital.com/rss',
        'https://www.globalcapital.com/feed',
        'https://www.globalcapital.com/rss.xml',
        'https://www.privatedebtinvestor.com/rss',
        'https://www.privatedebtinvestor.com/feed',
        'https://www.privatedebtinvestor.com/rss.xml',
        'https://www.loanpricing.com/rss',
        'https://www.loanpricing.com/feed',
        'https://www.loanpricing.com/rss.xml',
        'https://www.creditflux.com/CLOs/rss',
        'https://www.creditflux.com/Funds/rss',
        'https://www.creditflux.com/News/rss',
        'https://www.creditflux.com/Analysis/rss',
        
        # Additional Credit Industry Sources
        'https://www.privateequitywire.co.uk/rss',
        'https://www.altassets.net/rss',
        'https://www.privateequityinternational.com/rss',
        'https://www.privateequitynews.com/rss'
    ]
    
    print(f"🔍 Starting RSS article fetch from {len(feeds)} feeds...")
    
    for feed_url in feeds:
        try:
            # Handle authenticated feeds (With Intelligence)
            if 'withintelligence.com' in feed_url:
                # Get credentials from environment
                import os
                username = os.getenv('WITH_INTELLIGENCE_USERNAME')
                password = os.getenv('WITH_INTELLIGENCE_PASSWORD')
                
                if username and password:
                    print(f"🔐 Fetching authenticated feed: {feed_url}")
                    content = fetch_authenticated_rss_feed(feed_url, username, password)
                    if not content:
                        print(f"❌ With Intelligence feed returned no content: {feed_url}")
                        continue
                    
                    print(f"📊 With Intelligence feed content length: {len(content) if content else 0}")
                    
                    # Check if feed has content
                    try:
                        root = ET.fromstring(content)
                        items = root.findall('.//item')
                        print(f"📊 With Intelligence feed items found: {len(items)}")
                        if len(items) == 0:
                            print(f"📭 With Intelligence feed is empty (0 articles) - checking feed structure...")
                            # Debug: print first 500 chars of content
                            print(f"📊 Feed content preview: {content[:500] if content else 'None'}")
                    except Exception as e:
                        print(f"❌ Error parsing With Intelligence feed: {e}")
                        print(f"📊 Raw content preview: {content[:500] if content else 'None'}")
                else:
                    print(f"⚠️ No credentials for With Intelligence feed: {feed_url}")
                    continue
            else:
                # Fetch regular RSS feed
                with urllib.request.urlopen(feed_url, timeout=10) as response:
                    content = response.read().decode('utf-8')
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Find all items
            items = root.findall('.//item')
            
            for item in items:  # Check all items for better filtering
                title_elem = item.find('title')
                description_elem = item.find('description')
                link_elem = item.find('link')
                pubdate_elem = item.find('pubDate')
                
                if title_elem is not None:
                    title = title_elem.text or ''
                    description = description_elem.text if description_elem is not None else ''
                    
                    # Use comprehensive credit filtering
                    is_relevant, relevance_score = is_credit_relevant(title, description)
                    
                    if is_relevant and relevance_score >= 1:  # Include relevant articles (lowered threshold)
                        link = link_elem.text if link_elem is not None else ''
                        
                        # Get publication date from RSS feed
                        pub_date = datetime.now().isoformat()  # Default to now
                        if pubdate_elem is not None and pubdate_elem.text:
                            try:
                                # Parse RSS pubDate format (e.g., "Tue, 24 Sep 2024 10:00:00 GMT")
                                pub_date = parsedate_to_datetime(pubdate_elem.text).isoformat()
                            except:
                                pub_date = datetime.now().isoformat()
                        
                        # Filter out articles older than 30 days
                        try:
                            article_date = datetime.fromisoformat(pub_date.replace('Z', ''))
                            days_old = (datetime.now() - article_date).days
                            if days_old > 30:
                                print(f"❌ Filtered out old article: {title[:50]}... (Age: {days_old} days)")
                                continue
                        except:
                            # If date parsing fails, assume it's recent
                            pass
                        
                        # Clean up description
                        description = re.sub(r'<[^>]+>', '', description)  # Remove HTML tags
                        description = description[:300] + '...' if len(description) > 300 else description
                        
                        # Determine source
                        source = 'Financial Times' if 'ft.com' in feed_url else \
                                'Bloomberg' if 'bloomberg.com' in feed_url else \
                                'CNBC' if 'cnbc.com' in feed_url else \
                                'WSJ' if 'dj.com' in feed_url else \
                                'MarketWatch' if 'marketwatch.com' in feed_url else \
                                'Creditflux' if 'creditflux.com' in feed_url else \
                                'GlobalCapital' if 'globalcapital.com' in feed_url else \
                                'Private Debt Investor' if 'privatedebtinvestor.com' in feed_url else \
                                'With Intelligence' if 'withintelligence.com' in feed_url else \
                                'Reuters' if 'reuters.com' in feed_url else \
                                'Other'
                        
                        # Determine category with comprehensive logic
                        category = 'Market Moves'  # Default
                        
                        # People Moves - Executive appointments, hires, departures
                        people_moves_keywords = [
                            'appointed', 'hired', 'joined', 'promoted', 'resigned', 'departed', 'leaves', 'leaving',
                            'named', 'appointed as', 'takes over', 'takes charge', 'new head', 'new ceo', 'new cfo',
                            'replaces', 'succeeds', 'takes helm', 'leadership', 'executive', 'director', 'managing director',
                            'partner', 'principal', 'senior', 'vice president', 'vp', 'chief', 'chairman', 'chair',
                            'meet the', 'profile', 'interview', 'career', 'background', 'experience', 'biography',
                            'joins', 'departs', 'exits', 'retires', 'steps down', 'moves to', 'switches to',
                            'poached', 'recruited', 'headhunted', 'lured', 'attracted', 'brought in'
                        ]
                        
                        # Regulatory & Compliance
                        regulatory_keywords = [
                            'regulation', 'regulatory', 'fca', 'sec', 'compliance', 'regulator', 'regulators',
                            'enforcement', 'fine', 'penalty', 'sanction', 'investigation', 'probe', 'inquiry',
                            'oversight', 'supervision', 'monitoring', 'audit', 'review', 'guidance', 'rules',
                            'policy', 'legislation', 'law', 'legal', 'court', 'judge', 'ruling', 'decision',
                            'ban', 'prohibition', 'restriction', 'limitation', 'requirement', 'mandate'
                        ]
                        
                        # Deals & Transactions
                        deals_keywords = [
                            'deal', 'deals', 'transaction', 'acquisition', 'merger', 'takeover', 'buyout',
                            'investment', 'funding', 'financing', 'loan', 'credit facility', 'syndication',
                            'issuance', 'issuing', 'launch', 'launched', 'announces', 'announced', 'agrees',
                            'agreement', 'partnership', 'joint venture', 'alliance', 'collaboration',
                            'purchase', 'sale', 'sold', 'bought', 'acquired', 'merges', 'combines'
                        ]
                        
                        # Market Analysis & Commentary
                        analysis_keywords = [
                            'analysis', 'commentary', 'outlook', 'forecast', 'prediction', 'trend', 'trends',
                            'report', 'study', 'research', 'survey', 'index', 'indices', 'benchmark',
                            'performance', 'returns', 'yields', 'spreads', 'pricing', 'valuation',
                            'market view', 'market outlook', 'market analysis', 'sector analysis',
                            'economic', 'economy', 'gdp', 'inflation', 'rates', 'monetary', 'fiscal'
                        ]
                        
                        # Fund & Product Launches
                        fund_keywords = [
                            'fund', 'funds', 'launch', 'launched', 'launching', 'new fund', 'new product',
                            'strategy', 'strategies', 'portfolio', 'investment strategy', 'fund strategy',
                            'alternative', 'private', 'hedge', 'mutual', 'etf', 'etfs', 'index fund',
                            'institutional', 'pension', 'endowment', 'sovereign', 'wealth management',
                            'asset management', 'investment management', 'fund management'
                        ]
                        
                        # Check for People Moves first (highest priority)
                        if any(keyword in title.lower() for keyword in people_moves_keywords):
                            category = 'People Moves'
                        # Check for Regulatory
                        elif any(keyword in title.lower() for keyword in regulatory_keywords):
                            category = 'Regulatory'
                        # Check for Deals & Transactions
                        elif any(keyword in title.lower() for keyword in deals_keywords):
                            category = 'Deals & Transactions'
                        # Check for Market Analysis
                        elif any(keyword in title.lower() for keyword in analysis_keywords):
                            category = 'Market Analysis'
                        # Check for Fund/Product launches
                        elif any(keyword in title.lower() for keyword in fund_keywords):
                            category = 'Fund & Product Launches'
                        
                        article = {
                            'id': f"live_{abs(hash(title))}",
                            'title': title,
                            'content': description,
                            'source': source,
                            'date': pub_date,
                            'link': link,
                            'category': category,
                            'relevanceScore': relevance_score
                        }
                        articles.append(article)
                        print(f"✅ Credit-relevant article: {title[:50]}... (Score: {relevance_score}, Source: {source})")
                                    
        except Exception as e:
            print(f"Error with feed {feed_url}: {e}")
            continue
    
    # Sort by relevance score (highest first)
    articles.sort(key=lambda x: x['relevanceScore'], reverse=True)
    
    print(f"✅ RSS fetch complete: {len(articles)} articles found")
    
    # Return ALL relevant articles - no limit
    return articles

def get_daily_news_articles():
    """Get articles from the full Daily News system if available"""
    if not DAILY_NEWS_AVAILABLE:
        return []
    
    try:
        # Initialize Daily News system
        collector = DataCollector()
        processor = DataProcessor()
        
        # Load recent data - 30 days to get more articles
        historical_data = processor.load_historical_data(days=30)
        
        articles = []
        for data in historical_data:
            if 'market_moves' in data:
                articles.extend(data['market_moves'])
            if 'people_moves' in data:
                articles.extend(data['people_moves'])
        
        # Process and filter articles
        articles = processor.deduplicate_articles(articles)
        
        # Additional aggressive deduplication for FT articles
        articles = deduplicate_ft_articles(articles)
        
        # Final aggressive deduplication at API level
        articles = aggressive_deduplicate(articles)
        
        # EMERGENCY: Simple exact title deduplication
        print(f"DEBUG: Before deduplication: {len(articles)} articles")
        seen_titles = set()
        final_articles = []
        duplicates_removed = 0
        
        for article in articles:
            title = article.get('title', '').strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                final_articles.append(article)
            else:
                duplicates_removed += 1
                print(f"DEBUG: Removed exact duplicate: {title}")
        
        articles = final_articles
        print(f"DEBUG: After deduplication: {len(articles)} articles, removed {duplicates_removed} duplicates")
        
        # FORCE: Additional check for remaining duplicates
        if duplicates_removed == 0 and len(articles) > 0:
            print("WARNING: No duplicates removed but duplicates still exist!")
            # Get all titles to see what's happening
            all_titles = [article.get('title', '') for article in articles]
            title_counts = {}
            for title in all_titles:
                title_counts[title] = title_counts.get(title, 0) + 1
            for title, count in title_counts.items():
                if count > 1:
                    print(f"STILL DUPLICATE: {title} appears {count} times")
        
        # Convert to API format and filter by date
        api_articles = []
        for article in articles:  # ALL articles - no limit
            # Filter out articles older than 30 days
            try:
                article_date_str = article.get('date', datetime.now().isoformat())
                article_date = datetime.fromisoformat(article_date_str.replace('Z', ''))
                days_old = (datetime.now() - article_date).days
                if days_old > 30:
                    print(f"❌ Filtered out old Daily News article: {article.get('title', '')[:50]}... (Age: {days_old} days)")
                    continue
            except:
                # If date parsing fails, assume it's recent
                pass
            
            api_articles.append({
                'id': f"daily_{abs(hash(article.get('title', '')))}",
                'title': article.get('title', 'No title'),
                'content': article.get('content', 'No content')[:300] + '...',
                'source': article.get('source', 'Daily News'),
                'date': article.get('date', datetime.now().isoformat()),
                'link': article.get('link', ''),
                'category': article.get('category', 'Market Moves'),
                'relevanceScore': article.get('relevance_score', 5)
            })
        
        return api_articles
        
    except Exception as e:
        print(f"Error getting Daily News articles: {e}")
        return []

@app.route('/')
def home():
    return "Welcome to Mawney Partners API with Full Daily News Integration!"

@app.route('/api/health')
def health():
    return jsonify({
        "status": "ok",
        "message": "Mawney Partners API with Comprehensive Credit News Sources",
                "version": "10.0",
        "daily_news_available": DAILY_NEWS_AVAILABLE,
        "sources": "35+ RSS feeds including FT, Bloomberg, Creditflux, GlobalCapital, Private Debt Investor, With Intelligence, and more",
        "deployment": "FORCE RESTART - Fix duplicate articles with simple deduplication"
    })

@app.route('/api/articles')
def get_articles():
    try:
        print(f"🔍 Starting article fetch...")
        
        # Try to get articles from Daily News system first
        print(f"📊 Daily News available: {DAILY_NEWS_AVAILABLE}")
        articles = get_daily_news_articles()
        print(f"📊 Daily News articles: {len(articles) if articles else 0}")
        
        if not articles:
            # Fallback to comprehensive RSS feeds
            print(f"🔄 Falling back to RSS feeds...")
            articles = get_comprehensive_rss_articles()
            print(f"📊 RSS articles: {len(articles) if articles else 0}")
        
        if articles:
            # FINAL DEDUPLICATION AT API LEVEL
            print(f"🔧 API-level deduplication: {len(articles)} articles before")
            seen_titles = set()
            deduplicated_articles = []
            duplicates_removed = 0
            
            for article in articles:
                title = article.get('title', '').strip()
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    deduplicated_articles.append(article)
                else:
                    duplicates_removed += 1
                    print(f"🔧 API removed duplicate: {title}")
            
            articles = deduplicated_articles
            print(f"🔧 API deduplication complete: {len(articles)} articles, removed {duplicates_removed} duplicates")
            
            print(f"✅ Returning {len(articles)} articles")
            return jsonify({
                "success": True,
                "articles": articles,
                "count": len(articles),
                "source": "COMPREHENSIVE CREDIT NEWS SOURCES",
                "timestamp": datetime.now().isoformat()
            })
        
        # Final fallback to basic articles
        fallback_articles = [
            {
                'id': '1',
                'title': 'Comprehensive Credit Market Update',
                'content': 'Real-time credit market analysis from 30+ sources including Financial Times, Bloomberg, Creditflux, and GlobalCapital.',
                'source': 'Mawney Partners API',
                'date': datetime.now().isoformat(),
                'link': 'https://example.com',
                'category': 'Market Moves',
                'relevanceScore': 8
            }
        ]
        
        return jsonify({
            "success": True,
            "articles": fallback_articles,
            "count": len(fallback_articles),
            "source": "FALLBACK - Comprehensive sources not available",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "articles": []
        }), 500

@app.route('/api/ai/summary', methods=['GET'])
def get_ai_summary():
    """Get comprehensive AI summary of articles from past 24 hours only"""
    try:
        # Get articles (either from Daily News or RSS)
        articles = get_daily_news_articles() if DAILY_NEWS_AVAILABLE else get_comprehensive_rss_articles()
        
        if not articles:
            return jsonify({
                "success": False,
                "error": "No articles available"
            }), 500

        # DEDUPLICATION FOR AI SUMMARY
        print(f"🔧 AI Summary deduplication: {len(articles)} articles before")
        seen_titles = set()
        deduplicated_articles = []
        duplicates_removed = 0
        
        for article in articles:
            title = article.get('title', '').strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                deduplicated_articles.append(article)
            else:
                duplicates_removed += 1
                print(f"🔧 AI Summary removed duplicate: {title}")
        
        articles = deduplicated_articles
        print(f"🔧 AI Summary deduplication complete: {len(articles)} articles, removed {duplicates_removed} duplicates")

        # Filter articles from past 24 hours ONLY
        now = datetime.now()
        past_24_hours = []
        
        for article in articles:
            try:
                # Parse article date - handle multiple date formats
                article_date = None
                date_fields = ['date', 'publishedAt', 'published_date', 'timestamp']
                
                for field in date_fields:
                    if field in article and article[field]:
                        try:
                            date_str = article[field]
                            # Remove 'Z' suffix if present
                            if date_str.endswith('Z'):
                                date_str = date_str[:-1]
                            article_date = datetime.fromisoformat(date_str)
                            break
                        except:
                            continue
                
                if not article_date:
                    continue
                
                # Check if within 24 hours only
                time_diff = now - article_date.replace(tzinfo=None)
                if time_diff.total_seconds() <= 24 * 3600:  # 24 hours in seconds
                    past_24_hours.append(article)
            except Exception as e:
                print(f"Error parsing date for article: {e}")
                continue

        if not past_24_hours:
            return jsonify({
                "success": False,
                "error": "No articles from past 24 hours available for analysis"
            }), 500

        # Comprehensive analysis of past 24 hours articles
        titles = [article.get('title', '') for article in past_24_hours]
        sources = list(set([article.get('source', 'Unknown') for article in past_24_hours]))
        categories = list(set([article.get('category', 'Unknown') for article in past_24_hours]))
        
        # Count articles by category
        category_counts = {}
        for article in past_24_hours:
            cat = article.get('category', 'Unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Count articles by source
        source_counts = {}
        for article in past_24_hours:
            src = article.get('source', 'Unknown')
            source_counts[src] = source_counts.get(src, 0) + 1
        
        # Analyze content themes
        content_themes = []
        for article in past_24_hours:
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            combined_text = title + ' ' + content
            
            # Identify key themes
            if any(word in combined_text for word in ['interest rate', 'fed', 'central bank', 'monetary policy']):
                content_themes.append('Monetary Policy')
            if any(word in combined_text for word in ['bond', 'yield', 'treasury', 'government debt']):
                content_themes.append('Government Bonds')
            if any(word in combined_text for word in ['corporate', 'credit', 'debt', 'issuance']):
                content_themes.append('Corporate Credit')
            if any(word in combined_text for word in ['default', 'distressed', 'restructuring']):
                content_themes.append('Credit Risk')
            if any(word in combined_text for word in ['merger', 'acquisition', 'm&a', 'deal']):
                content_themes.append('M&A Activity')
        
        theme_counts = {}
        for theme in content_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        # Analyze actual article content for meaningful insights
        article_insights = []
        key_headlines = []
        detailed_analysis = []
        
        # Analyze only top 5 most relevant articles for concise summary
        for article in past_24_hours[:5]:
            title = article.get('title', '')
            content = article.get('content', '')
            source = article.get('source', '')
            
            key_headlines.append(f"• {title} ({source})")
            
            # Create concise analysis of each article
            if title and content:
                # Extract key insights from article content
                if any(word in (title + content).lower() for word in ['rate', 'interest', 'fed', 'central bank', 'monetary policy']):
                    article_insights.append(f"Interest rate developments: {title}")
                    detailed_analysis.append(f"Interest rates: {title} - {content[:80]}...")
                elif any(word in (title + content).lower() for word in ['bond', 'yield', 'treasury', 'government debt']):
                    article_insights.append(f"Fixed income activity: {title}")
                    detailed_analysis.append(f"Bond markets: {title} - {content[:80]}...")
                elif any(word in (title + content).lower() for word in ['credit', 'debt', 'issuance', 'corporate']):
                    article_insights.append(f"Credit market news: {title}")
                    detailed_analysis.append(f"Credit markets: {title} - {content[:80]}...")
                elif any(word in (title + content).lower() for word in ['merger', 'acquisition', 'deal', 'm&a']):
                    article_insights.append(f"M&A activity: {title}")
                    detailed_analysis.append(f"M&A deals: {title} - {content[:80]}...")
                elif any(word in (title + content).lower() for word in ['default', 'distressed', 'restructuring', 'bankruptcy']):
                    article_insights.append(f"Credit risk developments: {title}")
                    detailed_analysis.append(f"Credit risk: {title} - {content[:80]}...")
                else:
                    # General credit market news
                    article_insights.append(f"Market development: {title}")
                    detailed_analysis.append(f"General: {title} - {content[:80]}...")
        
        # Generate comprehensive summary based on actual article analysis
        summary = {
            "executive_summary": f"24-Hour Credit Market Summary: {len(past_24_hours)} key developments from {len(sources)} sources. Focus areas: {', '.join(list(category_counts.keys())[:2])} with {', '.join(list(theme_counts.keys())[:2]) if theme_counts else 'credit market activity'}.",
            
            "key_points": key_headlines[:5] if key_headlines else [
                f"📊 {len(past_24_hours)} articles analyzed from past 24 hours",
                f"📰 Top sources: {', '.join([f'{src} ({count})' for src, count in list(source_counts.items())[:3]])}",
                f"📈 Market sectors: {', '.join([f'{cat} ({count})' for cat, count in list(category_counts.items())[:3]])}",
                f"🎯 Key themes: {', '.join([f'{theme} ({count})' for theme, count in list(theme_counts.items())[:3]]) if theme_counts else 'Credit market developments'}",
                f"⏰ Analysis period: Last 24 hours (as of {now.strftime('%Y-%m-%d %H:%M UTC')})"
            ],
            
            "market_insights": detailed_analysis[:3] if detailed_analysis else [
                f"Recent activity shows {len(past_24_hours)} significant credit market developments",
                f"Primary coverage from: {', '.join(list(source_counts.keys())[:3])}",
                f"Market focus areas: {', '.join(list(category_counts.keys())[:3])}",
                f"Key themes emerging: {', '.join(list(theme_counts.keys())[:3]) if theme_counts else 'General market activity'}",
                "Credit market conditions reflect real-time developments and immediate market responses",
                "Investment implications based on current market intelligence"
            ],
            
            "articles_analyzed": len(past_24_hours),
            "analysis_period": "Past 24 hours only",
            "timestamp": datetime.now().isoformat(),
            "data_freshness": "Real-time analysis of latest articles",
            "key_headlines": key_headlines if key_headlines else []
        }
        
        return jsonify({
            "success": True,
            "summary": summary
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get pending notifications for the mobile app"""
    try:
        # Check for new articles first
        check_for_new_articles()
        
        # Return queued notifications
        notifications = notification_queue.copy()
        notification_queue.clear()  # Clear the queue after sending
        
        return jsonify({
            "success": True,
            "notifications": notifications,
            "count": len(notifications),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "notifications": []
        }), 500

@app.route('/api/test-notification', methods=['POST'])
def test_notification():
    """Test endpoint to create a test notification"""
    try:
        test_notification = {
            'id': f"test_{datetime.now().timestamp()}",
            'title': '🧪 Test Notification',
            'body': 'This is a test notification from Mawney Partners API',
            'data': {
                'type': 'test',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        notification_queue.append(test_notification)
        
        return jsonify({
            "success": True,
            "message": "Test notification created",
            "notification": test_notification
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/trigger-collection', methods=['POST'])
def trigger_collection():
    """Manually trigger article collection and refresh"""
    try:
        print("🔄 Manual article collection triggered")
        
        # Clear any cached data
        global last_collection_time
        last_collection_time = None
        
        # Force fresh collection
        if DAILY_NEWS_AVAILABLE:
            articles = get_daily_news_articles()
            source = "Daily News System"
        else:
            articles = get_comprehensive_rss_articles()
            source = "RSS Feeds"
        
        article_count = len(articles) if articles else 0
        
        return jsonify({
            "success": True,
            "message": f"Article collection triggered successfully",
            "articles_collected": article_count,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error triggering collection: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Chat API endpoints
@app.route('/api/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """Get all chat sessions for the user"""
    try:
        # For now, return all sessions (in production, filter by user_id)
        return jsonify({
            "success": True,
            "sessions": chat_sessions
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat/sessions', methods=['POST'])
def create_chat_session():
    """Create a new chat session"""
    try:
        data = request.get_json()
        chat_name = data.get('name', 'New Chat')
        user_id = data.get('user_id', 'default_user')
        
        # Generate new chat ID
        chat_id = f"chat_{int(datetime.now().timestamp() * 1000)}"
        
        # Create new chat session
        new_chat = {
            'id': chat_id,
            'name': chat_name,
            'topic': 'New conversation',
            'created_at': datetime.now().isoformat(),
            'user_id': user_id
        }
        
        # Add to sessions
        chat_sessions[chat_id] = new_chat
        chat_conversations[chat_id] = []
        
        return jsonify({
            "success": True,
            "chat_id": chat_id,
            "session": new_chat
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat/sessions/<chat_id>', methods=['DELETE'])
def delete_chat_session(chat_id):
    """Delete a chat session"""
    try:
        if chat_id == 'default':
            return jsonify({
                "success": False,
                "error": "Cannot delete default chat"
            }), 400
        
        if chat_id in chat_sessions:
            del chat_sessions[chat_id]
            if chat_id in chat_conversations:
                del chat_conversations[chat_id]
            
            return jsonify({
                "success": True,
                "message": "Chat deleted successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Chat not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat/sessions/<chat_id>/conversations', methods=['GET'])
def get_chat_conversations(chat_id):
    """Get conversations for a specific chat"""
    try:
        if chat_id in chat_conversations:
            return jsonify({
                "success": True,
                "conversations": chat_conversations[chat_id]
            })
        else:
            return jsonify({
                "success": True,
                "conversations": []
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat/sessions/<chat_id>/conversations', methods=['POST'])
def add_chat_conversation(chat_id):
    """Add a conversation to a chat"""
    try:
        data = request.get_json()
        user_message = data.get('user_message')
        ai_response = data.get('ai_response')
        
        if not user_message or not ai_response:
            return jsonify({
                "success": False,
                "error": "Missing user_message or ai_response"
            }), 400
        
        # Initialize chat if it doesn't exist
        if chat_id not in chat_conversations:
            chat_conversations[chat_id] = []
        
        # Add conversation
        conversation = {
            'id': f"conv_{int(datetime.now().timestamp() * 1000)}",
            'user_message': user_message,
            'ai_response': ai_response,
            'timestamp': datetime.now().isoformat()
        }
        
        chat_conversations[chat_id].append(conversation)
        
        return jsonify({
            "success": True,
            "conversation": conversation
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat/current', methods=['POST'])
def set_current_chat():
    """Set the current chat for a user"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        user_id = data.get('user_id', 'default_user')
        
        if chat_id in chat_sessions:
            current_chat_sessions[user_id] = chat_id
            return jsonify({
                "success": True,
                "current_chat": chat_id
            })
        else:
            return jsonify({
                "success": False,
                "error": "Chat not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat/current', methods=['GET'])
def get_current_chat():
    """Get the current chat for a user"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        current_chat = current_chat_sessions.get(user_id, 'default')
        
        return jsonify({
            "success": True,
            "current_chat": current_chat
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def store_memory(key, value, memory_type='learned_knowledge', user_id=None):
    """Store information in AI memory with categorization"""
    try:
        if user_id:
            if user_id not in ai_memory[memory_type]:
                ai_memory[memory_type][user_id] = {}
            ai_memory[memory_type][user_id][key] = {
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'access_count': 0
            }
        else:
            ai_memory[memory_type][key] = {
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'access_count': 0
            }
        print(f"🧠 Stored memory: {key} in {memory_type}")
        return True
    except Exception as e:
        print(f"❌ Error storing memory: {e}")
        return False

def retrieve_memory(key, memory_type='learned_knowledge', user_id=None):
    """Retrieve information from AI memory with access tracking"""
    try:
        if user_id and user_id in ai_memory[memory_type]:
            if key in ai_memory[memory_type][user_id]:
                ai_memory[memory_type][user_id][key]['access_count'] += 1
                return ai_memory[memory_type][user_id][key]['value']
        elif key in ai_memory[memory_type]:
            ai_memory[memory_type][key]['access_count'] += 1
            return ai_memory[memory_type][key]['value']
        return None
    except Exception as e:
        print(f"❌ Error retrieving memory: {e}")
        return None

def learn_from_interaction(query, response, user_id=None, feedback=None):
    """Learn from user interactions and feedback"""
    try:
        # Store the interaction
        interaction_key = f"interaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        store_memory(interaction_key, {
            'query': query,
            'response': response,
            'feedback': feedback,
            'success': feedback is None or feedback > 0
        }, 'user_interactions', user_id)
        
        # Learn from patterns
        if user_id:
            if user_id not in ai_memory['conversation_patterns']:
                ai_memory['conversation_patterns'][user_id] = []
            
            ai_memory['conversation_patterns'][user_id].append({
                'query_type': classify_query(query.lower()),
                'query_length': len(query),
                'response_type': response.get('type', 'unknown'),
                'confidence': response.get('confidence', 0.5),
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 50 interactions per user
            if len(ai_memory['conversation_patterns'][user_id]) > 50:
                ai_memory['conversation_patterns'][user_id] = ai_memory['conversation_patterns'][user_id][-50:]
        
        # Extract and store knowledge
        extract_and_store_knowledge(query, response)
        
        print(f"🧠 Learned from interaction: {query[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Error learning from interaction: {e}")
        return False

def extract_and_store_knowledge(query, response):
    """Extract knowledge from interactions and store it"""
    try:
        query_lower = query.lower()
        
        # Extract financial terms and concepts
        financial_terms = ['clo', 'cdo', 'credit', 'bond', 'debt', 'leverage', 'spread', 'yield', 'default']
        for term in financial_terms:
            if term in query_lower:
                knowledge_key = f"financial_term_{term}"
                store_memory(knowledge_key, {
                    'term': term,
                    'context': query,
                    'explanation': response.get('text', ''),
                    'confidence': response.get('confidence', 0.5)
                }, 'learned_knowledge')
        
        # Extract industry insights
        if 'market' in query_lower or 'trend' in query_lower:
            insight_key = f"market_insight_{datetime.now().strftime('%Y%m%d')}"
            store_memory(insight_key, {
                'topic': query,
                'insight': response.get('text', ''),
                'source': 'user_interaction'
            }, 'industry_insights')
        
        # Extract user preferences
        if 'prefer' in query_lower or 'like' in query_lower or 'want' in query_lower:
            preference_key = f"preference_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            store_memory(preference_key, {
                'preference': query,
                'context': response.get('context', ''),
                'timestamp': datetime.now().isoformat()
            }, 'user_preferences')
        
    except Exception as e:
        print(f"❌ Error extracting knowledge: {e}")

def get_user_context(user_id=None):
    """Get comprehensive user context from memory"""
    try:
        context = {
            'recent_interactions': [],
            'preferences': {},
            'expertise_areas': [],
            'conversation_style': 'professional'
        }
        
        if user_id:
            # Get recent interactions
            if user_id in ai_memory['user_interactions']:
                recent_interactions = list(ai_memory['user_interactions'][user_id].items())[-5:]
                context['recent_interactions'] = [interaction[1] for interaction in recent_interactions]
            
            # Get user preferences
            if user_id in ai_memory['user_preferences']:
                context['preferences'] = ai_memory['user_preferences'][user_id]
            
            # Get conversation patterns
            if user_id in ai_memory['conversation_patterns']:
                patterns = ai_memory['conversation_patterns'][user_id]
                if patterns:
                    # Analyze conversation style
                    avg_confidence = sum(p.get('confidence', 0.5) for p in patterns) / len(patterns)
                    if avg_confidence > 0.8:
                        context['conversation_style'] = 'detailed'
                    elif avg_confidence < 0.6:
                        context['conversation_style'] = 'simple'
        
        return context
    except Exception as e:
        print(f"❌ Error getting user context: {e}")
        return {}

def enhance_response_with_memory(response, user_id=None, query=None):
    """Enhance response using memory and context"""
    try:
        user_context = get_user_context(user_id)
        
        # Add personalized elements based on memory
        if user_context.get('conversation_style') == 'detailed':
            if response.get('type') == 'definition':
                response['text'] += "\n\n*Additional context based on your previous questions about financial concepts.*"
        
        # Add relevant insights from memory
        if query and 'market' in query.lower():
            market_insights = ai_memory['industry_insights']
            if market_insights:
                recent_insight = list(market_insights.items())[-1]
                if recent_insight:
                    response['text'] += f"\n\n*Related insight: {recent_insight[1].get('insight', '')[:100]}...*"
        
        # Add user-specific recommendations
        if user_id and user_id in ai_memory['user_preferences']:
            preferences = ai_memory['user_preferences'][user_id]
            if preferences:
                response['text'] += "\n\n*Based on your preferences, here are some additional considerations...*"
        
        return response
    except Exception as e:
        print(f"❌ Error enhancing response with memory: {e}")
        return response

def generate_intelligent_response(query, query_lower, chat_id, context):
    """Generate intelligent AI responses with advanced capabilities"""
    try:
        # Get conversation history for context
        conversation_history = chat_conversations.get(chat_id, [])
        
        # Advanced query classification
        query_type = classify_query(query_lower)
        confidence = calculate_confidence(query_lower, query_type)
        
        # Context-aware response generation
        if query_type == 'job_ad':
            response_text = generate_advanced_job_ad(query, conversation_history)
            return {
                "success": True,
                "text": response_text,
                "type": "job_ad",
                "confidence": confidence,
                "actions": ["copy_to_clipboard", "save_job_ad"],
                "context": "Professional job advertisement generated"
            }
        
        elif query_type == 'definition':
            response_text = generate_advanced_definition(query, conversation_history)
            return {
                "success": True,
                "text": response_text,
                "type": "definition",
                "confidence": confidence,
                "actions": ["copy_to_clipboard"],
                "context": "Financial term definition provided"
            }
        
        elif query_type == 'market_analysis':
            response_text = generate_market_analysis(query, conversation_history)
            return {
                "success": True,
                "text": response_text,
                "type": "market_insight",
                "confidence": confidence,
                "actions": ["copy_to_clipboard", "save_analysis"],
                "context": "Market analysis and insights provided"
            }
        
        elif query_type == 'search':
            response_text = search_online_articles(query)
            return {
                "success": True,
                "text": response_text,
                "type": "online_search",
                "confidence": confidence,
                "actions": ["copy_to_clipboard"],
                "context": "Latest articles and market information"
            }
        
        elif query_type == 'cv_help':
            response_text = generate_cv_guidance(query, conversation_history)
            return {
                "success": True,
                "text": response_text,
                "type": "cv_format",
                "confidence": confidence,
                "actions": ["copy_to_clipboard", "save_cv"],
                "context": "CV formatting and career guidance"
            }
        
        elif query_type == 'conversation':
            response_text = generate_conversational_response(query, conversation_history)
            return {
                "success": True,
                "text": response_text,
                "type": "answer",
                "confidence": confidence,
                "actions": ["copy_to_clipboard"],
                "context": "Conversational response with context"
            }
        
        else:
            # Fallback to general intelligent response
            response_text = generate_general_response(query, conversation_history)
            return {
                "success": True,
                "text": response_text,
                "type": "answer",
                "confidence": 0.7,
                "actions": ["copy_to_clipboard"],
                "context": "General intelligent response"
            }
    
    except Exception as e:
        print(f"❌ Error in generate_intelligent_response: {e}")
        return {
            "success": False,
            "text": "I apologize, but I encountered an error processing your request. Please try again.",
            "type": "error",
            "confidence": 0.0,
            "actions": [],
            "context": "Error in AI processing"
        }

def classify_query(query_lower):
    """Advanced query classification with multiple criteria"""
    # Job-related queries
    job_keywords = ['job', 'ad', 'advertisement', 'posting', 'position', 'role', 'career', 'hiring', 'recruit']
    if any(word in query_lower for word in job_keywords):
        return 'job_ad'
    
    # Definition queries
    definition_keywords = ['what is', 'define', 'definition', 'meaning', 'explain', 'tell me about']
    if any(word in query_lower for word in definition_keywords):
        return 'definition'
    
    # Market analysis queries
    market_keywords = ['market', 'trend', 'insight', 'analysis', 'outlook', 'forecast', 'prediction', 'credit market', 'bond market']
    if any(word in query_lower for word in market_keywords):
        return 'market_analysis'
    
    # Search queries
    search_keywords = ['search', 'find', 'latest', 'news', 'articles', 'update', 'current', 'recent']
    if any(word in query_lower for word in search_keywords):
        return 'search'
    
    # CV/Resume help
    cv_keywords = ['cv', 'resume', 'format', 'template', 'career advice', 'interview']
    if any(word in query_lower for word in cv_keywords):
        return 'cv_help'
    
    # Conversational queries
    conversation_keywords = ['hello', 'hi', 'how are you', 'help', 'assist', 'can you', 'could you', 'would you']
    if any(word in query_lower for word in conversation_keywords):
        return 'conversation'
    
    return 'general'

def calculate_confidence(query_lower, query_type):
    """Calculate confidence score based on query analysis"""
    base_confidence = 0.8
    
    # Increase confidence for specific keywords
    if query_type == 'job_ad' and any(word in query_lower for word in ['create', 'write', 'generate']):
        return min(0.95, base_confidence + 0.15)
    
    if query_type == 'definition' and any(word in query_lower for word in ['clo', 'cdo', 'credit', 'bond', 'debt']):
        return min(0.95, base_confidence + 0.15)
    
    return base_confidence

def generate_advanced_job_ad(query, conversation_history):
    """Generate sophisticated job advertisements"""
    job_examples = ai_memory.get('ai_learning_job_ad_examples', '')
    
    if job_examples and 'EXAMPLE 1' in job_examples:
        return generate_professional_job_ad(query, job_examples)
    else:
        return generate_basic_job_ad(query)

def generate_advanced_definition(query, conversation_history):
    """Generate comprehensive financial definitions"""
    return get_financial_definition(query)

def generate_market_analysis(query, conversation_history):
    """Generate sophisticated market analysis"""
    # Get recent articles for context
    try:
        articles = get_daily_news_articles() if DAILY_NEWS_AVAILABLE else get_comprehensive_rss_articles()
        recent_articles = articles[:5] if articles else []
        
        analysis = f"""**Advanced Market Analysis**

**Query Context:** {query}

**Current Market Intelligence:**
Based on recent market developments and data analysis:

**Key Market Drivers:**
• Interest rate environment and central bank policy
• Credit spread dynamics and risk appetite
• Sector-specific performance and outlook
• Regulatory developments and compliance requirements

**Recent Developments:**
"""
        
        if recent_articles:
            for i, article in enumerate(recent_articles[:3], 1):
                analysis += f"• {article.get('title', 'Market Development')}\n"
        
        analysis += f"""
**Risk Assessment:**
• Market volatility indicators
• Credit quality trends
• Liquidity conditions
• Geopolitical factors

**Investment Implications:**
• Portfolio positioning recommendations
• Risk management considerations
• Opportunity identification
• Sector allocation guidance

*Analysis based on real-time market data and professional insights.*"""
        
        return analysis
    except Exception as e:
        return f"**Market Analysis**\n\nI'm currently analyzing market conditions. Please try again in a moment for the latest insights.\n\n*Error: {str(e)}*"

def generate_cv_guidance(query, conversation_history):
    """Generate comprehensive CV and career guidance"""
    return f"""**Advanced CV & Career Guidance**

**Your Query:** {query}

**Professional CV Structure:**

**1. Header Section:**
• Name (prominent, professional font)
• Contact details (phone, email, LinkedIn)
• Professional title/headline
• Location (city, country)

**2. Executive Summary:**
• 3-4 sentences highlighting key achievements
• Quantified accomplishments
• Career focus and value proposition
• Tailored to target role

**3. Professional Experience:**
• Reverse chronological order
• Company, position, dates
• 4-6 bullet points per role
• Action verbs (achieved, developed, led, managed)
• Quantified results and impact
• Relevant achievements for target role

**4. Education & Qualifications:**
• Degree, institution, graduation year
• Relevant coursework or honors
• Professional certifications
• Continuing education

**5. Key Skills:**
• Technical skills (credit analysis, financial modeling)
• Soft skills (leadership, communication)
• Industry-specific expertise
• Software proficiency

**6. Additional Sections:**
• Professional achievements
• Publications or thought leadership
• Volunteer work (if relevant)
• Languages (if applicable)

**Advanced Tips:**
• Use keywords from job descriptions
• Quantify achievements with numbers
• Show career progression
• Highlight relevant experience
• Keep to 2 pages maximum
• Use consistent formatting
• Proofread thoroughly

**Interview Preparation:**
• Research the company and role
• Prepare STAR method examples
• Practice common questions
• Prepare thoughtful questions to ask
• Dress professionally
• Arrive early

*This guidance is tailored to credit and financial services roles.*"""

def generate_conversational_response(query, conversation_history):
    """Generate contextual conversational responses"""
    query_lower = query.lower()
    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in query_lower for greeting in greetings):
        return """Hello! I'm your AI assistant specialized in credit industry knowledge, job advertisements, CV guidance, and market analysis. 

How can I help you today? I can:
• Write professional job advertisements
• Explain financial terms and concepts
• Provide market analysis and insights
• Help with CV formatting and career advice
• Search for the latest industry news
• Answer questions about credit markets

What would you like to know?"""
    
    if 'help' in query_lower or 'assist' in query_lower:
        return """I'm here to help with all your credit industry needs! Here's what I can do:

**Job Advertisements:**
• Create professional job postings
• Use industry-specific language
• Follow best practices for recruitment

**Financial Knowledge:**
• Define complex financial terms
• Explain credit instruments (CLOs, CDOs, etc.)
• Provide market insights

**Career Guidance:**
• CV formatting and optimization
• Interview preparation
• Career development advice

**Market Intelligence:**
• Current market trends
• Credit market analysis
• Latest industry news

Just ask me anything related to credit, finance, or your career!"""
    
    return f"""I understand you're asking about: {query}

I'm your specialized AI assistant for the credit industry. I can help with job advertisements, financial definitions, market analysis, CV guidance, and more.

Could you be more specific about what you'd like to know? For example:
• "Write a job ad for a credit analyst"
• "What is a CLO?"
• "Current credit market trends"
• "Help with my CV" """

def generate_general_response(query, conversation_history):
    """Generate intelligent general responses"""
    return f"""**Intelligent Response**

I understand you're asking about: {query}

As your specialized AI assistant for the credit industry, I can provide expert guidance on:

**Financial Knowledge:**
• Credit instruments and structures
• Market analysis and trends
• Regulatory developments
• Risk assessment

**Professional Services:**
• Job advertisement creation
• CV optimization and career advice
• Interview preparation
• Industry insights

**Market Intelligence:**
• Real-time market data
• Sector analysis
• Investment opportunities
• Risk factors

Please let me know specifically what you'd like help with, and I'll provide detailed, professional guidance tailored to your needs."""

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant():
    """AI Assistant endpoint for processing queries using the advanced AI system"""
    try:
        print(f"🧠 AI Assistant request received")
        print(f"🧠 Content-Type: {request.content_type}")
        print(f"🧠 Method: {request.method}")
        
        # Check if this is a multipart request (with attachments)
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            print(f"🧠 Processing as multipart request with attachments")
            return handle_ai_assistant_with_attachments()
        else:
            print(f"🧠 Processing as text-only request")
            return handle_ai_assistant_text_only()
        
    except Exception as e:
        print(f"❌ Error in AI assistant: {e}")
        return jsonify({
            "success": False,
            "error": f"AI processing error: {str(e)}"
        }), 500

def handle_ai_assistant_text_only():
    """Handle text-only AI assistant requests (existing functionality)"""
    try:
        data = request.get_json()
        # Support both 'query' (from iOS app) and 'message' parameters
        message = data.get('query', data.get('message', ''))
        user_id = data.get('chat_id', data.get('user_id', 'hope'))
        
        if not message:
            return jsonify({
                "success": False,
                "error": "No message provided"
            }), 400
        
        print(f"🧠 AI Assistant processing message: {message}")
        print(f"🧠 User ID: {user_id}")
        
        # Prepare context for AI assistant
        context = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Get recent articles for context if available
        try:
            recent_articles = get_recent_articles(limit=10)
            if recent_articles:
                context['articles'] = recent_articles
                print(f"🧠 Added {len(recent_articles)} recent articles to context")
        except Exception as e:
            print(f"🧠 Could not fetch recent articles: {e}")
        
        # Process query using the advanced AI assistant
        ai_response = process_ai_query(message, context)
        
        # Store the interaction in memory system
        store_interaction(message, ai_response['text'], ai_response['type'], ai_response['confidence'])
        
        # Build response (support both iOS and other clients)
        response_payload = {
            "success": True,
            "text": ai_response['text'],  # iOS app expects 'text'
            "response": ai_response['text'],  # Alternative key for compatibility
            "type": ai_response['type'],
            "confidence": ai_response['confidence'],
            "sources": ai_response.get('sources', []),
            "actions": ai_response.get('actions', [])
        }
        
        # If this is a CV formatting response and we only have text containing HTML,
        # expose html_content and a sensible default filename so clients can download/share cleanly
        try:
            if ai_response.get('type') == 'cv_format':
                text_lower = (ai_response.get('text') or '').lower()
                if ('<html' in text_lower) or ('<head' in text_lower) or ('<body' in text_lower):
                    response_payload['html_content'] = ai_response.get('text')
                    response_payload['download_filename'] = 'formatted_cv.html'
        except Exception:
            # Non-fatal; keep base payload
            pass
        
        return jsonify(response_payload)
        
    except Exception as e:
        print(f"❌ Error in text-only AI assistant: {e}")
        return jsonify({
            "success": False,
            "error": f"Text processing error: {str(e)}"
        }), 500

def handle_ai_assistant_with_attachments():
    """Handle AI assistant requests with file attachments"""
    try:
        # Extract form data
        message = request.form.get('query', request.form.get('message', ''))
        user_id = request.form.get('chat_id', request.form.get('user_id', 'hope'))
        
        if not message:
            return jsonify({
                "success": False,
                "error": "No message provided"
            }), 400
        
        print(f"🧠 AI Assistant processing message with attachments: {message}")
        print(f"🧠 User ID: {user_id}")
        
        # Process attachments
        attachments = request.files.getlist('attachments')
        file_analyses = []
        
        if attachments:
            print(f"📎 Processing {len(attachments)} attachments")
            
            for attachment in attachments:
                if attachment.filename:
                    try:
                        # Get file data
                        file_data = attachment.read()
                        filename = attachment.filename
                        mime_type = attachment.content_type or 'application/octet-stream'
                        
                        print(f"📎 Analyzing file: {filename} ({mime_type})")
                        
                        # Analyze the file
                        analysis = file_analyzer.analyze_file(file_data, filename, mime_type)
                        file_analyses.append(analysis)
                        
                        print(f"📎 Analysis complete for {filename}")
                        
                    except Exception as e:
                        print(f"❌ Error processing attachment {attachment.filename}: {e}")
                        file_analyses.append({
                            'type': 'error',
                            'filename': attachment.filename,
                            'error': str(e),
                            'extracted_text': '',
                            'analysis': f'Error processing file: {str(e)}'
                        })
        
        # Prepare enhanced context for AI assistant
        context = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'has_attachments': len(file_analyses) > 0,
            'file_analyses': file_analyses
        }
        
        # Get recent articles for context if available
        try:
            recent_articles = get_recent_articles(limit=10)
            if recent_articles:
                context['articles'] = recent_articles
                print(f"🧠 Added {len(recent_articles)} recent articles to context")
        except Exception as e:
            print(f"🧠 Could not fetch recent articles: {e}")
        
        # Process query with file context using the advanced AI assistant
        ai_response = process_ai_query_with_files(message, context, file_analyses)
        
        # Store the interaction in memory system
        store_interaction(message, ai_response['text'], ai_response['type'], ai_response['confidence'])
        
        # Return response in expected format
        response_data = {
            "success": True,
            "text": ai_response['text'],  # iOS app expects 'text'
            "response": ai_response['text'],  # Alternative key for compatibility
            "type": ai_response['type'],
            "confidence": ai_response['confidence'],
            "sources": ai_response.get('sources', []),
            "actions": ai_response.get('actions', []),
            "attachments_processed": len(file_analyses),
            "file_summaries": [{
                'filename': analysis.get('filename', 'Unknown'),
                'type': analysis.get('type', 'unknown'),
                'has_text': analysis.get('has_text', False),
                'analysis': analysis.get('analysis', '')
            } for analysis in file_analyses]
        }
        
        # Add CV file download info if available
        if ai_response.get('download_url'):
            response_data['download_url'] = ai_response['download_url']
            response_data['download_filename'] = ai_response.get('filename')
            response_data['cv_file'] = ai_response.get('cv_file')
            response_data['html_content'] = ai_response.get('html_content')
            response_data['html_base64'] = ai_response.get('html_base64')
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error in attachment AI assistant: {e}")
        return jsonify({
            "success": False,
            "error": f"Attachment processing error: {str(e)}"
        }), 500

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """AI Chat endpoint for call note transcript summarization"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'system')
        context = data.get('context', {})
        
        if not message:
            return jsonify({
                "success": False,
                "error": "No message provided"
            }), 400
        
        print(f"🎙️ AI Chat processing call transcript: {message[:100]}...")
        print(f"🎙️ User ID: {user_id}")
        
        # Check if this is a call transcript
        is_call_transcript = context.get('type') == 'call_notes' or 'transcript' in message.lower()
        
        if is_call_transcript:
            # Process as call transcript summary
            ai_response = process_call_transcript(message, context)
        else:
            # Process as regular AI query
            ai_response = process_ai_query(message, context)
        
        # Return response in expected format for Call Notes
        return jsonify({
            "success": True,
            "response": ai_response['text'],
            "type": ai_response['type'],
            "confidence": ai_response['confidence'],
            "sources": ai_response.get('sources', []),
            "actions": ai_response.get('actions', [])
        })
        
    except Exception as e:
        print(f"❌ Error in AI chat: {e}")
        return jsonify({
            "success": False,
            "error": f"AI chat error: {str(e)}"
        }), 500

def process_call_transcript(transcript, context):
    """Process call transcript and generate structured summary"""
    try:
        # Generate comprehensive call summary
        summary_prompt = f"""
        Please analyze this call transcript and provide a structured summary:

        TRANSCRIPT:
        {transcript}

        Please provide:
        1. Executive Summary (2-3 sentences)
        2. Key Points (bullet points)
        3. Action Items (bullet points)
        4. Participants (if identifiable)
        5. Meeting Duration/Type (if mentioned)

        Format as a professional meeting summary.
        """
        
        # Use the existing AI processing
        ai_response = process_ai_query(summary_prompt, context)
        
        # Enhance the response for call notes
        enhanced_text = f"""
        **MEETING SUMMARY**
        
        {ai_response['text']}
        
        **TRANSCRIPT LENGTH:** {len(transcript.split())} words
        **GENERATED:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        *This summary was generated using AI analysis of the call transcript.*
        """
        
        return {
            "text": enhanced_text,
            "type": "call_summary",
            "confidence": 0.9,
            "sources": ["call_transcript"],
            "actions": ["copy_to_clipboard", "save_summary"]
        }
        
    except Exception as e:
        print(f"❌ Error processing call transcript: {e}")
        return {
            "text": f"Error processing transcript: {str(e)}",
            "type": "error",
            "confidence": 0.0,
            "sources": [],
            "actions": []
        }

def get_recent_articles(limit=10):
    """Get recent articles for AI context"""
    try:
        # Fetch from comprehensive RSS articles system
        all_articles = get_comprehensive_rss_articles()
        
        if not all_articles:
            print("⚠️ No articles available from RSS feeds")
            return []
        
        # Sort by date and return most recent
        sorted_articles = sorted(
            all_articles, 
            key=lambda x: x.get('publishedAt', x.get('date', '')), 
            reverse=True
        )
        
        recent_articles = sorted_articles[:limit]
        print(f"✅ Fetched {len(recent_articles)} recent articles for AI context")
        
        return recent_articles
    except Exception as e:
        print(f"❌ Error fetching recent articles: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.route('/api/user/profile', methods=['GET'])
def user_profile():
    """User profile management endpoint"""
    try:
        if request.method == 'GET':
            # Get user profile
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'User ID required'
                }), 400
            
            # Check if user profile exists
            profile_key = f"user_profile_{user_id}"
            if profile_key in ai_memory:
                return jsonify({
                    'success': True,
                    'profile': ai_memory[profile_key]
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Profile not found'
                }), 404
        
        elif request.method == 'POST':
            # Create new user profile
            data = request.get_json()
            if not data or 'user_id' not in data:
                return jsonify({
                    'success': False,
                    'error': 'User ID required'
                }), 400
            
            user_id = data['user_id']
            profile_key = f"user_profile_{user_id}"
            
            # Store user profile
            profile_data = {
                'user_id': user_id,
                'name': data.get('name', ''),
                'email': data.get('email', ''),
                'avatar': data.get('avatar', ''),
                'preferences': data.get('preferences', {}),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            ai_memory[profile_key] = profile_data
            
            return jsonify({
                'success': True,
                'message': 'Profile created successfully',
                'profile': profile_data
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user/profile', methods=['POST'])
def create_user_profile():
    """Create user profile endpoint"""
    return user_profile()

def authenticate_user():
    """Authenticate user by checking email in user_profiles"""
    email = request.headers.get('X-User-Email') or request.args.get('email')
    if not email:
        return None, jsonify({
            'success': False,
            'error': 'Authentication required. Please provide user email.'
        }), 401
    
    # Check if user exists in user_profiles
    if email not in user_profiles:
        return None, jsonify({
            'success': False,
            'error': 'Unauthorized. User not found.'
        }), 403
    
    return email, None, None

def check_rate_limit(email, max_requests=10, window_seconds=60):
    """Check rate limiting for compensation endpoint"""
    global compensation_rate_limits
    
    now = datetime.now()
    
    if email not in compensation_rate_limits:
        compensation_rate_limits[email] = {
            'count': 1,
            'reset_time': now + timedelta(seconds=window_seconds)
        }
        return True, (None, None)
    
    rate_data = compensation_rate_limits[email]
    
    # Reset if window expired
    if now > rate_data['reset_time']:
        rate_data['count'] = 1
        rate_data['reset_time'] = now + timedelta(seconds=window_seconds)
        return True, (None, None)
    
    # Check if limit exceeded
    if rate_data['count'] >= max_requests:
        return False, (jsonify({
            'success': False,
            'error': f'Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds.'
        }), 429)
    
    rate_data['count'] += 1
    return True, (None, None)

def validate_compensation(comp):
    """Validate a single compensation entry"""
    errors = []
    
    # Check required fields
    if 'jobTitle' not in comp or not comp['jobTitle']:
        errors.append('jobTitle is required')
    elif len(comp['jobTitle']) > MAX_JOB_TITLE_LENGTH:
        errors.append(f'jobTitle exceeds maximum length of {MAX_JOB_TITLE_LENGTH} characters')
    
    if 'baseSalary' not in comp:
        errors.append('baseSalary is required')
    else:
        try:
            base_salary = float(comp['baseSalary'])
            if base_salary < MIN_COMPENSATION_VALUE or base_salary > MAX_COMPENSATION_VALUE:
                errors.append(f'baseSalary must be between {MIN_COMPENSATION_VALUE} and {MAX_COMPENSATION_VALUE}')
        except (ValueError, TypeError):
            errors.append('baseSalary must be a valid number')
    
    if 'bonus' not in comp:
        errors.append('bonus is required')
    else:
        try:
            bonus = float(comp['bonus'])
            if bonus < MIN_COMPENSATION_VALUE or bonus > MAX_COMPENSATION_VALUE:
                errors.append(f'bonus must be between {MIN_COMPENSATION_VALUE} and {MAX_COMPENSATION_VALUE}')
        except (ValueError, TypeError):
            errors.append('bonus must be a valid number')
    
    # Validate currency
    if 'currency' in comp:
        valid_currencies = ['USD', 'GBP', 'EUR']
        if comp['currency'] not in valid_currencies:
            errors.append(f'currency must be one of: {", ".join(valid_currencies)}')
    
    # Validate person name (optional)
    if 'personName' in comp and comp['personName']:
        if len(comp['personName']) > MAX_PERSON_NAME_LENGTH:
            errors.append(f'personName exceeds maximum length of {MAX_PERSON_NAME_LENGTH} characters')
        # Sanitize person name - remove potentially dangerous characters
        if not re.match(r'^[a-zA-Z0-9\s\-\'\.]+$', comp['personName']):
            errors.append('personName contains invalid characters')
    
    # Validate dates
    if 'addedDate' in comp:
        try:
            datetime.fromisoformat(comp['addedDate'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            errors.append('addedDate must be a valid ISO 8601 date')
    
    return errors

def sanitize_compensation(comp):
    """Sanitize compensation data"""
    sanitized = {}
    
    # Sanitize job title
    if 'jobTitle' in comp:
        sanitized['jobTitle'] = re.sub(r'[<>"\']', '', str(comp['jobTitle'])).strip()[:MAX_JOB_TITLE_LENGTH]
    
    # Sanitize numeric fields
    if 'baseSalary' in comp:
        try:
            sanitized['baseSalary'] = float(comp['baseSalary'])
        except (ValueError, TypeError):
            sanitized['baseSalary'] = 0.0
    
    if 'bonus' in comp:
        try:
            sanitized['bonus'] = float(comp['bonus'])
        except (ValueError, TypeError):
            sanitized['bonus'] = 0.0
    
    # Sanitize currency
    if 'currency' in comp:
        sanitized['currency'] = str(comp['currency']).upper()
        if sanitized['currency'] not in ['USD', 'GBP', 'EUR']:
            sanitized['currency'] = 'USD'
    
    # Sanitize person name
    if 'personName' in comp and comp['personName']:
        sanitized['personName'] = re.sub(r'[<>"\']', '', str(comp['personName'])).strip()[:MAX_PERSON_NAME_LENGTH]
    
    # Preserve other fields
    for key in ['id', 'addedDate', 'createdAt', 'updatedAt', 'workflowData']:
        if key in comp:
            sanitized[key] = comp[key]
    
    return sanitized

@app.route('/api/compensations', methods=['GET', 'POST'])
def compensations_endpoint():
    """Compensation data endpoint - shared across all users with security"""
    global compensations
    
    try:
        # Authentication check
        email, auth_error, auth_status = authenticate_user()
        if auth_error:
            return auth_error, auth_status
        
        # Rate limiting check
        allowed, rate_error = check_rate_limit(email, max_requests=20, window_seconds=60)
        if not allowed:
            error_response, status_code = rate_error
            return error_response, status_code
        
        if request.method == 'GET':
            # Return all compensation data (read-only, no validation needed)
            return jsonify({
                'success': True,
                'compensations': compensations,
                'count': len(compensations)
            })
        
        elif request.method == 'POST':
            # Save compensation data (replace all) - requires validation
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Request body is required'
                }), 400
            
            if 'compensations' not in data:
                return jsonify({
                    'success': False,
                    'error': 'Compensations data required'
                }), 400
            
            comps = data['compensations']
            
            # Validate array
            if not isinstance(comps, list):
                return jsonify({
                    'success': False,
                    'error': 'Compensations must be an array'
                }), 400
            
            # Check size limit
            if len(comps) > MAX_COMPENSATIONS_PER_REQUEST:
                return jsonify({
                    'success': False,
                    'error': f'Maximum {MAX_COMPENSATIONS_PER_REQUEST} compensations allowed per request'
                }), 400
            
            # Validate and sanitize each compensation entry
            validated_comps = []
            all_errors = []
            
            for idx, comp in enumerate(comps):
                if not isinstance(comp, dict):
                    all_errors.append(f'Entry {idx}: Must be an object')
                    continue
                
                errors = validate_compensation(comp)
                if errors:
                    all_errors.extend([f'Entry {idx}: {error}' for error in errors])
                    continue
                
                # Sanitize and add
                sanitized = sanitize_compensation(comp)
                validated_comps.append(sanitized)
            
            if all_errors:
                return jsonify({
                    'success': False,
                    'error': 'Validation errors',
                    'errors': all_errors
                }), 400
            
            # All validations passed - update compensations
            compensations = validated_comps
            
            # Log the update
            print(f"✅ Compensation data updated by {email}: {len(validated_comps)} entries")
            
            return jsonify({
                'success': True,
                'message': f'Saved {len(validated_comps)} compensation entries',
                'count': len(validated_comps)
            })
    
    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'error': 'Invalid JSON in request body'
        }), 400
    except Exception as e:
        print(f"❌ Error in compensations endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/download-cv/<filename>', methods=['GET'])
def download_cv(filename):
    """Download formatted CV file"""
    try:
        import os
        cv_dir = 'generated_cvs'
        
        # Security: Only allow alphanumeric, dots, underscores, and hyphens in filename
        import re
        if not re.match(r'^[\w\-. ]+$', filename):
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400
        
        filepath = os.path.join(cv_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        # Send file with appropriate mimetype
        mimetype = 'text/html' if filename.endswith('.html') else 'application/pdf'
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        print(f"❌ Error downloading CV: {e}")
        return jsonify({
            'success': False,
            'error': f'Download error: {str(e)}'
        }), 500

# MARK: - User-to-User Chat Endpoints

@app.route('/api/user-chats', methods=['GET'])
def get_user_chats():
    """Get all chats for a user"""
    global user_chats
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email parameter is required'
            }), 400
        
        print(f"📥 Fetching chats for user: {email}")
        
        # Get chats for this user, or return empty list
        chats = user_chats.get(email, [])
        
        print(f"✅ Returning {len(chats)} chats for {email}")
        
        return jsonify({
            'success': True,
            'chats': chats
        })
        
    except Exception as e:
        print(f"❌ Error fetching user chats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user-chats', methods=['POST'])
def save_user_chats():
    """Save chats for a user"""
    global user_chats
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        email = data.get('email')
        chats = data.get('chats', [])
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        if not isinstance(chats, list):
            return jsonify({
                'success': False,
                'error': 'Chats must be an array'
            }), 400
        
        print(f"💾 Saving {len(chats)} chats for user: {email}")
        
        # Save chats for this user
        user_chats[email] = chats
        
        print(f"✅ Successfully saved {len(chats)} chats for {email}")
        
        return jsonify({
            'success': True,
            'message': f'Saved {len(chats)} chats'
        })
        
    except Exception as e:
        print(f"❌ Error saving user chats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user-messages', methods=['GET'])
def get_user_messages():
    """Get all messages for a chat"""
    global user_messages
    try:
        chat_id = request.args.get('chat_id')
        if not chat_id:
            return jsonify({
                'success': False,
                'error': 'chat_id parameter is required'
            }), 400
        
        print(f"📥 Fetching messages for chat: {chat_id}")
        
        # Get messages for this chat, or return empty list
        messages = user_messages.get(chat_id, [])
        
        print(f"✅ Returning {len(messages)} messages for chat {chat_id}")
        
        return jsonify({
            'success': True,
            'messages': messages
        })
        
    except Exception as e:
        print(f"❌ Error fetching user messages: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user-messages', methods=['POST'])
def save_user_messages():
    """Save messages for a chat and send push notifications to recipients"""
    global user_messages, user_chats, device_tokens
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        chat_id = data.get('chat_id')
        messages = data.get('messages', [])
        sender_email = data.get('sender_email')  # Email of the person sending the message
        
        if not chat_id:
            return jsonify({
                'success': False,
                'error': 'chat_id is required'
            }), 400
        
        if not isinstance(messages, list):
            return jsonify({
                'success': False,
                'error': 'Messages must be an array'
            }), 400
        
        print(f"💾 Saving {len(messages)} messages for chat: {chat_id}")
        
        # Get previous messages to detect new ones
        previous_messages = user_messages.get(chat_id, [])
        previous_message_ids = {msg.get('id') for msg in previous_messages if isinstance(msg, dict)}
        
        # Save messages for this chat
        user_messages[chat_id] = messages
        
        # Find new messages (ones not in previous set)
        new_messages = [msg for msg in messages if isinstance(msg, dict) and msg.get('id') not in previous_message_ids]
        
        # Find the chat to get participants
        chat = None
        for email, chats in user_chats.items():
            for c in chats:
                if isinstance(c, dict) and c.get('id') == chat_id:
                    chat = c
                    break
            if chat:
                break
        
        # Send push notifications to recipients (participants who aren't the sender)
        if new_messages and chat and sender_email:
            participants = chat.get('participants', [])
            
            # Get sender name from user_profiles
            sender_profile = user_profiles.get(sender_email, {})
            sender_name = sender_profile.get('name', 'Someone')
            
            # Map participant IDs to emails
            # Participants can be either emails or user IDs
            # We need to find all users who have this chat and get their emails
            recipient_emails = []
            for email, user_chat_list in user_chats.items():
                # Check if this user has this chat
                for user_chat in user_chat_list:
                    if isinstance(user_chat, dict) and user_chat.get('id') == chat_id:
                        # This user is a participant, add their email if not the sender
                        if email != sender_email:
                            recipient_emails.append(email)
                        break
            
            # Also check if participants are emails directly
            for participant in participants:
                if isinstance(participant, str):
                    # If it's an email, use it directly
                    if '@' in participant and participant != sender_email:
                        if participant not in recipient_emails:
                            recipient_emails.append(participant)
            
            print(f"📱 Push notification: sender={sender_email}, recipients={recipient_emails}, chat_id={chat_id}")
            
            # Get the last new message for notification
            last_message = new_messages[-1] if new_messages else None
            if last_message:
                message_text = last_message.get('text', 'New message')
                # Truncate long messages
                if len(message_text) > 100:
                    message_text = message_text[:100] + "..."
                
                # Send push notification to each recipient
                for recipient_email in recipient_emails:
                    device_token = device_tokens.get(recipient_email)
                    if device_token:
                        print(f"📤 Attempting to send push notification to {recipient_email}")
                        print(f"   Device token: {device_token[:20]}...")
                        print(f"   Title: 💬 {sender_name}")
                        print(f"   Body: {message_text}")
                        result = send_push_notification(
                            device_token=device_token,
                            title=f"💬 {sender_name}",
                            body=message_text,
                            chat_id=chat_id,
                            message_id=last_message.get('id')
                        )
                        if result:
                            print(f"✅ Push notification sent successfully to {recipient_email}")
                        else:
                            print(f"❌ Failed to send push notification to {recipient_email}")
                    else:
                        print(f"⚠️ No device token found for {recipient_email}")
                        print(f"   Registered tokens: {list(device_tokens.keys())}")
                        print(f"   Total registered devices: {len(device_tokens)}")
            else:
                print(f"⚠️ No new messages to notify about")
        
        print(f"✅ Successfully saved {len(messages)} messages for chat {chat_id}")
        
        return jsonify({
            'success': True,
            'message': f'Saved {len(messages)} messages'
        })
        
    except Exception as e:
        print(f"❌ Error saving user messages: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# MARK: - Push Notifications

def send_push_notification(device_token, title, body, chat_id=None, message_id=None):
    """Send push notification using APNs"""
    try:
        # Get APNs key and team ID from environment variables
        apns_key_id = os.getenv('APNS_KEY_ID')
        apns_team_id = os.getenv('APNS_TEAM_ID')
        apns_key_path = os.getenv('APNS_KEY_PATH')
        apns_topic = os.getenv('APNS_TOPIC', 'MP.MP-APP-V4')  # Your bundle ID
        apns_use_sandbox = os.getenv('APNS_USE_SANDBOX', 'false').lower() == 'true'
        
        print(f"🔍 Checking APNs configuration...")
        print(f"   APNS_KEY_ID: {'✅ Set' if apns_key_id else '❌ Missing'}")
        print(f"   APNS_TEAM_ID: {'✅ Set' if apns_team_id else '❌ Missing'}")
        print(f"   APNS_KEY_PATH: {'✅ Set' if apns_key_path else '❌ Missing'}")
        print(f"   APNS_TOPIC: {apns_topic}")
        print(f"   APNS_USE_SANDBOX: {apns_use_sandbox}")
        
        if not all([apns_key_id, apns_team_id, apns_key_path]):
            print("⚠️ APNs credentials not configured - skipping push notification")
            print("💡 Set APNS_KEY_ID, APNS_TEAM_ID, and APNS_KEY_PATH environment variables on Render")
            return False
        
        # Try to send using PyAPNs2
        try:
            from apns2.client import APNsClient
            from apns2.payload import Payload
            from apns2.credentials import TokenCredentials
            
            print(f"📂 Reading APNs key from: {apns_key_path}")
            
            # Check if key file exists
            import os
            if not os.path.exists(apns_key_path):
                print(f"❌ APNs key file not found at: {apns_key_path}")
                print(f"   Current working directory: {os.getcwd()}")
                print(f"   Files in current directory: {os.listdir('.')}")
                return False
            
            # Create credentials from key file
            with open(apns_key_path, 'r') as f:
                key_content = f.read()
                print(f"✅ Read APNs key file ({len(key_content)} bytes)")
            
            credentials = TokenCredentials(
                auth_key_path=apns_key_path,
                auth_key_id=apns_key_id,
                team_id=apns_team_id
            )
            
            print(f"🔐 Created APNs credentials")
            
            # Create APNs client
            client = APNsClient(
                credentials=credentials,
                use_sandbox=apns_use_sandbox,
                use_alternative_port=False
            )
            
            print(f"📱 Created APNs client (sandbox: {apns_use_sandbox})")
            
            # Create payload
            payload = Payload(
                alert={"title": title, "body": body},
                sound="default",
                badge=1,
                custom={"chat_id": chat_id, "message_id": message_id} if chat_id else {}
            )
            
            print(f"📦 Created payload: title='{title}', body='{body[:50]}...'")
            
            # Send notification (PyAPNs2 send_notification is fire-and-forget)
            print(f"🚀 Sending push notification to device token: {device_token[:20]}...")
            try:
                client.send_notification(device_token, payload, topic=apns_topic)
                print(f"✅ Push notification sent successfully!")
                return True
            except Exception as send_error:
                print(f"❌ Error sending notification: {send_error}")
                import traceback
                traceback.print_exc()
                return False
            
        except ImportError as import_error:
            print(f"❌ PyAPNs2 not installed: {import_error}")
            print(f"💡 Install with: pip install PyAPNs2")
            print(f"📱 Would send push notification:")
            print(f"   Device Token: {device_token[:20]}...")
            print(f"   Title: {title}")
            print(f"   Body: {body}")
            print(f"   Chat ID: {chat_id}")
            return False
        except Exception as apns_error:
            print(f"❌ APNs error: {apns_error}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Error sending push notification: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/api/test-push-notification', methods=['POST'])
def test_push_notification():
    """Test endpoint to send a push notification"""
    global device_tokens
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        email = data.get('email')
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        device_token = device_tokens.get(email)
        if not device_token:
            return jsonify({
                'success': False,
                'error': f'No device token found for {email}. Registered emails: {list(device_tokens.keys())}'
            }), 400
        
        title = data.get('title', 'Test Notification')
        body = data.get('body', 'This is a test push notification')
        
        result = send_push_notification(
            device_token=device_token,
            title=title,
            body=body,
            chat_id=None,
            message_id=None
        )
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Test push notification sent'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send push notification (check server logs)'
            }), 500
        
    except Exception as e:
        print(f"❌ Error in test push notification: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/register-device-token', methods=['POST'])
def register_device_token():
    """Register a device token for push notifications"""
    global device_tokens
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        email = data.get('email')
        device_token = data.get('device_token')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        if not device_token:
            return jsonify({
                'success': False,
                'error': 'Device token is required'
            }), 400
        
        # Store device token for this user
        device_tokens[email] = device_token
        
        print(f"✅ Registered device token for {email}")
        print(f"   Token: {device_token[:20]}...{device_token[-10:]}")
        print(f"   Total registered devices: {len(device_tokens)}")
        print(f"   All registered emails: {list(device_tokens.keys())}")
        
        return jsonify({
            'success': True,
            'message': 'Device token registered'
        })
        
    except Exception as e:
        print(f"❌ Error registering device token: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# MARK: - Call Notes Endpoints

@app.route('/api/user-call-notes', methods=['GET'])
def get_user_call_notes():
    """Get all call notes for a user"""
    global user_call_notes
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email parameter is required'
            }), 400
        
        print(f"📥 Fetching call notes for user: {email}")
        
        # Get call notes for this user, or return empty list
        call_notes = user_call_notes.get(email, [])
        
        print(f"✅ Returning {len(call_notes)} call notes for {email}")
        
        return jsonify({
            'success': True,
            'call_notes': call_notes
        })
        
    except Exception as e:
        print(f"❌ Error fetching user call notes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user-call-notes', methods=['POST'])
def save_user_call_notes():
    """Save call notes for a user"""
    global user_call_notes
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        email = data.get('email')
        call_notes = data.get('call_notes', [])
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        if not isinstance(call_notes, list):
            return jsonify({
                'success': False,
                'error': 'Call notes must be an array'
            }), 400
        
        print(f"💾 Saving {len(call_notes)} call notes for user: {email}")
        
        # Save call notes for this user
        user_call_notes[email] = call_notes
        
        print(f"✅ Successfully saved {len(call_notes)} call notes for {email}")
        
        return jsonify({
            'success': True,
            'message': f'Saved {len(call_notes)} call notes'
        })
        
    except Exception as e:
        print(f"❌ Error saving user call notes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/share-call-note', methods=['POST'])
def share_call_note():
    """Share a call note with specific users"""
    global user_call_notes
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        call_note = data.get('call_note')
        user_emails = data.get('user_emails', [])
        
        if not call_note:
            return jsonify({
                'success': False,
                'error': 'Call note is required'
            }), 400
        
        if not isinstance(user_emails, list) or len(user_emails) == 0:
            return jsonify({
                'success': False,
                'error': 'At least one user email is required'
            }), 400
        
        print(f"📤 Sharing call note '{call_note.get('title', 'Unknown')}' with {len(user_emails)} users")
        
        # Add call note to each user's list
        shared_count = 0
        for user_email in user_emails:
            if user_email not in user_call_notes:
                user_call_notes[user_email] = []
            
            # Check if call note already exists (by ID)
            call_note_id = call_note.get('id')
            if call_note_id and not any(note.get('id') == call_note_id for note in user_call_notes[user_email]):
                user_call_notes[user_email].append(call_note)
                shared_count += 1
                print(f"✅ Added call note to {user_email}'s list")
            else:
                print(f"ℹ️ Call note already exists for {user_email}")
        
        return jsonify({
            'success': True,
            'message': f'Shared call note with {shared_count} user(s)',
            'shared_count': shared_count
        })
        
    except Exception as e:
        print(f"❌ Error sharing call note: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# MARK: - Todo Endpoints

@app.route('/api/user-todos', methods=['GET'])
def get_user_todos():
    """Get all todos for a user"""
    global user_todos
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email parameter is required'
            }), 400
        
        print(f"📥 Fetching todos for user: {email}")
        
        # Get todos for this user, or return empty list
        todos = user_todos.get(email, [])
        
        print(f"✅ Returning {len(todos)} todos for {email}")
        
        return jsonify({
            'success': True,
            'todos': todos
        })
        
    except Exception as e:
        print(f"❌ Error fetching user todos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user-todos', methods=['POST'])
def save_user_todos():
    """Save todos for a user"""
    global user_todos
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        email = data.get('email')
        todos = data.get('todos', [])
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        if not isinstance(todos, list):
            return jsonify({
                'success': False,
                'error': 'Todos must be an array'
            }), 400
        
        print(f"💾 Saving {len(todos)} todos for user: {email}")
        
        # Save todos for this user
        user_todos[email] = todos
        
        print(f"✅ Successfully saved {len(todos)} todos for {email}")
        
        return jsonify({
            'success': True,
            'message': f'Saved {len(todos)} todos'
        })
        
    except Exception as e:
        print(f"❌ Error saving user todos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/assign-task', methods=['POST'])
def assign_task():
    """Assign a task to specific users (similar to sharing call notes)"""
    global user_todos
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        task = data.get('task')
        user_emails = data.get('user_emails', [])
        assigner_email = data.get('assigner_email')  # Email of person assigning the task
        
        if not task:
            return jsonify({
                'success': False,
                'error': 'Task is required'
            }), 400
        
        if not isinstance(user_emails, list) or len(user_emails) == 0:
            return jsonify({
                'success': False,
                'error': 'At least one user email is required'
            }), 400
        
        print(f"📤 Assigning task '{task.get('title', 'Unknown')}' to {len(user_emails)} users")
        
        # Map user IDs to emails for assignment
        # The task has assignedTo as user ID, but we need to find the email
        assigned_to_user_id = task.get('assignedTo')
        
        # Map assigner email to user ID
        email_to_id = {
            'hg@mawneypartners.com': 'user_hope',
            'jt@mawneypartners.com': 'user_josh',
            'finance@mawneypartners.com': 'user_rachel',
            'jd@mawneypartners.com': 'user_jack',
            'he@mawneypartners.com': 'user_harry',
            'tjt@mawneypartners.com': 'user_tyler'
        }
        assigner_id = email_to_id.get(assigner_email)
        task_id = task.get('id')
        
        # Remove task from assigner's list (if it exists there)
        if assigner_email in user_todos and task_id:
            user_todos[assigner_email] = [
                t for t in user_todos[assigner_email] 
                if t.get('id') != task_id
            ]
            print(f"✅ Removed task from assigner's ({assigner_email}) list")
        
        # Add task to each recipient's list
        assigned_count = 0
        for user_email in user_emails:
            if user_email not in user_todos:
                user_todos[user_email] = []
            
            # Check if task already exists (by ID)
            if task_id and not any(t.get('id') == task_id for t in user_todos[user_email]):
                # Find user ID from email
                user_id = email_to_id.get(user_email)
                
                # Create a copy of the task with updated assignment
                assigned_task = task.copy()
                if user_id:
                    assigned_task['assignedTo'] = user_id
                if assigner_id:
                    assigned_task['assignedBy'] = assigner_id
                
                user_todos[user_email].append(assigned_task)
                assigned_count += 1
                print(f"✅ Added task to {user_email}'s list (assignedTo: {user_id})")
            else:
                print(f"ℹ️ Task already exists for {user_email}")
        
        return jsonify({
            'success': True,
            'message': f'Assigned task to {assigned_count} user(s)',
            'assigned_count': assigned_count
        })
        
    except Exception as e:
        print(f"❌ Error assigning task: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Force restart to pick up new template and text parsing fixes
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 Starting Mawney Partners API with AI Assistant on port {port}")
    print("🧠 AI Assistant system loaded with advanced capabilities...")
    print("📝 Text parsing fixes deployed - strategic line breaks for CV structure")
    print("📄 Template pagination fixes deployed - improved margins and spacing")
    print("🎨 Logo fixes deployed - top MP logo and bottom MAWNEY Partners logo")
    app.run(host='0.0.0.0', port=port, debug=False)
