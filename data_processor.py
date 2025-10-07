import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict

class DataProcessor:
    """Process and analyze collected data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = "data"
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_raw_data(self, data: Dict[str, List[Dict]], filename: str = None):
        """Save raw collected data to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"raw_data_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Raw data saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving raw data: {str(e)}")
    
    def load_historical_data(self, days: int = 7) -> List[Dict]:
        """Load historical data from the last N days"""
        historical_data = []
        
        try:
            for filename in os.listdir(self.data_dir):
                if filename.startswith('raw_data_') and filename.endswith('.json'):
                    filepath = os.path.join(self.data_dir, filename)
                    
                    # Check if file is within the specified time range
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time >= datetime.now() - timedelta(days=days):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            historical_data.append(data)
            
            self.logger.info(f"Loaded {len(historical_data)} historical data files")
        except Exception as e:
            self.logger.error(f"Error loading historical data: {str(e)}")
        
        return historical_data
    
    def deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity and content"""
        unique_articles = []
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            content = article.get('content', '').lower().strip()
            source = article.get('source', '')
            
            # Skip if we've seen a very similar article
            is_duplicate = False
            for seen in unique_articles:
                seen_title = seen.get('title', '').lower().strip()
                seen_content = seen.get('content', '').lower().strip()
                seen_source = seen.get('source', '')
                
                # Check for exact title match
                if title == seen_title:
                    is_duplicate = True
                    break
                
                # Check for very similar titles (85%+ similarity)
                if self._calculate_similarity(title, seen_title) > 0.85:
                    is_duplicate = True
                    # Keep the one with higher relevance score
                    if article.get('relevance_score', 0) > seen.get('relevance_score', 0):
                        unique_articles.remove(seen)
                        unique_articles.append(article)
                    break
                
                # Check for same source and very similar content
                if source == seen_source and self._calculate_similarity(content, seen_content) > 0.9:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
        
        self.logger.info(f"Deduplicated {len(articles)} articles to {len(unique_articles)}")
        return unique_articles
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using Jaccard similarity"""
        if not text1 or not text2:
            return 0.0
        
        # Convert to sets of words
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def categorize_market_moves(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize market moves articles by type"""
        categories = {
            'credit_ratings': [],
            'bond_issuance': [],
            'defaults_bankruptcies': [],
            'market_analysis': [],
            'regulatory_changes': [],
            'other': []
        }
        
        for article in articles:
            title_lower = article['title'].lower()
            
            # Credit ratings
            if any(keyword in title_lower for keyword in ['rating', 'downgrade', 'upgrade', 's&p', 'moody', 'fitch']):
                categories['credit_ratings'].append(article)
            # Bond issuance
            elif any(keyword in title_lower for keyword in ['issuance', 'bond offering', 'debt sale', 'refinancing']):
                categories['bond_issuance'].append(article)
            # Defaults and bankruptcies
            elif any(keyword in title_lower for keyword in ['default', 'bankruptcy', 'restructuring', 'distressed']):
                categories['defaults_bankruptcies'].append(article)
            # Market analysis
            elif any(keyword in title_lower for keyword in ['analysis', 'outlook', 'forecast', 'trend']):
                categories['market_analysis'].append(article)
            # Regulatory changes
            elif any(keyword in title_lower for keyword in ['regulation', 'regulatory', 'policy', 'fed', 'ecb']):
                categories['regulatory_changes'].append(article)
            else:
                categories['other'].append(article)
        
        return categories
    
    def categorize_people_moves(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize people moves articles by seniority and function"""
        categories = {
            'c_suite': [],
            'directors': [],
            'managers': [],
            'analysts': [],
            'other': []
        }
        
        for article in articles:
            title_lower = article['title'].lower()
            
            # C-Suite
            if any(keyword in title_lower for keyword in ['ceo', 'cfo', 'chief', 'president', 'chairman']):
                categories['c_suite'].append(article)
            # Directors
            elif any(keyword in title_lower for keyword in ['director', 'head of', 'vice president', 'vp']):
                categories['directors'].append(article)
            # Managers
            elif any(keyword in title_lower for keyword in ['manager', 'senior', 'principal']):
                categories['managers'].append(article)
            # Analysts
            elif any(keyword in title_lower for keyword in ['analyst', 'associate']):
                categories['analysts'].append(article)
            else:
                categories['other'].append(article)
        
        return categories
    
    def generate_summary_statistics(self, data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate summary statistics for the collected data"""
        stats = {
            'total_articles': 0,
            'market_moves': {
                'count': len(data.get('market_moves', [])),
                'sources': defaultdict(int)
            },
            'people_moves': {
                'count': len(data.get('people_moves', [])),
                'sources': defaultdict(int)
            },
            'collection_time': data.get('collection_time', 'Unknown')
        }
        
        # Count articles by source
        for article in data.get('market_moves', []):
            stats['market_moves']['sources'][article.get('source', 'Unknown')] += 1
        
        for article in data.get('people_moves', []):
            stats['people_moves']['sources'][article.get('source', 'Unknown')] += 1
        
        stats['total_articles'] = stats['market_moves']['count'] + stats['people_moves']['count']
        
        return stats
    
    def identify_trending_topics(self, historical_data: List[Dict]) -> Dict[str, List[str]]:
        """Identify trending topics based on historical data"""
        word_counts = defaultdict(int)
        all_titles = []
        
        # Collect all titles from historical data
        for data in historical_data:
            for category in ['market_moves', 'people_moves']:
                for article in data.get(category, []):
                    all_titles.append(article.get('title', '').lower())
        
        # Count word frequencies (excluding common words)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        for title in all_titles:
            words = title.split()
            for word in words:
                # Clean word (remove punctuation)
                clean_word = ''.join(c for c in word if c.isalnum())
                if len(clean_word) > 3 and clean_word not in common_words:
                    word_counts[clean_word] += 1
        
        # Get top trending words
        trending_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'trending_words': [word for word, count in trending_words],
            'word_counts': dict(trending_words)
        }
    
    def process_data(self, raw_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Main data processing pipeline"""
        self.logger.info("Starting data processing...")
        
        # Save raw data
        self.save_raw_data(raw_data)
        
        # Deduplicate articles
        processed_data = {}
        processed_data['market_moves'] = self.deduplicate_articles(raw_data.get('market_moves', []))
        processed_data['people_moves'] = self.deduplicate_articles(raw_data.get('people_moves', []))
        processed_data['collection_time'] = raw_data.get('collection_time')
        
        # Categorize articles
        processed_data['market_categories'] = self.categorize_market_moves(processed_data['market_moves'])
        processed_data['people_categories'] = self.categorize_people_moves(processed_data['people_moves'])
        
        # Generate statistics
        processed_data['statistics'] = self.generate_summary_statistics(processed_data)
        
        # Identify trending topics
        historical_data = self.load_historical_data(days=7)
        processed_data['trending_topics'] = self.identify_trending_topics(historical_data)
        
        self.logger.info("Data processing completed")
        return processed_data



