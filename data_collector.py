import requests
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from typing import List, Dict, Optional
from config import Config
import feedparser

class DataCollector:
    """Main class for collecting data from various sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def setup_selenium_driver(self) -> webdriver.Chrome:
        """Setup Selenium Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={self.ua.random}')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver
    
    def login_to_source(self, driver: webdriver.Chrome, source: Dict) -> bool:
        """Login to a specific source if credentials are provided"""
        try:
            if not source.get('username') or not source.get('password'):
                self.logger.info(f"No credentials provided for {source['name']}")
                return True
                
            driver.get(source['url'])
            time.sleep(3)
            
            # For FT, navigate directly to the login page
            if 'ft.com' in source['url']:
                try:
                    driver.get('https://www.ft.com/login')
                    time.sleep(3)  # Wait for login page to load
                    self.logger.info("Navigated to FT login page")
                except Exception as e:
                    self.logger.warning(f"Could not navigate to FT login page: {str(e)}")
            
            # Try multiple common login field selectors
            username_selectors = [
                "input[name='email']",  # FT uses this
                "input[name='username']",
                "input[name='login']",
                "input[name='Email address']",  # FT specific
                "input[type='email']",
                "input[placeholder*='email']",
                "input[placeholder*='username']",
                "input[placeholder*='Email address']",  # FT specific
                "input[id*='email']",
                "input[id*='username']",
                "input[id*='login']",
                "input[id*='Email']"  # FT specific
            ]
            
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[placeholder*='password']",
                "input[id*='password']"
            ]
            
            username_field = None
            password_field = None
            
            # Try to find username field
            for selector in username_selectors:
                try:
                    username_field = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    self.logger.info(f"Found username field with selector: {selector}")
                    break
                except:
                    continue
            
            if not username_field:
                self.logger.error(f"Could not find username field for {source['name']}")
                return False
            
            # Try to find password field
            for selector in password_selectors:
                try:
                    password_field = driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found password field with selector: {selector}")
                    break
                except:
                    continue
            
            if not password_field:
                self.logger.error(f"Could not find password field for {source['name']}")
                return False
            
            # Fill in credentials
            username_field.clear()
            username_field.send_keys(source['username'])
            password_field.clear()
            password_field.send_keys(source['password'])
            
            # Try multiple submit button selectors
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Sign in')",
                "button:contains('Login')",
                "button:contains('Log in')",
                "button:contains('Submit')",
                ".login-button",
                ".submit-button",
                "#login-button",
                "#submit-button"
            ]
            
            login_button = None
            for selector in submit_selectors:
                try:
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found submit button with selector: {selector}")
                    break
                except:
                    continue
            
            if login_button:
                login_button.click()
            else:
                # Try pressing Enter on password field
                password_field.send_keys(Keys.RETURN)
            
            time.sleep(5)  # Wait for login to process
            
            # Check if login was successful by looking for logout button or user menu
            try:
                # Look for signs of successful login
                logout_indicators = [
                    "a[href*='logout']",
                    "button:contains('Logout')",
                    "button:contains('Sign out')",
                    ".user-menu",
                    ".account-menu",
                    "[data-testid*='user']",
                    "[data-testid*='account']"
                ]
                
                for indicator in logout_indicators:
                    try:
                        driver.find_element(By.CSS_SELECTOR, indicator)
                        self.logger.info(f"Successfully logged into {source['name']}")
                        return True
                    except:
                        continue
                
                # If no logout indicators found, assume login failed
                self.logger.warning(f"Login to {source['name']} may have failed - no logout indicators found")
                return False
                
            except Exception as e:
                self.logger.error(f"Error checking login status for {source['name']}: {str(e)}")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to login to {source['name']}: {str(e)}")
            return False
    
    def scrape_with_requests(self, url: str, selectors: Dict, source_name: str = 'Unknown') -> List[Dict]:
        """Scrape data using requests and BeautifulSoup"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Extract headlines with their parent containers to find associated links
            headlines = soup.select(selectors.get('headlines', 'h1, h2, h3'))
            
            for headline in headlines[:10]:  # Limit to 10 articles
                title = headline.get_text(strip=True)
                
                # Skip navigation items
                if any(nav_word in title.lower() for nav_word in ['browse', 'menu', 'navigation', 'nav']):
                    continue
                
                article = {
                    'title': title,
                    'link': '',
                    'timestamp': '',
                    'source': source_name
                }
                
                # Try to find the link associated with this headline
                # First, check if the headline itself is a link
                if headline.name == 'a' and headline.get('href'):
                    article['link'] = headline['href']
                else:
                    # Look for a link in the same container as the headline
                    parent = headline.parent
                    if parent:
                        # Look for links in the parent container
                        link_elem = parent.find('a')
                        if link_elem and link_elem.get('href'):
                            article['link'] = link_elem['href']
                        else:
                            # Look in the grandparent container
                            grandparent = parent.parent
                            if grandparent:
                                link_elem = grandparent.find('a')
                                if link_elem and link_elem.get('href'):
                                    article['link'] = link_elem['href']
                
                # For FT, prioritize content links over stream/section links
                if 'ft.com' in url and article['link']:
                    # Look for better FT content links in the same container
                    parent = headline.parent
                    if parent:
                        # Look for content links specifically
                        content_links = parent.find_all('a', href=lambda x: x and '/content/' in x)
                        if content_links:
                            article['link'] = content_links[0]['href']
                
                # Make sure the link is absolute
                if article['link'] and not article['link'].startswith('http'):
                    if article['link'].startswith('/'):
                        article['link'] = url.rstrip('/') + article['link']
                    else:
                        article['link'] = url.rstrip('/') + '/' + article['link']
                
                # Try to find timestamp in the same container
                parent = headline.parent
                if parent:
                    timestamp_elem = parent.find('time') or parent.find(class_=lambda x: x and 'time' in x.lower()) if parent else None
                    if timestamp_elem:
                        article['timestamp'] = timestamp_elem.get_text(strip=True)
                
                articles.append(article)
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return []
    
    def scrape_rss_feed(self, feed_url: str, source_name: str) -> List[Dict]:
        """Scrape data from RSS feeds"""
        try:
            self.logger.info(f"Scraping RSS feed: {feed_url}")
            
            # Parse the RSS feed
            feed = feedparser.parse(feed_url)
            articles = []
            
            # Get current date and yesterday for filtering
            from datetime import datetime, timedelta
            now = datetime.now()
            yesterday = now - timedelta(days=1)
            
            for entry in feed.entries[:15]:  # Check more articles to find recent ones
                article = {
                    'title': entry.get('title', '').strip(),
                    'link': entry.get('link', ''),
                    'timestamp': '',
                    'source': source_name,
                    'relevance_score': 1
                }
                
                # Try to get timestamp
                entry_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    entry_date = datetime(*entry.published_parsed[:6])
                    article['timestamp'] = entry.published
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    entry_date = datetime(*entry.updated_parsed[:6])
                    article['timestamp'] = entry.updated
                elif hasattr(entry, 'published'):
                    article['timestamp'] = entry.published
                elif hasattr(entry, 'updated'):
                    article['timestamp'] = entry.updated
                
                # Filter for recent articles (last 2 days to be safe)
                is_recent = True
                if entry_date:
                    days_old = (now - entry_date).days
                    is_recent = days_old <= 2
                    if days_old > 7:  # Skip very old articles
                        continue
                
                # Only add articles with titles, links, and recent dates
                if article['title'] and article['link'] and is_recent:
                    articles.append(article)
            
            # Sort by date (most recent first) and limit to 10
            articles.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            articles = articles[:10]
            
            self.logger.info(f"Found {len(articles)} recent articles from RSS feed")
            return articles
            
        except Exception as e:
            self.logger.error(f"Error scraping RSS feed {feed_url}: {str(e)}")
            return []
    
    def _is_valid_link(self, url: str) -> bool:
        """Check if a URL is valid and accessible"""
        if not url or not url.startswith('http'):
            return False
        
        # Skip obviously problematic domains
        problematic_domains = [
            'example.com',
            'localhost',
            'test.com'
        ]
        
        for domain in problematic_domains:
            if domain in url:
                return False
        
        # Skip problematic FT link patterns
        if 'ft.com' in url:
            # Skip FT stream URLs and section pages that don't work as public links
            if '/stream/' in url or '/markets/' in url:
                return False
        
        # Skip problematic Reuters link patterns
        if 'reuters.com' in url:
            # Skip Reuters section pages and non-article URLs
            if '/business/' in url and not any(pattern in url for pattern in ['/article/', '/news/', '/world/', '/finance/', '/cenbank-']):
                return False
        
        # Basic URL validation
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if not parsed.netloc or not parsed.scheme:
                return False
        except:
            return False
        
        # Test actual accessibility for known problematic domains
        if 'ft.com' in url or 'reuters.com' in url:
            try:
                response = self.session.head(url, timeout=10, allow_redirects=True)
                # Reject links that return 404 or 401 errors
                if response.status_code in [404, 401]:
                    self.logger.debug(f"Rejecting {url} - HTTP {response.status_code}")
                    return False
                # Accept links that return 200 or other success codes
                elif response.status_code < 400:
                    return True
                else:
                    self.logger.debug(f"Rejecting {url} - HTTP {response.status_code}")
                    return False
            except Exception as e:
                self.logger.debug(f"Could not test {url}: {str(e)}")
                # If we can't test, fall back to basic validation
                return True
        
        return True
    
    def scrape_with_selenium(self, source: Dict) -> List[Dict]:
        """Scrape data using Selenium for JavaScript-heavy sites"""
        driver = None
        try:
            driver = self.setup_selenium_driver()
            
            # Login if credentials provided
            if not self.login_to_source(driver, source):
                return []
            
            driver.get(source['url'])
            time.sleep(5)  # Wait for page to load
            
            articles = []
            selectors = source.get('selectors', {})
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract headlines
            headlines = driver.find_elements(By.CSS_SELECTOR, selectors.get('headlines', 'h1, h2, h3'))
            
            for i, headline in enumerate(headlines[:10]):  # Limit to 10 articles
                try:
                    article = {
                        'title': headline.text.strip(),
                        'link': '',
                        'timestamp': '',
                        'source': source['name']
                    }
                    
                    # Try to find corresponding link
                    # First check if the headline itself is a link
                    try:
                        if headline.tag_name == 'a':
                            article['link'] = headline.get_attribute('href')
                        else:
                            # Look for a link in the parent container
                            parent = headline.find_element(By.XPATH, './..')
                            try:
                                link_elem = parent.find_element(By.CSS_SELECTOR, 'a')
                                article['link'] = link_elem.get_attribute('href')
                            except:
                                # Try grandparent container
                                try:
                                    grandparent = parent.find_element(By.XPATH, './..')
                                    link_elem = grandparent.find_element(By.CSS_SELECTOR, 'a')
                                    article['link'] = link_elem.get_attribute('href')
                                except:
                                    pass
                        
                        # For FT, prioritize content links over stream/section links
                        if 'ft.com' in source['url'] and article['link']:
                            try:
                                parent = headline.find_element(By.XPATH, './..')
                                # Look for content links specifically
                                content_links = parent.find_elements(By.CSS_SELECTOR, 'a[href*="/content/"]')
                                if content_links:
                                    article['link'] = content_links[0].get_attribute('href')
                            except:
                                pass
                                
                    except Exception as e:
                        self.logger.warning(f"Error finding link for article {i}: {str(e)}")
                    
                    # Try to find timestamp
                    try:
                        parent = headline.find_element(By.XPATH, './..')
                        timestamp_selectors = selectors.get('timestamps', 'time, .timestamp, .date')
                        for selector in timestamp_selectors.split(', '):
                            try:
                                timestamp_elem = parent.find_element(By.CSS_SELECTOR, selector)
                                article['timestamp'] = timestamp_elem.text.strip()
                                break
                            except:
                                continue
                    except Exception as e:
                        self.logger.warning(f"Error finding timestamp for article {i}: {str(e)}")
                    
                    articles.append(article)
                    
                except Exception as e:
                    self.logger.warning(f"Error extracting article {i}: {str(e)}")
                    continue
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error with Selenium scraping {source['name']}: {str(e)}")
            return []
        
        finally:
            if driver:
                driver.quit()
    
    def collect_market_data(self) -> List[Dict]:
        """Collect market moves data from all configured sources"""
        all_articles = []
        
        # First try RSS feeds (more reliable)
        for feed in Config.RSS_FEEDS['market_moves']:
            self.logger.info(f"Collecting market data from RSS: {feed['name']}")
            articles = self.scrape_rss_feed(feed['url'], feed['name'])
            filtered_articles = self.filter_articles(articles, Config.MARKET_KEYWORDS)
            # Only keep articles with valid links
            valid_articles = [article for article in filtered_articles if article.get('link') and self._is_valid_link(article['link'])]
            all_articles.extend(valid_articles)
            time.sleep(1)  # Be respectful to servers
        
        # Then try web scraping (as backup)
        for source in Config.DATA_SOURCES['market_moves']:
            self.logger.info(f"Collecting market data from {source['name']}")
            
            # Try Selenium first for JavaScript-heavy sites
            articles = self.scrape_with_selenium(source)
            
            # If Selenium fails, try requests
            if not articles:
                articles = self.scrape_with_requests(source['url'], source.get('selectors', {}), source['name'])
            
            # Filter articles by keywords and links
            filtered_articles = self.filter_articles(articles, Config.MARKET_KEYWORDS)
            # Only keep articles with valid links
            valid_articles = [article for article in filtered_articles if article.get('link') and self._is_valid_link(article['link'])]
            all_articles.extend(valid_articles)
            
            time.sleep(2)  # Be respectful to servers
        
        return all_articles
    
    def collect_people_moves_data(self) -> List[Dict]:
        """Collect people moves data from all configured sources"""
        all_articles = []
        
        # First try RSS feeds (more reliable)
        for feed in Config.RSS_FEEDS['people_moves']:
            self.logger.info(f"Collecting people moves data from RSS: {feed['name']}")
            articles = self.scrape_rss_feed(feed['url'], feed['name'])
            filtered_articles = self.filter_articles(articles, Config.PEOPLE_MOVES_KEYWORDS)
            # Only keep articles with valid links
            valid_articles = [article for article in filtered_articles if article.get('link') and self._is_valid_link(article['link'])]
            all_articles.extend(valid_articles)
            time.sleep(1)  # Be respectful to servers
        
        # Then try web scraping (as backup)
        for source in Config.DATA_SOURCES['people_moves']:
            self.logger.info(f"Collecting people moves data from {source['name']}")
            
            # Try Selenium first for JavaScript-heavy sites
            articles = self.scrape_with_selenium(source)
            
            # If Selenium fails, try requests
            if not articles:
                articles = self.scrape_with_requests(source['url'], source.get('selectors', {}), source['name'])
            
            # Filter articles by keywords and links
            filtered_articles = self.filter_articles(articles, Config.PEOPLE_MOVES_KEYWORDS)
            # Only keep articles with valid links
            valid_articles = [article for article in filtered_articles if article.get('link') and self._is_valid_link(article['link'])]
            all_articles.extend(valid_articles)
            
            time.sleep(2)  # Be respectful to servers
        
        return all_articles
    
    def filter_articles(self, articles: List[Dict], keywords: List[str]) -> List[Dict]:
        """Filter articles based on relevant keywords and exclude irrelevant content"""
        filtered = []
        
        # Exclusion keywords for personal finance and irrelevant content
        exclusion_keywords = [
            # Personal finance
            'boyfriend', 'girlfriend', 'husband', 'wife', 'spouse', 'partner',
            'estate', 'inheritance', 'will', 'leaving my', 'dealbreaker',
            'credit card debt', 'personal finance', 'retirement planning',
            'mortgage advice', 'loan consolidation', 'budget tips',
            'money management', 'savings account', 'investment advice',
            'financial planning', 'wealth management', 'tax advice',
            
            # Retirement and personal situations
            'retired', 'retirement', 'ira', 'social security', 'pension',
            '401k', '403b', 'roth ira', 'traditional ira', 'annuity',
            'medicare', 'medicaid', 'disability', 'unemployment',
            'am i the biggest loser', 'biggest loser', 'losing money',
            'live off', 'living off', 'income in retirement',
            
            # Consumer/general topics
            'dating', 'relationship', 'marriage', 'divorce', 'family',
            'home buying', 'car loan', 'student loan', 'credit score',
            'insurance advice', 'health insurance', 'life insurance',
            'home insurance', 'auto insurance', 'renters insurance',
            
            # Personal questions and advice
            'should i', 'what should', 'how to save', 'how to invest',
            'is this normal', 'am i doing', 'help me', 'advice needed',
            'am i', 'should i be', 'what do you think', 'need advice',
            'personal question', 'personal situation', 'my situation',
            
            # Non-financial topics
            'recipe', 'cooking', 'travel', 'vacation', 'lifestyle',
            'fashion', 'beauty', 'health', 'fitness', 'diet',
            'entertainment', 'celebrity', 'sports', 'gaming',
            'movie', 'book', 'music', 'art', 'culture',
            
            # Media and entertainment
            'jimmy kimmel', 'charlie kirk', 'fcc', 'mislead', 'killing',
            'talk show', 'late night', 'comedy', 'television', 'tv show',
            'podcast', 'radio', 'streaming', 'netflix', 'disney',
            'hollywood', 'actor', 'actress', 'director', 'producer',
            
            # Politics and non-financial news
            'political', 'election', 'campaign', 'vote', 'voting',
            'congress', 'senate', 'house', 'president', 'governor',
            'mayor', 'candidate', 'democrat', 'republican', 'independent',
            'policy', 'legislation', 'bill', 'law', 'court case',
            
            # Social issues and non-financial
            'social media', 'facebook', 'twitter', 'instagram', 'tiktok',
            'privacy', 'data breach', 'cybersecurity', 'hacking',
            'climate change', 'environment', 'renewable energy', 'solar',
            'education', 'school', 'university', 'college', 'student',
            
            # Age and personal demographics
            'i am 68', 'i am 65', 'i am 70', 'i am 75', 'i am 80',
            'i am 88', 'i am 90', 'years old', 'age 68', 'age 65',
            'age 70', 'age 75', 'age 80', 'age 88', 'age 90'
        ]
        
        for article in articles:
            title_lower = article['title'].lower()
            
            # First check for exclusion keywords
            excluded_keywords = [keyword for keyword in exclusion_keywords if keyword.lower() in title_lower]
            if excluded_keywords:
                self.logger.info(f"🚫 Article excluded: '{article['title'][:50]}...' (excluded by: {excluded_keywords})")
                continue
            
            # STRICT CREDIT FILTERING - Must contain core credit terms
            core_credit_terms = [
                'corporate credit', 'credit markets', 'credit spreads', 'credit rating', 'credit default', 'credit risk',
                'credit default swap', 'credit derivatives', 'credit portfolio', 'credit analysis', 'credit trading',
                'credit fund', 'credit strategy', 'credit investment', 'credit manager', 'credit analyst',
                'credit trader', 'credit research', 'credit desk', 'credit team', 'credit division',
                'corporate bonds', 'bond issuance', 'bond market', 'bond trading', 'bond portfolio',
                'debt issuance', 'debt refinancing', 'debt restructuring', 'debt capital markets',
                'high yield bonds', 'investment grade bonds', 'distressed debt', 'debt securities',
                'leveraged finance', 'leveraged loans', 'leveraged buyout', 'leveraged credit',
                'private credit', 'private debt', 'direct lending', 'private lending',
                'clo', 'collateralised loan obligation', 'collateralized loan obligation',
                'securitised finance', 'securitized finance', 'asset backed securities',
                'specialty finance', 'special situations', 'distressed credit', 'distressed lending',
                'credit restructuring', 'debt restructuring', 'workout', 'credit workout'
            ]
            
            # Check for core credit terms first
            core_matches = [term for term in core_credit_terms if term.lower() in title_lower]
            
            # If no core credit terms, check for secondary credit terms but require multiple matches
            secondary_keywords = [keyword for keyword in keywords if keyword.lower() in title_lower and keyword not in core_credit_terms]
            
            # Only include if:
            # 1. Contains core credit terms, OR
            # 2. Contains at least 2 secondary credit terms, OR  
            # 3. Contains specific credit company names (like 'oaktree', 'blackrock', etc.)
            credit_companies = ['oaktree', 'blackrock', 'apollo', 'carlyle', 'ares', 'kkr', 'blackstone', 'silver point', 'king street', 'blue owl', 'eldridge', 'aegon']
            company_matches = [company for company in credit_companies if company.lower() in title_lower]
            
            if core_matches or len(secondary_keywords) >= 2 or company_matches:
                matching_keywords = core_matches + secondary_keywords + company_matches
                article['relevance_score'] = len(matching_keywords) + (len(core_matches) * 2)  # Boost score for core terms
                filtered.append(article)
                self.logger.info(f"✅ Article matched keywords: '{article['title'][:50]}...' (keywords: {matching_keywords})")
            else:
                self.logger.info(f"❌ Article filtered out: '{article['title'][:50]}...'")
        
        # Sort by relevance score (highest first)
        filtered.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return filtered[:5]  # Return top 5 most relevant articles per source
    
    def collect_all_data(self) -> Dict[str, List[Dict]]:
        """Collect all data from all sources"""
        self.logger.info("Starting data collection...")
        
        market_data = self.collect_market_data()
        people_moves_data = self.collect_people_moves_data()
        
        self.logger.info(f"Collected {len(market_data)} market articles and {len(people_moves_data)} people moves articles")
        
        return {
            'market_moves': market_data,
            'people_moves': people_moves_data,
            'collection_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
