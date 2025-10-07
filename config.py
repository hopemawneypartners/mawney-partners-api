import os
from dotenv import load_dotenv
from typing import List, Dict
import logging

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for Daily News system"""
    
    # Email settings
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    SENDER_NAME = os.getenv('SENDER_NAME', 'Daily News Team')
    
    # Team configuration
    TEAM_EMAILS = [email.strip() for email in os.getenv('TEAM_EMAILS', '').split(',') if email.strip()]
    
    # AI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'daily_news.log')
    
    # RSS feeds for reliable data collection - MAWNEY PARTNERS FOCUS
    RSS_FEEDS = {
        'market_moves': [
            {
                'name': 'Financial Times Markets',
                'url': 'https://www.ft.com/markets?format=rss',
                'type': 'rss'
            },
            {
                'name': 'Financial Times Credit',
                'url': 'https://www.ft.com/credit-markets?format=rss',
                'type': 'rss'
            },
            {
                'name': 'Financial Times Debt Capital Markets',
                'url': 'https://www.ft.com/debt-capital-markets?format=rss',
                'type': 'rss'
            },
            {
                'name': 'Bloomberg Markets',
                'url': 'https://feeds.bloomberg.com/markets/news.rss',
                'type': 'rss'
            },
            {
                'name': 'Bloomberg Credit',
                'url': 'https://feeds.bloomberg.com/credit/news.rss',
                'type': 'rss'
            },
            {
                'name': 'CNBC Finance',
                'url': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114',
                'type': 'rss'
            },
            {
                'name': 'WSJ Markets',
                'url': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
                'type': 'rss'
            },
            {
                'name': 'MarketWatch',
                'url': 'https://feeds.marketwatch.com/marketwatch/marketpulse/',
                'type': 'rss'
            },
            {
                'name': 'Creditflux',
                'url': 'https://www.creditflux.com/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'GlobalCapital',
                'url': 'https://www.globalcapital.com/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'Private Debt Investor',
                'url': 'https://www.privatedebtinvestor.com/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'Private Equity International',
                'url': 'https://www.privateequityinternational.com/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'The Deal',
                'url': 'https://www.thedeal.com/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'Debtwire',
                'url': 'https://www.debtwire.com/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'Financial News',
                'url': 'https://www.fnlondon.com/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'Citywire',
                'url': 'https://www.citywire.co.uk/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'Investment Week',
                'url': 'https://www.investmentweek.co.uk/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'Bloomberg Markets (Additional)',
                'url': 'https://feeds.bloomberg.com/markets/news.rss',
                'type': 'rss'
            },
            {
                'name': 'MarketWatch Top Stories',
                'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
                'type': 'rss'
            },
            {
                'name': 'Creditflux (Additional)',
                'url': 'https://www.creditflux.com/rss',
                'type': 'rss'
            },
            {
                'name': 'With Intelligence - Main Feed',
                'url': 'https://www.withintelligence.com/rss',
                'type': 'rss',
                'username': os.getenv('WITH_INTELLIGENCE_USERNAME'),
                'password': os.getenv('WITH_INTELLIGENCE_PASSWORD')
            },
            {
                'name': 'With Intelligence - Alternative Feed',
                'url': 'https://www.withintelligence.com/feed',
                'type': 'rss',
                'username': os.getenv('WITH_INTELLIGENCE_USERNAME'),
                'password': os.getenv('WITH_INTELLIGENCE_PASSWORD')
            },
            {
                'name': 'FCA News',
                'url': 'https://www.fca.org.uk/news/rss',
                'type': 'rss'
            },
            {
                'name': 'MarketWatch MarketPulse',
                'url': 'https://feeds.marketwatch.com/marketwatch/marketpulse/',
                'type': 'rss'
            },
            {
                'name': 'MarketWatch Top Stories',
                'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
                'type': 'rss'
            },
            {
                'name': 'Financial Times Home',
                'url': 'https://www.ft.com/rss/home',
                'type': 'rss'
            },
            {
                'name': 'Financial Times Companies',
                'url': 'https://www.ft.com/rss/companies',
                'type': 'rss'
            },
            {
                'name': 'Financial Times Markets',
                'url': 'https://www.ft.com/rss/markets',
                'type': 'rss'
            },
            {
                'name': 'Financial Times Management',
                'url': 'https://www.ft.com/rss/management',
                'type': 'rss'
            },
            {
                'name': 'Financial Times Private Equity',
                'url': 'https://www.ft.com/rss/private-equity',
                'type': 'rss'
            },
            {
                'name': 'Financial Times M&A',
                'url': 'https://www.ft.com/rss/mergers-acquisitions',
                'type': 'rss'
            }
        ],
        'people_moves': [
            {
                'name': 'Financial Times People',
                'url': 'https://www.ft.com/people?format=rss',
                'type': 'rss'
            },
            {
                'name': 'Financial Times Management',
                'url': 'https://www.ft.com/management?format=rss',
                'type': 'rss'
            },
            {
                'name': 'Financial Times Companies',
                'url': 'https://www.ft.com/companies?format=rss',
                'type': 'rss'
            },
            {
                'name': 'Bloomberg Markets',
                'url': 'https://feeds.bloomberg.com/markets/news.rss',
                'type': 'rss'
            },
            {
                'name': 'CNBC Finance',
                'url': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114',
                'type': 'rss'
            },
            {
                'name': 'WSJ Markets',
                'url': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
                'type': 'rss'
            },
            {
                'name': 'Financial News',
                'url': 'https://www.fnlondon.com/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'Citywire',
                'url': 'https://www.citywire.co.uk/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'Investment Week',
                'url': 'https://www.investmentweek.co.uk/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'eFinancialCarements',
                'url': 'https://www.efinancialcarements.com/rss.xml',
                'type': 'rss'
            },
            {
                'name': 'City AM',
                'url': 'https://www.cityam.com/rss.xml',
                'type': 'rss'
            }
        ]
    }

    # Data sources configuration
    DATA_SOURCES = {
        'market_moves': [
            {
                'name': 'Financial Times',
                'url': 'https://www.ft.com/markets',
                'username': os.getenv('FT_USERNAME'),
                'password': os.getenv('FT_PASSWORD'),
                'selectors': {
                    'headlines': '.o-teaser__heading:not(nav .o-teaser__heading):not(footer .o-teaser__heading)',
                    'links': '.o-teaser a:not(nav a):not(footer a)',
                    'timestamps': '.o-teaser__timestamp:not(nav .o-teaser__timestamp):not(footer .o-teaser__timestamp)'
                }
            },
            {
                'name': 'Bloomberg',
                'url': 'https://www.bloomberg.com/markets',
                'username': os.getenv('BLOOMBERG_USERNAME'),
                'password': os.getenv('BLOOMBERG_PASSWORD'),
                'selectors': {
                    'headlines': '.story-package-module__story__headline',
                    'links': '.story-package-module__story__link',
                    'timestamps': '.story-package-module__story__timestamp'
                }
            },
            {
                'name': 'Reuters',
                'url': 'https://www.reuters.com/business/',
                'username': os.getenv('REUTERS_USERNAME'),
                'password': os.getenv('REUTERS_PASSWORD'),
                'selectors': {
                    'headlines': '[data-testid="Heading"]:not(nav [data-testid="Heading"]):not(footer [data-testid="Heading"])',
                    'links': 'a[data-testid="Link"]:not(nav a):not(footer a)',
                    'timestamps': 'time:not(nav time):not(footer time)'
                }
            },
            {
                'name': 'Goldman Sachs News',
                'url': 'https://www.goldmansachs.com/media-relations/index.html',
                'username': None,
                'password': None,
                'selectors': {
                    'headlines': '.news-item h3, .press-release h3, .announcement h3',
                    'links': '.news-item a, .press-release a, .announcement a',
                    'timestamps': '.news-date, .press-date, .announcement-date'
                }
            },
            {
                'name': 'JP Morgan News',
                'url': 'https://www.jpmorgan.com/news',
                'username': None,
                'password': None,
                'selectors': {
                    'headlines': '.news-title, .press-title, h3',
                    'links': '.news-item a, .press-item a, a[href*="/news/"]',
                    'timestamps': '.news-date, .press-date, time'
                }
            },
            {
                'name': 'Blackstone News',
                'url': 'https://www.blackstone.com/news',
                'username': None,
                'password': None,
                'selectors': {
                    'headlines': '.news-title, .press-title, h3',
                    'links': '.news-item a, .press-item a, a[href*="/news/"]',
                    'timestamps': '.news-date, .press-date, time'
                }
            },
            {
                'name': 'Apollo News',
                'url': 'https://www.apollo.com/news',
                'username': None,
                'password': None,
                'selectors': {
                    'headlines': '.news-title, .press-title, h3',
                    'links': '.news-item a, .press-item a, a[href*="/news/"]',
                    'timestamps': '.news-date, .press-date, time'
                }
            },
            {
                'name': 'BNP Paribas News',
                'url': 'https://www.bnpparibas.com/news',
                'username': None,
                'password': None,
                'selectors': {
                    'headlines': 'h1, h2, h3, h4',
                    'links': 'a[href*="/news/"]',
                    'timestamps': 'time, .date, .timestamp'
                }
            },
            {
                'name': 'UBS News',
                'url': 'https://www.ubs.com/news',
                'username': None,
                'password': None,
                'selectors': {
                    'headlines': 'h1, h2, h3, h4',
                    'links': 'a[href*="/news/"]',
                    'timestamps': 'time, .date, .timestamp'
                }
            },
            {
                'name': 'Citi News',
                'url': 'https://www.citi.com/citi/news/',
                'username': None,
                'password': None,
                'selectors': {
                    'headlines': 'h1, h2, h3, h4',
                    'links': 'a[href*="/news/"]',
                    'timestamps': 'time, .date, .timestamp'
                }
            },
            {
                'name': 'Macquarie News',
                'url': 'https://www.macquarie.com/about/news/',
                'username': None,
                'password': None,
                'selectors': {
                    'headlines': 'h1, h2, h3, h4',
                    'links': 'a[href*="/news/"]',
                    'timestamps': 'time, .date, .timestamp'
                }
            },
            {
                'name': 'Standard Chartered News',
                'url': 'https://www.standardchartered.com/about-us/news/',
                'username': None,
                'password': None,
                'selectors': {
                    'headlines': 'h1, h2, h3, h4',
                    'links': 'a[href*="/news/"]',
                    'timestamps': 'time, .date, .timestamp'
                }
            },
            {
                'name': 'BBVA News',
                'url': 'https://www.bbva.com/en/news/',
                'username': None,
                'password': None,
                'selectors': {
                    'headlines': 'h1, h2, h3, h4',
                    'links': 'a[href*="/news/"]',
                    'timestamps': 'time, .date, .timestamp'
                }
            }
        ],
        'people_moves': [
            {
                'name': 'LinkedIn',
                'url': 'https://www.linkedin.com/feed/',
                'username': os.getenv('LINKEDIN_USERNAME'),
                'password': os.getenv('LINKEDIN_PASSWORD'),
                'selectors': {
                    'posts': '.feed-shared-update-v2',
                    'content': '.feed-shared-text',
                    'timestamps': '.feed-shared-actor__sub-description'
                }
            },
            {
                'name': 'With Intelligence',
                'url': 'https://www.withintelligence.com/insights/',
                'username': os.getenv('WITH_INTELLIGENCE_USERNAME'),
                'password': os.getenv('WITH_INTELLIGENCE_PASSWORD'),
                'selectors': {
                    'headlines': '.title:not(nav .title):not(footer .title), h3:not(nav h3):not(footer h3), h2:not(nav h2):not(footer h2)',
                    'links': 'a[href*="/insight/"]:not(nav a):not(footer a), a[href*="/report/"]:not(nav a):not(footer a), a[href*="/article/"]:not(nav a):not(footer a)',
                    'timestamps': '.date, .timestamp, time, .published'
                }
            },
            {
                'name': 'Credit Risk Professional',
                'url': 'https://www.creditriskprofessional.com/news',
                'username': os.getenv('CRP_USERNAME'),
                'password': os.getenv('CRP_PASSWORD'),
                'selectors': {
                    'headlines': '.news-title',
                    'links': '.news-link',
                    'timestamps': '.news-date'
                }
            }
        ]
    }
    
    
    # MARKET MOVES - CREDIT FOCUSED ONLY - Everything else in the credit industry
    MARKET_KEYWORDS = [
        # CREDIT CORE TERMS - Must contain credit/debt/bond terms
        'corporate credit', 'credit markets', 'credit spreads', 'credit rating', 'credit default', 'credit risk',
        'credit default swap', 'credit derivatives', 'credit portfolio', 'credit analysis', 'credit trading',
        'credit fund', 'credit strategy', 'credit investment', 'credit manager', 'credit analyst',
        'credit trader', 'credit research', 'credit desk', 'credit team', 'credit division',
        
        # DEBT & BONDS - Core credit instruments
        'corporate bonds', 'bond issuance', 'bond market', 'bond trading', 'bond portfolio',
        'debt issuance', 'debt refinancing', 'debt restructuring', 'debt capital markets',
        'high yield bonds', 'investment grade bonds', 'distressed debt', 'debt securities',
        'bond yields', 'bond spreads', 'bond prices', 'bond indices', 'bond funds',
        
        # LEVERAGED FINANCE - Credit-specific
        'leveraged finance', 'leveraged loans', 'leveraged buyout', 'leveraged credit',
        'leveraged debt', 'leveraged lending', 'leveraged fund', 'leveraged portfolio',
        
        # PRIVATE CREDIT - Direct lending focus
        'private credit', 'private debt', 'direct lending', 'private lending',
        'credit lending', 'debt lending', 'loan origination', 'credit origination',
        
        # STRUCTURED CREDIT - CLOs, ABS, etc.
        'clo', 'collateralised loan obligation', 'collateralized loan obligation',
        'securitised finance', 'securitized finance', 'asset backed securities',
        'abs', 'structured credit', 'structured debt', 'credit securitization',
        
        # SPECIALTY CREDIT
        'specialty finance', 'special situations', 'distressed credit', 'distressed lending',
        'credit restructuring', 'debt restructuring', 'workout', 'credit workout',
        
        # CREDIT-SPECIFIC M&A & RESTRUCTURING
        'debt advisory', 'restructuring advisor', 'debt restructuring', 'credit restructuring',
        'distressed m&a', 'debt-for-equity', 'debt exchange', 'credit workout',
        
        # CREDIT-SPECIFIC PRIVATE EQUITY
        'credit pe', 'debt pe', 'credit buyout', 'debt buyout', 'credit secondaries',
        'debt secondaries', 'credit portfolio', 'debt portfolio',
        
        # CREDIT-SPECIFIC FICC
        'credit fixed income', 'credit derivatives', 'credit structured solutions',
        'credit treasury', 'credit rates', 'credit fx', 'credit macro',
        
        # CREDIT-SPECIFIC BUSINESS DEVELOPMENT
        'credit sales', 'debt sales', 'credit investor relations', 'debt investor relations',
        'credit business development', 'debt business development', 'credit product specialist',
        'debt product specialist', 'credit capital formation', 'debt capital formation',
        
        # CREDIT MARKET TERMS
        'credit market', 'debt market', 'bond market', 'credit economy', 'debt economy',
        'credit interest rate', 'debt interest rate', 'credit yield', 'debt yield',
        'credit volatility', 'debt volatility', 'credit liquidity', 'debt liquidity',
        'credit spread widening', 'credit spread tightening', 'debt spread widening', 'debt spread tightening',
        
        # Comprehensive Asset Manager & Fund Keywords (Mawney Partners)
        'aberdeen group', 'acadian asset management', 'aegon', 'alliance trust',
        'alliancebernstein', 'allianz global investors', 'allspring global investments',
        'amundi', 'aqr capital', 'aristotle capital management', 'arrowstreet capital',
        'aviva investors', 'axa investment managers', 'axis asset management',
        'baillie gifford', 'barclays', 'barings llc', 'blackrock', 'blackstone',
        'bluebay asset management', 'bnp paribas asset management', 'bny',
        'boston partners', 'bridgewater associates', 'brookfield asset management',
        'brown advisory', 'btg pactual', 'cambridge associates', 'cambridge investment research',
        'candriam investors group', 'capital fund management', 'capital group',
        'charles schwab corporation', 'ci financial', 'columbia threadneedle investments',
        'conning', 'credit agricole', 'dekabank', 'dimensional fund advisors',
        'dodge & cox', 'doubleline capital', 'dreyfus corporation', 'dws group',
        'eastspring investments', 'eaton vance', 'eldridge', 'eurizon capital',
        'f&c asset management', 'federated hermes', 'fidelity international',
        'fidelity investments', 'first sentier investors', 'first trust',
        'fisher investments', 'franklin templeton', 'gamco investors',
        'generali investments', 'geode capital management', 'gmo llc',
        'goldman sachs am', 'henderson group', 'hsbc', 'icbc credit suisse asset management',
        'icici prudential asset management', 'ifm investors', 'insight investment',
        'invesco', 'investcorp', 'itau unibanco', 'janus capital group',
        'janus henderson', 'jpmorgan am', 'jupiter fund management',
        'legal & general', 'legg mason', 'lgt group', 'liongate capital management',
        'lombard odier', 'loomis sayles & company', 'lord abbett', 'm&g investments',
        'macquarie asset management', 'magellan financial group', 'manulife investment management',
        'meag', 'mercury asset management', 'merrill', 'mfs investment management',
        'mirabaud group', 'mirae asset financial group', 'morgan stanley im',
        'mufg', 'nbk capital', 'neuberger berman', 'newton investment management',
        'ninety one ltd', 'nisa investment advisors', 'nn investment partners',
        'nomura holdings', 'northern trust', 'northern trust corporation',
        'nuveen investments', 'oaktree capital management', 'octopus group',
        'old mutual', 'orbis investment management', 'payden & rygel', 'perpetual',
        'pgim', 'pimco', 'pinebridge investments', 'pinnacle investment management',
        'platinum asset management', 'polen capital', 'principal financial group',
        'prudential financial', 'psp investments', 'public investment corporation',
        'putnam investments', 'pzena investment management', 'rathbones',
        'raymond james', 'robeco', 'royal london asset management',
        'russell investments', 'schroders', 'skagen funds', 'state street global advisors',
        'sumitomo mitsui trust holdings', 'sun life financial', 'swiss life',
        't. rowe price', 'tcw group', 'the children\'s mutual', 'the vanguard group',
        'tiaa', 'ubs', 'vaneck', 'vanguard group', 'victory capital',
        'virtus investment partners', 'voya financial', 'wellington management company',
        'wisdomtree investments',
        
        # Major Hedge Funds & Alternative Asset Managers
        'apollo', 'carlyle', 'blackstone', 'ares', 'kkr', 'schonfeld', 'point72',
        'millennium', 'brevan howard', 'citadel', 'balyasny', 'marshall wace',
        'verition', 'rokos', 'exoduspoint', 'bluecrest', 'jain global', 'taula',
        'centiva', 'system 2 capital', 'palmerston capital', 'axebrook capital',
        'acasta partners', 'aperture investors', 'acer tree', 'chepstow lane',
        'tt international', 'tresidor investment management', 'king street',
        'davidson kempner', 'farallon', 'sona am', 'arini', 'varde partners',
        'ab carval', 'cross ocean partners', 'de shaw', 'diameter capital',
        'faros point', 'hbk', 'ironshield', 'man group', 'chenavari', 'cheyne capital',
        
        # Private Credit & Direct Lending Firms
        'alcentra', 'albaCore', 'alchemy partners', 'alinor capital', 'anchorage',
        'aptior', 'arcmont', 'arena investors', 'astaris', 'attestor',
        'avenue capital', 'bain capital credit', 'beach point', 'ben oldman',
        'blantyre', 'brigade capital', 'caius capital', 'canyon', 'castlelake',
        'centerbridge', 'cerberus', 'chepstow lane', 'cyrus capital', 'davide leone',
        'eicos investment management', 'elliott', 'eqt/bridgepoint', 'fidera',
        'fortress', 'goldentree', 'h/2 capital', 'hayfin', 'hig bayside', 'hps',
        'icg', 'jp morgan asset management global special situations', 'kimmik capital',
        'kite lake', 'kyma capital', 'lodbrok', 'man glg', 'marathon asset management',
        'melqart', 'monarch capital', 'mudrick capital', 'negentropy', 'njord partners',
        'northwall', 'oak hill', 'oaktree', 'octane', 'one im', 'pearlstone alternative',
        'permira', 'pvtl point', 'polus capital', 'rbc bluebay', 'sculptor capital management',
        'serone', 'silver point capital', 'sixth street', 'sona', 'sparta capital',
        'svpglobal', 'taconic', 'tikehau', 'tpg angelo gordon', 'triton debt opportunities',
        'varde', 'warwick capital', 'zetland capital',
        
        # Additional Asset Managers & Funds
        '17 capital', '400 capital', 'aberdeen', 'adams street', 'aimco', 'albacore',
        'all seas', 'alpha wave', 'apera am', 'ardian', 'arrow global', 'ashgrove',
        'aurelius', 'avenue', 'aviva', 'bgo', 'blue owl', 'bridgepoint', 'brookfield am',
        'cdpq', 'cic', 'cifc', 'claret capital', 'clearlake', 'cordet', 'corinthia global',
        'cpp ib', 'crescent capital', 'crestline', 'cvc', 'dws', 'deva capital',
        'ebrd', 'edmond de rothschild', 'eurazeo', 'fasanara', 'fiera capital',
        'five arrows', 'fitzwalter', 'general atlantic', 'gic', 'gsam', 'golub',
        'hamilton lane', 'harwood', 'hig capital', 'investec', 'jefferies credit partners',
        'kartesia', 'kinnerton hill', 'lgim', 'letterone', 'lgt capital', 'marathon am',
        'muzinich', 'north leaf', 'nuveen', 'omers', 'orchard global', 'pak square capital',
        'partners group', 'patrizia', 'pemberton', 'phoenix group', 'pictet',
        'pollen street', 'pricoa capital', 'psp', 'soho square', 'temasek',
        'tenax capital', 'tresmares',
        
        # Additional Credit & Distressed Funds
        'acasta', 'athlone', 'assured im', 'artemis', 'black diamond', 'bluebay',
        'bluecrest', 'boussard & gavaudan', 'bmo', 'boundary creek', 'bridgepoint',
        'brigade capital', 'canyon partners', 'centiva', 'chenevari', 'chepstow lane',
        'cheyne', 'cifc', 'clearlake', 'copper street', 'cpp ib', 'cqs',
        'cross ocean', 'cvc', 'deltroit', 'diameter', 'dws', 'ebrd', 'eisler capital',
        'elmwood', 'emso', 'fair oaks', 'five arrows', 'gic', 'goldentree', 'gsam',
        'graham capital', 'hayfin', 'hbk', 'hps', 'hudson bay capital', 'icg',
        'insight investments', 'invesco', 'investcorp', 'investec', 'jain global',
        'janus henderson', 'jupiter am', 'kartesia', 'king street', 'kite lake',
        'kyma', 'lgim', 'letterone', 'lgt', 'lmr', 'lombard odier', 'man group',
        'marathon am', 'mfs im', 'm&g investments', 'millennium', 'morgan stanley im',
        'muzinich', 'napier park', 'nassau', 'neuberger berman', 'ninety one',
        'northlight', 'oak hill', 'oaktree', 'omers', 'onex', 'orchard global',
        'palmer square', 'partners group', 'permira', 'pgim', 'pimco', 'pictet',
        'pinebridge', 'polen capital', 'polus capital', 'pvtl point', 'robus',
        'rokos', 'schonfeld', 'schroders', 'sculptor capital', 'shenkman', 'signal',
        'silver point', 'sona', 'sound point', 'spire', 'squarepoint', 'symmetry',
        'tcw', 'temasek', 'tenax', 'tikehau', 'tpg angelo gordon', 'tresidor',
        't. rowe price', 'tt international', 'vanguard', 'varde', 'verition',
        'voya', 'walleye', 'waterfall am', 'wellington', 'western am', 'white box',
        'winton', 'zetland',
        
        # Additional Private Credit & Direct Lending
        'accunia', 'acer tree', 'aegon', 'albacore', 'angelo gordon', 'apollo redding ridge',
        'arcano', 'bain', 'barings', 'black diamond', 'bnp paribas', 'bridgepoint',
        'brigade', 'canyon', 'capital four', 'carlyle', 'carval', 'chenavari',
        'cic private debt', 'cifc', 'clearlake', 'cqs', 'cross ocean', 'cvc',
        'diameter capital', 'elmwood am', 'fair oaks', 'fidelity', 'five arrows',
        'fortress', 'franklin templeton/alcentra', 'goldentree', 'guggenheim',
        'hayfin', 'hps', 'icg', 'invesco', 'investcorp', 'king street', 'kkr',
        'lgt', 'macquarie', 'man group', 'm&g', 'napier park', 'nassau global',
        'neuberger berman', 'oak hill', 'oaktree', 'onex', 'palmer square',
        'partners group', 'pemberton', 'permira', 'pinebridge', 'pgim', 'polus capital',
        'rbc', 'royal london', 'serone', 'sculptor', 'signal harmonic', 'silver point',
        'sona am', 'sound point', 'spire', 'tikehau', 'ubs', 'voya', 'whitestar am',
        
        # Restructuring Advisors
        'moelis', 'pjt', 'houlihan lokey', 'fti consulting',
        'alvarez & marsal', 'perella weinberg', 'dc advisory', 'lazard',
        'alixpartners', 'evercore', 'rothschild',
        
        # Brokers
        'stifel', 'oppenheimer', 'seaport', 'aurel', 'bgc', 'imperial capital',
        'btig', 'stonex', 'cantor fitzgerald', 'cowen',
        
        # Comprehensive Bank & Financial Institution Keywords (Mawney Partners)
        'goldman sachs', 'jp morgan', 'bank of america merrill lynch', 'morgan stanley',
        'citi', 'deutsche bank', 'barclays', 'bnp paribas', 'ubs', 'rbc',
        'jefferies', 'nomura', 'macquarie', 'standard chartered', 'natwest',
        'unicredit', 'santander', 'wells fargo', 'bbva', 'societe generale',
        'credit agricole', 'mitsubishi', 'natixis', 'hsbc', 'lloyds',
        'truist', 'pnc', 'rbc capital markets', 'td securities', 'bmo',
        'scotiabank', 'cibc', 'handelsbanken', 'seb', 'nordea', 'danske',
        'dnb', 'carnegie', 'cic', 'commerzbank', 'dz bank', 'berenberg',
        'bayern lb', 'nord lb', 'hamburg bank', 'raiffeisen bank', 'erste',
        'intesa sanpaolo', 'banca imi', 'mediobanca', 'mps', 'caixabank',
        'sabadell', 'novo banco', 'caxia general de deposites', 'ing',
        'rabobank', 'abn amro', 'bank degroof petercam', 'bnp paribas fortis',
        'kbc bank', 'van lanschot', 'absa', 'standard bank', 'icbc',
        'rand merchant', 'nedbank', 'banque misr', 'ecobank', 'access bank',
        'anz', 'cba', 'nab', 'westpac', 'emirates nbd', 'first abu dhabi bank',
        'abu dhabi commercial bank', 'qnb', 'mashreq', 'mizuho',
        'mitsubishi ufj', 'smbc', 'mitsui', 'bank of china', 'hi tong',
        'china construction bank', 'agricultural bank of china', 'citic',
        'dbs', 'ocbc', 'btg pactual', 'banco do brazil', 'itau', 'safra'
    ]

    
    # PEOPLE MOVES - Only actual people changing jobs, getting promoted, joining/leaving companies
    PEOPLE_MOVES_KEYWORDS = [
        # PEOPLE MOVES ONLY - Job changes, appointments, departures, promotions
        'appointed', 'hired', 'joined', 'promoted', 'resigned', 'departed',
        'leaves', 'leaving', 'exits', 'exiting', 'quits', 'quitting',
        'named', 'named as', 'takes role', 'takes position', 'assumes role',
        'becomes', 'becomes head', 'becomes chief', 'becomes director',
        'steps down', 'steps up', 'moves to', 'moves from', 'switches to',
        'joins from', 'leaves for', 'departs for', 'heads to',
        'new hire', 'new appointment', 'replacement', 'successor',
        'career move', 'job change', 'role change', 'position change',
        'executive', 'senior executive', 'senior hire', 'senior appointment',
        'leadership', 'leadership change', 'management change',
        'ceo', 'cfo', 'coo', 'cto', 'cmo', 'chief executive', 'chief financial',
        'chief operating', 'chief technology', 'chief marketing',
        'managing director', 'executive director', 'senior director',
        'partner', 'senior partner', 'managing partner',
        'head of', 'chief of', 'director of', 'manager of',
        'portfolio manager', 'investment manager', 'fund manager',
        'credit analyst', 'risk manager', 'trader', 'sales director',
        'business development', 'investor relations', 'product specialist',
        
        # Job Titles & Roles (for people moves only)
        'credit analyst', 'credit trader', 'credit portfolio manager',
        'm&a banker', 'restructuring banker', 'advisory banker',
        'pe analyst', 'pe associate', 'pe principal', 'pe partner',
        'macro trader', 'rates trader', 'fx trader', 'commodity trader',
        'ir director', 'bd director', 'sales director',
        'vp', 'associate', 'analyst', 'senior analyst', 'principal',
        'compensation', 'bonus', 'carried interest', 'partnership'
    ]

    
    @classmethod
    def setup_logging(cls):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        required_fields = ['EMAIL_ADDRESS', 'EMAIL_PASSWORD']
        missing_fields = [field for field in required_fields if not getattr(cls, field)]
        
        if missing_fields:
            print('Missing required configuration: ' + ', '.join(missing_fields))
            print('Please check your .env file')
            return False
        
        if not cls.TEAM_EMAILS:
            print('No team emails configured')
            return False
            
        return True
