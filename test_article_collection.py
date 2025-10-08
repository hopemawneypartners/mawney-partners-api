#!/usr/bin/env python3
"""
Test script for article monitoring system
"""

import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required imports work"""
    try:
        import feedparser
        logger.info("✅ feedparser imported successfully")
        
        from data_collector import DataCollector
        logger.info("✅ DataCollector imported successfully")
        
        from data_processor import DataProcessor
        logger.info("✅ DataProcessor imported successfully")
        
        from config import Config
        logger.info("✅ Config imported successfully")
        
        return True
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False

def test_rss_feed_parsing():
    """Test RSS feed parsing"""
    try:
        import feedparser
        
        # Test with a known working RSS feed
        test_url = "https://www.ft.com/rss/markets"
        logger.info(f"Testing RSS feed: {test_url}")
        
        feed = feedparser.parse(test_url)
        
        if hasattr(feed, 'bozo') and feed.bozo:
            logger.warning(f"⚠️ RSS feed has parsing issues (bozo flag set)")
            if hasattr(feed, 'bozo_exception'):
                logger.warning(f"Bozo exception: {feed.bozo_exception}")
        
        if not hasattr(feed, 'entries') or not feed.entries:
            logger.error("❌ No entries found in RSS feed")
            return False
        
        logger.info(f"✅ RSS feed parsed successfully: {len(feed.entries)} entries found")
        
        # Test first entry
        if feed.entries:
            entry = feed.entries[0]
            logger.info(f"Sample entry title: {entry.get('title', 'No title')[:50]}...")
            logger.info(f"Sample entry link: {entry.get('link', 'No link')[:50]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ RSS feed parsing error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_collector():
    """Test DataCollector functionality"""
    try:
        from data_collector import DataCollector
        from config import Config
        
        logger.info("Initializing DataCollector...")
        collector = DataCollector()
        
        # Test RSS feed scraping with a single feed
        test_feed = Config.RSS_FEEDS['market_moves'][0]
        logger.info(f"Testing with feed: {test_feed['name']}")
        
        articles = collector.scrape_rss_feed(test_feed['url'], test_feed['name'])
        
        if articles:
            logger.info(f"✅ DataCollector test passed: {len(articles)} articles collected")
            logger.info(f"Sample article: {articles[0].get('title', 'No title')[:50]}...")
            return True
        else:
            logger.warning("⚠️ No articles collected from test feed")
            return False
            
    except Exception as e:
        logger.error(f"❌ DataCollector test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_article_filtering():
    """Test article filtering logic"""
    try:
        from data_collector import DataCollector
        from config import Config
        
        logger.info("Testing article filtering...")
        collector = DataCollector()
        
        # Test articles
        test_articles = [
            {
                'title': 'Blackstone Launches New Private Credit Fund',
                'link': 'https://example.com/1',
                'source': 'Test Source',
                'timestamp': datetime.now().isoformat()
            },
            {
                'title': 'New Restaurant Opens in London',
                'link': 'https://example.com/2',
                'source': 'Test Source',
                'timestamp': datetime.now().isoformat()
            },
            {
                'title': 'CLO Market Shows Strong Growth',
                'link': 'https://example.com/3',
                'source': 'Test Source',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        filtered = collector.filter_articles(test_articles, Config.MARKET_KEYWORDS)
        
        logger.info(f"Filtered {len(test_articles)} articles to {len(filtered)}")
        
        # Should keep credit-related articles and filter out non-credit
        if len(filtered) >= 2:  # Should keep articles 1 and 3
            logger.info("✅ Article filtering test passed")
            for article in filtered:
                logger.info(f"Kept: {article['title']}")
            return True
        else:
            logger.error(f"❌ Article filtering test failed: expected at least 2 articles, got {len(filtered)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Article filtering test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_processor():
    """Test DataProcessor functionality"""
    try:
        from data_processor import DataProcessor
        
        logger.info("Testing DataProcessor...")
        processor = DataProcessor()
        
        # Test with sample data
        test_data = {
            'market_moves': [
                {
                    'title': 'Test Article 1',
                    'link': 'https://example.com/1',
                    'source': 'Test Source',
                    'relevance_score': 5
                },
                {
                    'title': 'Test Article 1',  # Duplicate
                    'link': 'https://example.com/1',
                    'source': 'Test Source',
                    'relevance_score': 5
                }
            ],
            'people_moves': [],
            'collection_time': datetime.now().isoformat()
        }
        
        # Test deduplication
        deduplicated = processor.deduplicate_articles(test_data['market_moves'])
        
        if len(deduplicated) == 1:
            logger.info("✅ DataProcessor deduplication test passed")
            return True
        else:
            logger.error(f"❌ DataProcessor deduplication test failed: expected 1 article, got {len(deduplicated)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ DataProcessor test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("ARTICLE MONITORING SYSTEM TEST SUITE")
    logger.info("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("RSS Feed Parsing", test_rss_feed_parsing),
        ("Data Collector", test_data_collector),
        ("Article Filtering", test_article_filtering),
        ("Data Processor", test_data_processor)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info("")
        logger.info(f"Running test: {test_name}")
        logger.info("-" * 60)
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info("")
    logger.info(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error(f"⚠️ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())


