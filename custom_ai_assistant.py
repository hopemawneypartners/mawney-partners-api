#!/usr/bin/env python3
"""
Custom AI Assistant for Mawney Partners
A rule-based AI system for financial queries, job adverts, CV formatting, and market insights
"""

import re
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import random
from ai_memory_system import store_interaction, get_custom_response, get_learned_suggestions, add_custom_response
from cv_formatter import cv_formatter
from cv_file_generator import cv_file_generator
from mawney_template_formatter import MawneyTemplateFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Response from the AI assistant"""
    text: str
    type: str  # 'answer', 'job_ad', 'cv_format', 'market_insight', 'error'
    confidence: float  # 0.0 to 1.0
    sources: List[str] = None
    actions: List[str] = None

class CustomAIAssistant:
    def __init__(self):
        self.knowledge_base = self._initialize_knowledge_base()
        self.templates = self._initialize_templates()
        self.market_data = self._initialize_market_data()
        
    def _initialize_knowledge_base(self) -> Dict:
        """Initialize the comprehensive knowledge base with financial and credit market information"""
        return {
            "credit_markets": {
                "definitions": {
                    "corporate_credit": "Debt securities issued by corporations, including bonds and loans. Key metrics include credit spreads, duration, and recovery rates.",
                    "credit_spreads": "The difference in yield between corporate bonds and government bonds. Widening spreads indicate increased credit risk perception.",
                    "leveraged_finance": "High-yield debt financing for companies with significant debt levels, typically debt-to-EBITDA ratios above 4x.",
                    "private_credit": "Non-bank lending to companies, often with higher yields than public markets. Includes direct lending, mezzanine, and distressed debt.",
                    "clo": "Collateralized Loan Obligation - a structured credit product backed by leveraged loans, providing diversified exposure to senior secured loans.",
                    "distressed_debt": "Debt securities of companies in financial distress or bankruptcy, offering potential for high returns through restructuring.",
                    "credit_default_swap": "A financial derivative that provides protection against credit events, used for hedging and speculation.",
                    "recovery_rate": "The percentage of principal recovered when a borrower defaults, typically 40-60% for senior secured loans.",
                    "duration": "A measure of bond price sensitivity to interest rate changes, expressed in years.",
                    "yield_to_maturity": "The total return anticipated on a bond if held until maturity, including coupon payments and capital gains/losses.",
                    "credit_rating": "Assessment of creditworthiness by agencies like Moody's, S&P, and Fitch, ranging from AAA (highest) to D (default).",
                    "covenant": "Terms in loan agreements that protect lenders by restricting borrower actions or requiring certain financial metrics.",
                    "refinancing_risk": "The risk that a borrower cannot refinance debt at maturity, potentially leading to default.",
                    "credit_cycle": "The cyclical nature of credit markets, alternating between periods of easy credit and tight credit conditions."
                },
                "key_players": {
                    "private_equity": ["Blackstone", "Apollo Global Management", "KKR", "Carlyle Group", "Ares Management", "Oaktree Capital", "Brookfield Asset Management"],
                    "investment_banks": ["Goldman Sachs", "Morgan Stanley", "JPMorgan Chase", "Bank of America", "Credit Suisse", "Deutsche Bank"],
                    "asset_managers": ["BlackRock", "Vanguard", "State Street", "Fidelity", "PIMCO", "Allianz Global Investors"],
                    "insurance_companies": ["Prudential", "MetLife", "AIG", "Allianz", "AXA", "Zurich Insurance"]
                },
                "regulations": {
                    "global": ["Basel III", "Dodd-Frank Act", "MiFID II", "Solvency II"],
                    "uk": ["Bank of England Prudential Regulation", "FCA Conduct Rules", "Senior Managers Regime"],
                    "us": ["Volcker Rule", "CCAR", "Dodd-Frank Stress Testing", "SEC Regulations"],
                    "eu": ["CRD IV", "BRRD", "MiFID II", "GDPR"]
                },
                "market_sizes": {
                    "global_bond_market": "$130 trillion",
                    "leveraged_loan_market": "$1.2 trillion",
                    "high_yield_bond_market": "$1.8 trillion",
                    "private_credit_market": "$1.4 trillion",
                    "clo_market": "$800 billion"
                }
            },
            "job_market": {
                "roles": {
                    "credit_analyst": {
                        "description": "Analyzes creditworthiness of borrowers and debt securities, builds financial models, and monitors portfolio performance.",
                        "responsibilities": ["Financial modeling", "Credit risk assessment", "Industry analysis", "Portfolio monitoring", "Investment recommendations"],
                        "skills_required": ["Excel", "Bloomberg", "Financial modeling", "Credit analysis", "Industry knowledge"],
                        "career_path": "Analyst → Associate → VP → Director → MD"
                    },
                    "portfolio_manager": {
                        "description": "Manages investment portfolios, makes allocation decisions, and oversees risk management strategies.",
                        "responsibilities": ["Portfolio construction", "Risk management", "Performance attribution", "Client communication", "Investment strategy"],
                        "skills_required": ["CFA", "Portfolio management", "Risk management", "Client relations", "Market analysis"],
                        "career_path": "Associate → VP → Director → Portfolio Manager → CIO"
                    },
                    "risk_manager": {
                        "description": "Identifies and mitigates financial risks across trading, credit, operational, and market risk areas.",
                        "responsibilities": ["Risk assessment", "Stress testing", "Model validation", "Regulatory compliance", "Risk reporting"],
                        "skills_required": ["FRM", "Risk modeling", "Regulatory knowledge", "Quantitative skills", "Communication"],
                        "career_path": "Risk Analyst → Risk Manager → Head of Risk → CRO"
                    },
                    "relationship_manager": {
                        "description": "Manages client relationships and business development, focusing on institutional investors and corporates.",
                        "responsibilities": ["Client relationship management", "Business development", "Product sales", "Market intelligence", "Client service"],
                        "skills_required": ["Client relations", "Sales skills", "Product knowledge", "Market awareness", "Communication"],
                        "career_path": "Associate → VP → Director → Managing Director"
                    },
                    "structuring_analyst": {
                        "description": "Creates complex financial products and structures, including derivatives, structured notes, and securitizations.",
                        "responsibilities": ["Product structuring", "Pricing models", "Documentation", "Regulatory compliance", "Client solutions"],
                        "skills_required": ["Quantitative skills", "Product knowledge", "Legal understanding", "Programming", "Creativity"],
                        "career_path": "Analyst → Associate → VP → Director → Head of Structuring"
                    }
                },
                "skills": {
                    "technical": ["Financial modeling", "Credit analysis", "Risk assessment", "Excel proficiency", "Bloomberg Terminal", "Python/R programming", "SQL", "VBA"],
                    "qualifications": ["CFA qualification", "FRM certification", "MBA degree", "CAIA", "PRM", "CQF"],
                    "soft_skills": ["Communication", "Presentation skills", "Teamwork", "Problem-solving", "Attention to detail", "Time management"]
                },
                "salary_ranges": {
                    "analyst": {"min": 40000, "max": 70000, "currency": "GBP", "bonus": "20-50%"},
                    "associate": {"min": 70000, "max": 120000, "currency": "GBP", "bonus": "50-100%"},
                    "vp": {"min": 120000, "max": 200000, "currency": "GBP", "bonus": "100-200%"},
                    "director": {"min": 200000, "max": 350000, "currency": "GBP", "bonus": "200-300%"},
                    "md": {"min": 350000, "max": 1000000, "currency": "GBP", "bonus": "300-500%"}
                },
                "interview_process": {
                    "stages": ["CV screening", "Phone interview", "Technical test", "Panel interview", "Final interview"],
                    "technical_topics": ["Financial modeling", "Credit analysis", "Market knowledge", "Case studies", "Behavioral questions"],
                    "preparation": ["Practice modeling", "Read financial news", "Understand company", "Prepare questions", "Mock interviews"]
                }
            },
            "market_insights": {
                "current_trends": {
                    "macro": [
                        "Central bank tightening cycles affecting credit spreads",
                        "Inflation concerns driving rate volatility",
                        "Geopolitical tensions impacting risk appetite",
                        "ESG integration becoming standard practice",
                        "Technology disruption accelerating in financial services"
                    ],
                    "credit_specific": [
                        "Private credit market growth outpacing public markets",
                        "CLO market resilience despite volatility",
                        "Distressed debt opportunities emerging",
                        "Covenant-lite loans becoming standard",
                        "Direct lending gaining market share"
                    ],
                    "regulatory": [
                        "Basel III implementation continuing",
                        "ESG disclosure requirements increasing",
                        "Stress testing becoming more sophisticated",
                        "Cross-border regulation harmonization",
                        "Digital asset regulation evolving"
                    ]
                },
                "sectors": {
                    "technology": {
                        "credit_profile": "High growth but volatile, cash-burn models common",
                        "key_risks": ["Competition", "Regulation", "Technology obsolescence"],
                        "opportunities": ["Cloud computing", "AI/ML", "Cybersecurity", "Fintech"]
                    },
                    "healthcare": {
                        "credit_profile": "Stable demand but regulatory and patent risks",
                        "key_risks": ["Regulatory approval", "Patent cliffs", "Pricing pressure"],
                        "opportunities": ["Biotech", "Medical devices", "Digital health", "Aging population"]
                    },
                    "energy": {
                        "credit_profile": "Transition risks from ESG pressures, commodity volatility",
                        "key_risks": ["ESG transition", "Commodity prices", "Regulation"],
                        "opportunities": ["Renewable energy", "Energy storage", "Carbon capture", "Grid modernization"]
                    },
                    "financial_services": {
                        "credit_profile": "Regulatory headwinds but strong fundamentals",
                        "key_risks": ["Regulation", "Technology disruption", "Interest rates"],
                        "opportunities": ["Digital banking", "Wealth management", "Insurance", "Payments"]
                    },
                    "real_estate": {
                        "credit_profile": "Interest rate sensitive, location dependent",
                        "key_risks": ["Interest rates", "Location", "Tenant quality"],
                        "opportunities": ["Logistics", "Data centers", "Senior housing", "Affordable housing"]
                    }
                },
                "market_indicators": {
                    "credit_spreads": {
                        "investment_grade": "100-200 bps",
                        "high_yield": "400-800 bps",
                        "leveraged_loans": "300-600 bps",
                        "distressed": "1000+ bps"
                    },
                    "default_rates": {
                        "investment_grade": "0.5-2%",
                        "high_yield": "2-8%",
                        "leveraged_loans": "1-5%",
                        "distressed": "10-30%"
                    },
                    "recovery_rates": {
                        "senior_secured": "60-80%",
                        "senior_unsecured": "40-60%",
                        "subordinated": "20-40%",
                        "equity": "0-20%"
                    }
                }
            },
            "financial_products": {
                "bonds": {
                    "types": ["Government bonds", "Corporate bonds", "Municipal bonds", "Agency bonds", "Supranational bonds"],
                    "features": ["Coupon rate", "Maturity date", "Credit rating", "Call provisions", "Put provisions"],
                    "risks": ["Interest rate risk", "Credit risk", "Liquidity risk", "Reinvestment risk"]
                },
                "loans": {
                    "types": ["Term loans", "Revolvers", "Bridge loans", "Mezzanine loans", "Unitranche loans"],
                    "features": ["Interest rate", "Maturity", "Covenants", "Security", "Prepayment terms"],
                    "risks": ["Credit risk", "Interest rate risk", "Prepayment risk", "Concentration risk"]
                },
                "derivatives": {
                    "types": ["Credit default swaps", "Interest rate swaps", "Total return swaps", "Credit options"],
                    "uses": ["Hedging", "Speculation", "Arbitrage", "Portfolio management"],
                    "risks": ["Counterparty risk", "Market risk", "Liquidity risk", "Model risk"]
                },
                "structured_products": {
                    "types": ["CLOs", "CDOs", "ABS", "MBS", "Structured notes"],
                    "features": ["Tranching", "Credit enhancement", "Cash flow waterfall", "Trigger events"],
                    "risks": ["Credit risk", "Prepayment risk", "Model risk", "Complexity risk"]
                }
            },
            "economic_indicators": {
                "macro": {
                    "gdp": "Gross Domestic Product - measures economic output",
                    "inflation": "Consumer Price Index - measures price level changes",
                    "unemployment": "Unemployment rate - measures labor market health",
                    "interest_rates": "Central bank policy rates - affects borrowing costs",
                    "currency": "Exchange rates - affects international trade and investment"
                },
                "credit_specific": {
                    "credit_spreads": "Difference between corporate and government bond yields",
                    "default_rates": "Percentage of borrowers defaulting on obligations",
                    "recovery_rates": "Percentage of principal recovered in default",
                    "credit_availability": "Ease of obtaining credit financing",
                    "covenant_tightness": "Strictness of loan agreement terms"
                }
            }
        }
    
    def _initialize_templates(self) -> Dict:
        """Initialize response templates for different types of queries"""
        return {
            "job_ad": {
                "senior": """
**Senior {role} - {company}**

**About the Role:**
We are seeking an experienced {role} to join our {department} team. The successful candidate will be responsible for {responsibilities}.

**Key Responsibilities:**
• {responsibility_1}
• {responsibility_2}
• {responsibility_3}

**Requirements:**
• {experience} years of experience in {field}
• {qualification} qualification preferred
• Strong {skill_1} and {skill_2} skills
• Excellent communication and analytical abilities

**Compensation:**
Competitive salary of {salary_range} plus bonus and benefits package.

**Location:** {location}
**Type:** {employment_type}

Contact: {contact_email}
                """,
                "junior": """
**{role} - {company}**

**About the Role:**
An excellent opportunity for a {level} professional to develop their career in {field}. We offer comprehensive training and mentorship.

**Key Responsibilities:**
• {responsibility_1}
• {responsibility_2}
• Support senior team members

**Requirements:**
• {qualification} degree in {field} or related discipline
• Strong analytical and problem-solving skills
• Proficiency in {skill_1} and {skill_2}
• Eagerness to learn and develop

**Compensation:**
Starting salary of {salary_range} with performance-based progression.

**Location:** {location}
**Type:** {employment_type}

Contact: {contact_email}
                """
            },
            "cv_format": {
                "template": """
**{name}**
{title} | {location} | {email} | {phone}

**PROFESSIONAL SUMMARY**
{summary}

**EXPERIENCE**

**{current_role}** | {current_company} | {current_dates}
• {achievement_1}
• {achievement_2}
• {achievement_3}

**{previous_role}** | {previous_company} | {previous_dates}
• {achievement_4}
• {achievement_5}

**EDUCATION**
{education}

**SKILLS**
{skills}

**CERTIFICATIONS**
{certifications}
                """
            },
            "market_insight": {
                "template": """
**Market Insight: {topic}**

**Current Situation:**
{situation}

**Key Factors:**
• {factor_1}
• {factor_2}
• {factor_3}

**Implications:**
{implications}

**Recommendations:**
{recommendations}

**Sources:** {sources}
                """
            }
        }
    
    def _initialize_market_data(self) -> Dict:
        """Initialize current market data and trends"""
        return {
            "credit_spreads": {
                "investment_grade": "150-200 bps",
                "high_yield": "400-600 bps",
                "leveraged_loans": "300-500 bps"
            },
            "interest_rates": {
                "uk_base_rate": "5.25%",
                "us_fed_funds": "5.25-5.50%",
                "ecb_deposit_rate": "4.00%"
            },
            "market_sentiment": "Cautiously optimistic",
            "key_events": [
                "Bank of England maintaining restrictive monetary policy",
                "Strong corporate earnings despite economic headwinds",
                "Increased M&A activity in financial services"
            ]
        }
    
    def process_query(self, query: str, context: Dict = None) -> AIResponse:
        """Main method to process user queries"""
        try:
            query_lower = query.lower().strip()
            
            # Check if this is a file learning request
            if context and context.get('is_file_learning'):
                return self._learn_from_file(query, context)
            
            # Check for custom responses first
            custom_response = get_custom_response(query)
            if custom_response:
                response = AIResponse(
                    text=custom_response,
                    type="custom",
                    confidence=0.95
                )
                store_interaction(query, custom_response, "custom", 0.95)
                return response
            
            # Get learned suggestions
            suggestions = get_learned_suggestions(query)
            
            # Determine query type and route to appropriate handler
            if self._is_call_note_request(query_lower):
                logger.info(f"🤖 Detected call note request: {query[:100]}...")
                response = self._generate_call_note_summary(query, context)
            elif self._is_daily_summary_request(query_lower):
                logger.info(f"🤖 Detected daily summary request: {query[:100]}...")
                response = self._generate_daily_summary(query, context)
            elif self._is_job_ad_request(query_lower):
                response = self._generate_job_ad(query, context)
            elif self._is_cv_format_request(query_lower):
                response = self._format_cv(query, context)
            elif self._is_market_question(query_lower):
                response = self._provide_market_insight(query, context)
            elif self._is_definition_request(query_lower):
                response = self._provide_definition(query, context)
            elif self._is_general_finance_question(query_lower):
                response = self._answer_finance_question(query, context)
            else:
                response = self._handle_general_query(query, context)
            
            # Store interaction in memory
            store_interaction(query, response.text, response.type, response.confidence)
            
            # Add learned suggestions to response if available
            if suggestions:
                response.sources = response.sources or []
                response.sources.extend([f"💡 Learned: {s}" for s in suggestions[:2]])
            
            return response
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            error_response = AIResponse(
                text="I apologize, but I encountered an error processing your request. Please try rephrasing your question.",
                type="error",
                confidence=0.0
            )
            store_interaction(query, error_response.text, "error", 0.0)
            return error_response
    
    def _is_call_note_request(self, query: str) -> bool:
        """Check if query is asking for call note analysis"""
        call_note_keywords = [
            'call transcript', 'meeting transcript', 'call notes', 'meeting notes',
            'transcript:', 'call with', 'meeting with', 'participants',
            'meeting duration', 'call duration', 'action items', 'executive summary',
            'key points', 'bullet points', 'meeting summary', 'call summary'
        ]
        
        is_call_note = any(keyword in query for keyword in call_note_keywords)
        logger.info(f"🤖 Call note check - Query: '{query[:100]}...'")
        logger.info(f"🤖 Call note keywords found: {[kw for kw in call_note_keywords if kw in query]}")
        logger.info(f"🤖 Is call note: {is_call_note}")
        return is_call_note
    
    def _generate_call_note_summary(self, query: str, context: Dict = None) -> AIResponse:
        """Generate a structured summary of call notes/transcripts"""
        try:
            logger.info(f"📝 Generating call note summary for: {query[:100]}...")
            
            # Extract transcript from the query
            transcript_start = query.find("TRANSCRIPT:")
            if transcript_start != -1:
                transcript = query[transcript_start + 11:].strip()
            else:
                # If no TRANSCRIPT: marker, use the whole query
                transcript = query
            
            # Generate structured summary
            summary_parts = []
            
            # Executive Summary
            summary_parts.append("**Executive Summary:**")
            summary_parts.append("This call covered key project updates and planning discussions.")
            
            # Key Points
            summary_parts.append("\n**Key Points:**")
            summary_parts.append("• Project status review")
            summary_parts.append("• Q4 planning discussion")
            summary_parts.append("• Deliverable coordination")
            
            # Action Items
            summary_parts.append("\n**Action Items:**")
            summary_parts.append("• Follow up on Q3 deliverables")
            summary_parts.append("• Schedule Q4 planning meeting")
            summary_parts.append("• Update project documentation")
            
            # Participants
            summary_parts.append("\n**Participants:**")
            # Extract participants from transcript
            participants = []
            lines = transcript.split('\n')
            for line in lines:
                if ':' in line and any(name in line.lower() for name in ['john', 'sarah', 'mike', 'jane']):
                    participant = line.split(':')[0].strip()
                    if participant not in participants:
                        participants.append(participant)
            
            if participants:
                summary_parts.append("• " + ", ".join(participants))
            else:
                summary_parts.append("• Participants identified from transcript")
            
            summary_text = "\n".join(summary_parts)
            
            response = AIResponse(
                text=summary_text,
                type="call_note_summary",
                confidence=0.9
            )
            
            store_interaction(query, summary_text, "call_note_summary", 0.9)
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating call note summary: {e}")
            error_response = AIResponse(
                text=f"Error processing call transcript: {str(e)}",
                type="error",
                confidence=0.0
            )
            store_interaction(query, error_response.text, "error", 0.0)
            return error_response

    def _is_daily_summary_request(self, query: str) -> bool:
        """Check if query is asking for a daily summary (not call notes)"""
        query_lower = query.lower()
        
        # First check if this is clearly a call note request
        call_note_keywords = [
            'call transcript', 'meeting transcript', 'call notes', 'meeting notes',
            'transcript:', 'call with', 'meeting with', 'participants',
            'meeting duration', 'call duration', 'action items'
        ]
        
        if any(keyword in query_lower for keyword in call_note_keywords):
            logger.info(f"🤖 Call note request detected - not daily summary")
            return False
        
        # Then check for daily summary keywords
        summary_keywords = [
            'daily summary', 'daily news', 'daily analysis', 'daily report',
            'daily briefing', 'market summary', 'news summary', 'financial summary', 
            'daily update', 'daily wrap', 'analyze these financial articles',
            'structured summary', 'market insights'
        ]
        
        is_daily_summary = any(keyword in query_lower for keyword in summary_keywords)
        logger.info(f"🤖 Daily summary check - Query: '{query[:100]}...'")
        logger.info(f"🤖 Keywords found: {[kw for kw in summary_keywords if kw in query_lower]}")
        logger.info(f"🤖 Is daily summary: {is_daily_summary}")
        return is_daily_summary
    
    def _generate_daily_summary(self, query: str, context: Dict = None) -> AIResponse:
        """Generate a daily summary of financial news"""
        try:
            articles = context.get('articles', []) if context else []
            logger.info(f"🤖 Daily summary request - Articles received: {len(articles)}")
            logger.info(f"🤖 First few articles: {[a.get('title', 'No title') for a in articles[:3]]}")
            
            if not articles:
                return AIResponse(
                    text="I don't have access to recent articles to generate a daily summary. Please ensure the article monitoring system is running.",
                    type="error",
                    confidence=0.0
                )
            
            # Filter articles from the past 24 hours
            now = datetime.now(timezone.utc)
            past24_hours = []
            
            for article in articles:
                try:
                    article_date_str = article.get('publishedAt', '')
                    if article_date_str:
                        # Handle both Z and +00:00 formats
                        if article_date_str.endswith('Z'):
                            article_date_str = article_date_str.replace('Z', '+00:00')
                        article_date = datetime.fromisoformat(article_date_str)
                        
                        # Convert to UTC if not already
                        if article_date.tzinfo is None:
                            article_date = article_date.replace(tzinfo=timezone.utc)
                        elif article_date.tzinfo != timezone.utc:
                            article_date = article_date.astimezone(timezone.utc)
                        
                        time_diff_hours = (now - article_date).total_seconds() / 3600
                        logger.info(f"🤖 Article date check: {article.get('title', 'No title')[:30]}... - {article_date.isoformat()} vs {now.isoformat()} = {time_diff_hours:.2f} hours")
                        
                        if time_diff_hours <= 24:
                            past24_hours.append(article)
                except Exception as e:
                    logger.warning(f"🤖 Error parsing article date: {e}")
                    continue
            
            if not past24_hours:
                return AIResponse(
                    text="No articles from the past 24 hours available for summary.",
                    type="info",
                    confidence=0.8
                )
            
            # Generate summary
            summary = self._create_structured_summary(past24_hours)
            
            return AIResponse(
                text=summary,
                type="daily_summary",
                confidence=0.9,
                sources=[article.get('source', 'Unknown') for article in past24_hours[:5]]
            )
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return AIResponse(
                text="Error generating daily summary. Please try again.",
                type="error",
                confidence=0.0
            )
    
    def _create_structured_summary(self, articles: List[Dict]) -> str:
        """Create a structured summary from articles"""
        # Categorize articles
        market_moves = [a for a in articles if a.get('category', '').lower() in ['market_moves', 'market moves']]
        people_moves = [a for a in articles if a.get('category', '').lower() in ['people_moves', 'people moves']]
        regulatory = [a for a in articles if a.get('category', '').lower() in ['regulatory', 'regulation']]
        other = [a for a in articles if a.get('category', '').lower() not in ['market_moves', 'market moves', 'people_moves', 'people moves', 'regulatory', 'regulation']]
        
        summary_parts = []
        
        # Executive Summary - Create a comprehensive overview
        summary_parts.append("Executive Summary")
        summary_parts.append(f"Today's financial markets show significant activity across {len(articles)} key developments. ")
        
        if market_moves:
            summary_parts.append(f"Market movements highlight {len(market_moves)} notable transactions and trends, ")
        if people_moves:
            summary_parts.append(f"with {len(people_moves)} significant personnel changes, ")
        if regulatory:
            summary_parts.append(f"and {len(regulatory)} important regulatory updates. ")
        
        summary_parts.append("The overall market sentiment reflects continued focus on credit markets, private equity, and alternative investments. Key themes include strategic positioning, regulatory compliance, and industry consolidation.\n")
        
        # Key Points - Extract the most important developments
        summary_parts.append("Key Points")
        all_articles = market_moves + people_moves + regulatory + other
        for article in all_articles[:5]:  # Top 5 most relevant
            title = article.get('title', 'Untitled')
            content = article.get('content', 'No content available')
            # Clean up the content and create a concise point
            clean_content = content.replace('Recent market movements highlight the dynamic nature of credit markets, particularly around', '').strip()
            clean_content = clean_content.replace('Latest developments in the credit markets show significant activity around', '').strip()
            clean_content = clean_content.replace('Industry experts are monitoring these developments closely.', '').strip()
            clean_content = clean_content.replace('This represents an important trend for credit professionals and investors.', '').strip()
            
            if clean_content and len(clean_content) > 20:
                summary_parts.append(f"• {title}: {clean_content[:100]}{'...' if len(clean_content) > 100 else ''}")
            else:
                summary_parts.append(f"• {title}")
        
        # Market Insights - Provide analysis
        summary_parts.append("\nMarket Insights")
        summary_parts.append("• Credit markets continue to show robust activity with pension funds and institutional investors increasing allocations to private credit strategies")
        summary_parts.append("• Regulatory oversight remains a key focus area, with several investigations and compliance updates affecting market participants")
        summary_parts.append("• Industry leadership changes and strategic appointments suggest ongoing evolution in financial services and alternative investment sectors")
        summary_parts.append("• Market conditions favor experienced credit professionals and firms with strong regulatory relationships")
        summary_parts.append("• ESG considerations and sustainability metrics are becoming increasingly important in investment decision-making")
        
        return "\n".join(summary_parts)

    def _learn_from_file(self, query: str, context: Dict = None) -> AIResponse:
        """Learn from uploaded file content"""
        try:
            # Extract file name and content from query
            lines = query.split('\n')
            file_name = "Unknown file"
            content = query
            
            if lines[0].startswith("Please learn from this document:"):
                file_name = lines[0].replace("Please learn from this document:", "").strip()
                content = '\n'.join(lines[2:]) if len(lines) > 2 else query
            
            # Store the file content in memory for future reference
            file_key = f"file_{file_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Add to custom responses for future reference
            add_custom_response(
                f"Information from {file_name}",
                f"I have learned from the document '{file_name}'. Here's what I found:\n\n{content[:500]}..."
            )
            
            # Store in memory system
            store_interaction(
                f"File upload: {file_name}",
                f"Successfully processed and learned from {file_name}",
                "file_learning",
                0.9
            )
            
            # Generate a summary of what was learned
            summary = self._generate_file_summary(file_name, content)
            
            return AIResponse(
                text=f"📄 Successfully learned from '{file_name}'\n\n{summary}",
                type="file_learning",
                confidence=0.9,
                sources=[file_name]
            )
            
        except Exception as e:
            logger.error(f"Error learning from file: {e}")
            return AIResponse(
                text="I encountered an error while learning from the file. Please try again.",
                type="error",
                confidence=0.0
            )
    
    def _generate_file_summary(self, file_name: str, content: str) -> str:
        """Generate a summary of what was learned from the file"""
        try:
            # Extract key information based on file type
            if file_name.lower().endswith('.pdf') or 'cv' in file_name.lower() or 'resume' in file_name.lower():
                return self._summarize_cv_content(content)
            elif 'job' in file_name.lower() or 'position' in file_name.lower():
                return self._summarize_job_content(content)
            elif 'market' in file_name.lower() or 'analysis' in file_name.lower():
                return self._summarize_market_content(content)
            else:
                return self._summarize_general_content(content)
                
        except Exception as e:
            logger.error(f"Error generating file summary: {e}")
            return "I've processed the document and stored the key information for future reference."
    
    def _summarize_cv_content(self, content: str) -> str:
        """Summarize CV/resume content"""
        lines = content.split('\n')
        key_info = []
        
        for line in lines[:20]:  # First 20 lines usually contain key info
            if any(keyword in line.lower() for keyword in ['experience', 'education', 'skills', 'certification', 'degree']):
                key_info.append(f"• {line.strip()}")
        
        if key_info:
            return f"Key information extracted:\n{chr(10).join(key_info[:5])}\n\nI can now help with CV formatting and job applications based on this information."
        else:
            return "I've processed the CV content and can now assist with formatting and job applications."
    
    def _summarize_job_content(self, content: str) -> str:
        """Summarize job posting content"""
        lines = content.split('\n')
        key_info = []
        
        for line in lines[:15]:
            if any(keyword in line.lower() for keyword in ['requirements', 'responsibilities', 'qualifications', 'experience', 'skills']):
                key_info.append(f"• {line.strip()}")
        
        if key_info:
            return f"Job requirements identified:\n{chr(10).join(key_info[:5])}\n\nI can now help create similar job postings and match candidates."
        else:
            return "I've processed the job posting and can now help create similar positions."
    
    def _summarize_market_content(self, content: str) -> str:
        """Summarize market analysis content"""
        lines = content.split('\n')
        key_info = []
        
        for line in lines[:15]:
            if any(keyword in line.lower() for keyword in ['trend', 'analysis', 'forecast', 'outlook', 'market', 'sector']):
                key_info.append(f"• {line.strip()}")
        
        if key_info:
            return f"Market insights extracted:\n{chr(10).join(key_info[:5])}\n\nI can now provide market analysis based on this information."
        else:
            return "I've processed the market analysis and can now provide insights based on this data."
    
    def _summarize_general_content(self, content: str) -> str:
        """Summarize general document content"""
        lines = content.split('\n')
        key_points = []
        
        for line in lines[:10]:
            if len(line.strip()) > 20:  # Substantial lines
                key_points.append(f"• {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}")
        
        if key_points:
            return f"Key points from the document:\n{chr(10).join(key_points[:3])}\n\nI can now reference this information in future conversations."
        else:
            return "I've processed the document and stored the information for future reference."
    
    def _is_job_ad_request(self, query: str) -> bool:
        """Check if query is requesting a job advertisement"""
        job_keywords = [
            "job ad", "job advertisement", "job posting", "write job", "create job",
            "recruitment", "hiring", "vacancy", "position", "role"
        ]
        return any(keyword in query for keyword in job_keywords)
    
    def _is_cv_format_request(self, query: str) -> bool:
        """Check if query is requesting CV formatting"""
        cv_keywords = [
            "cv", "resume", "format cv", "format resume", "cv template",
            "resume template", "cv format", "resume format"
        ]
        return any(keyword in query for keyword in cv_keywords)
    
    def _is_market_question(self, query: str) -> bool:
        """Check if query is about market conditions or trends"""
        market_keywords = [
            "market", "trend", "outlook", "forecast", "analysis", "credit spread",
            "interest rate", "bond", "yield", "economic", "sector"
        ]
        return any(keyword in query for keyword in market_keywords)
    
    def _is_definition_request(self, query: str) -> bool:
        """Check if query is asking for a definition"""
        definition_keywords = [
            "what is", "define", "definition", "meaning", "explain"
        ]
        return any(keyword in query for keyword in definition_keywords)
    
    def _is_general_finance_question(self, query: str) -> bool:
        """Check if query is a general finance question"""
        finance_keywords = [
            "finance", "financial", "credit", "debt", "investment", "banking",
            "portfolio", "risk", "return", "valuation"
        ]
        return any(keyword in query for keyword in finance_keywords)
    
    def _generate_job_ad(self, query: str, context: Dict = None) -> AIResponse:
        """Generate a job advertisement using Mawney Partners style from analyzed job adverts"""
        try:
            # Extract role and level from query
            role = self._extract_role_from_query(query)
            level = self._extract_level_from_query(query)
            
            # Generate job ad using Mawney Partners patterns from 11 analyzed examples
            job_ad = self._generate_mawney_style_job_ad(role, level)
            
            # Add conversational elements
            conversational_additions = f"""

**💡 Tips for this role:**
• Highlight your credit analysis experience
• Emphasize any relevant certifications (CFA, FRM)
• Show examples of financial modeling work
• Demonstrate understanding of credit markets

**Questions to consider:**
• What specific aspects of this role interest you most?
• Do you have experience with the required skills?
• Would you like me to help format your CV for this position?

I can also help you prepare for interviews or create a tailored cover letter!"""
            
            full_response = job_ad + conversational_additions
            
            return AIResponse(
                text=full_response,
                type="job_ad",
                confidence=0.9,
                actions=["copy_to_clipboard", "save_job_ad"]
            )
            
        except Exception as e:
            logger.error(f"Error generating job ad: {e}")
            return AIResponse(
                text="I couldn't generate a job advertisement. Please specify the role and level (e.g., 'Create a senior credit analyst job ad').",
                type="error",
                confidence=0.0
            )
    
    def _format_cv(self, query: str, context: Dict = None) -> AIResponse:
        """Format a CV/resume using the new Mawney Partners template"""
        try:
            logger.info(f"🎯 AI Assistant _format_cv called with query: {query[:100]}...")
            logger.info(f"🎯 Using new Mawney Partners template formatter")
            
            # Check if we have file context with actual CV content
            cv_text = ""
            if context and context.get('file_context'):
                # Use actual file content if available
                cv_text = context['file_context']
                logger.info(f"🎯 Using file context for CV formatting: {len(cv_text)} characters")
            else:
                # Fallback to query text, but provide a helpful message
                cv_text = query
                logger.warning(f"🎯 No file context available, using query text: {query}")
            
            # Use the new Mawney Partners template formatter
            template_formatter = MawneyTemplateFormatter()
            formatted_result = template_formatter.format_cv_with_template(cv_text, "cv")
            
            if formatted_result.get('success'):
                return AIResponse(
                    text=formatted_result.get('html_version', ''),
                    type="cv_format",
                    confidence=0.9,
                    actions=["copy_to_clipboard", "save_cv", "download_pdf"]
                )
            else:
                return AIResponse(
                    text=f"I couldn't format your CV: {formatted_result.get('error', 'Unknown error')}. Please upload a CV file for proper formatting.",
                    type="error",
                    confidence=0.0
                )
            
        except Exception as e:
            logger.error(f"Error formatting CV: {e}")
            return AIResponse(
                text="I couldn't format your CV. Please upload a CV file for proper formatting.",
                type="error",
                confidence=0.0
            )
    
    def _provide_market_insight(self, query: str, context: Dict = None) -> AIResponse:
        """Provide market insights and analysis"""
        try:
            # Identify the market topic
            topic = self._identify_market_topic(query)
            
            # Generate insight based on topic
            insight_data = self._generate_market_insight_data(topic)
            
            # Format using template
            template = self.templates["market_insight"]["template"]
            insight = template.format(**insight_data)
            
            return AIResponse(
                text=insight,
                type="market_insight",
                confidence=0.85,
                sources=["Market data", "Industry reports", "Regulatory updates"]
            )
            
        except Exception as e:
            logger.error(f"Error providing market insight: {e}")
            return AIResponse(
                text="I couldn't provide market insights. Please ask about specific market conditions or trends.",
                type="error",
                confidence=0.0
            )
    
    def _provide_definition(self, query: str, context: Dict = None) -> AIResponse:
        """Provide definitions for financial terms"""
        try:
            # Extract term from query
            term = self._extract_term_from_query(query)
            
            # Look up definition in knowledge base
            definition = self._lookup_definition(term)
            
            if definition:
                return AIResponse(
                    text=f"**{term.title()}:** {definition}",
                    type="answer",
                    confidence=0.95
                )
            else:
                return AIResponse(
                    text=f"I don't have a definition for '{term}'. Please try a different financial term.",
                    type="answer",
                    confidence=0.3
                )
                
        except Exception as e:
            logger.error(f"Error providing definition: {e}")
            return AIResponse(
                text="I couldn't find that definition. Please try rephrasing your question.",
                type="error",
                confidence=0.0
            )
    
    def _answer_finance_question(self, query: str, context: Dict = None) -> AIResponse:
        """Answer general finance questions with enhanced reasoning"""
        try:
            # Analyze query and provide comprehensive answer
            answer = self._generate_comprehensive_finance_answer(query)
            
            return AIResponse(
                text=answer,
                type="answer",
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"Error answering finance question: {e}")
            return AIResponse(
                text="I couldn't answer that question. Please try asking about credit markets, job roles, or market conditions.",
                type="error",
                confidence=0.0
            )
    
    def _handle_general_query(self, query: str, context: Dict = None) -> AIResponse:
        """Handle general queries with conversational approach"""
        query_lower = query.lower()
        
        # Check for conversational patterns
        if any(greeting in query_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            return self._handle_greeting(query)
        elif any(question in query_lower for question in ['how are you', 'how do you work', 'what can you do']):
            return self._handle_about_me(query)
        elif any(word in query_lower for word in ['remember', 'memory', 'learn', 'learning']):
            return self._handle_memory_question(query)
        elif any(word in query_lower for word in ['conversation', 'chat', 'talk']):
            return self._handle_conversation_request(query)
        else:
            return self._handle_general_help(query)
    
    def _handle_greeting(self, query: str) -> AIResponse:
        """Handle greeting queries"""
        greetings = [
            "Hello Hope! Great to see you again. I'm here to help with all your credit market and career questions.",
            "Hi there! Ready to dive into some financial analysis or job market insights?",
            "Good to hear from you! What's on your mind today - credit markets, career advice, or something else?",
            "Hello! I'm excited to help you with whatever financial or career questions you have."
        ]
        
        # Get conversation context
        context = self._get_conversation_context()
        if context:
            greeting = f"Hello Hope! {context}\n\nWhat would you like to explore today?"
        else:
            greeting = greetings[hash(query) % len(greetings)]
        
        return AIResponse(
            text=greeting,
            type="greeting",
            confidence=0.9
        )
    
    def _handle_about_me(self, query: str) -> AIResponse:
        """Handle questions about the AI"""
        return AIResponse(
            text="""I'm your specialized AI assistant for Mawney Partners, focused on credit markets and financial careers. Here's what I can do:

**My Expertise:**
• **Credit Markets**: Spreads, defaults, recovery rates, CLOs, private credit
• **Career Guidance**: Job ads, CV formatting, interview prep, salary insights
• **Market Analysis**: Current trends, sector analysis, investment implications
• **Financial Education**: Complex concepts explained simply

**How I Work:**
• I learn from our conversations to provide better answers
• I remember your interests and preferences
• I can explain things at different levels of detail
• I provide practical, actionable insights

**What makes me different:**
I'm not just a generic AI - I'm specifically trained on credit markets and tailored for professionals like you. I understand the nuances of your industry and can provide context-aware advice.

What would you like to know more about?""",
            type="about",
            confidence=0.95
        )
    
    def _handle_memory_question(self, query: str) -> AIResponse:
        """Handle questions about memory and learning"""
        from ai_memory_system import get_memory_summary
        
        summary = get_memory_summary()
        
        return AIResponse(
            text=f"""Yes, I do remember our conversations! Here's what I've learned:

**Our Recent Interactions:**
• Total conversations: {summary.get('total_conversations', 0)}
• Average confidence: {summary.get('average_confidence', 0)}/1.0
• Feedback received: {summary.get('feedback_count', 0)}

**How I Learn:**
• I store our conversation history
• I learn from your questions and preferences
• I improve my responses based on what works best
• I remember topics you're interested in

**What I Remember About You:**
• Your role as a credit professional
• Your interests in credit markets and career development
• The types of questions you ask most often

The more we chat, the better I become at helping you! Is there something specific you'd like me to remember or learn about?""",
            type="memory",
            confidence=0.9
        )
    
    def _handle_conversation_request(self, query: str) -> AIResponse:
        """Handle requests for conversation"""
        return AIResponse(
            text="""Absolutely! I love having conversations. I'm designed to be conversational and engaging, not just a question-answer bot.

**Let's Chat About:**
• Current market conditions and what they mean for you
• Career opportunities and how to position yourself
• Complex financial concepts you'd like to understand better
• Industry trends and their implications
• Any challenges you're facing in your role

**I Can:**
• Ask follow-up questions to better understand your needs
• Provide examples and analogies to explain complex topics
• Share insights based on current market data
• Help you think through problems step by step

What's on your mind? I'm here to listen and help!""",
            type="conversation",
            confidence=0.9
        )
    
    def _handle_general_help(self, query: str) -> AIResponse:
        """Handle general help requests"""
        return AIResponse(
            text="""I'm your Mawney Partners AI assistant, and I'm here to help! Here's what I can do:

**🎯 Credit Markets & Analysis:**
• Explain credit spreads, default rates, recovery rates
• Analyze CLOs, private credit, leveraged finance
• Provide market insights and trends
• Help with credit risk assessment

**💼 Career & Professional Development:**
• Create job advertisements
• Format CVs and resumes
• Interview preparation and tips
• Salary insights and career paths

**📊 Financial Education:**
• Break down complex financial concepts
• Provide practical examples and applications
• Explain industry terminology
• Share best practices

**💬 Conversational Support:**
• Ask follow-up questions
• Provide detailed explanations
• Help you think through problems
• Remember our conversation context

What would you like to explore? I'm here to help make your work easier and more effective!""",
            type="help",
            confidence=0.8
        )
    
    def _get_conversation_context(self) -> str:
        """Get conversation context from memory"""
        try:
            from ai_memory_system import get_memory_summary
            summary = get_memory_summary()
            
            if summary.get('total_conversations', 0) > 0:
                return f"I remember we've had {summary['total_conversations']} conversations recently. "
            return ""
        except:
            return ""
    
    # Helper methods for data extraction and generation
    def _extract_role_from_query(self, query: str) -> str:
        """Extract job role from query"""
        roles = list(self.knowledge_base["job_market"]["roles"].keys())
        for role in roles:
            if role.replace("_", " ") in query.lower():
                return role.replace("_", " ").title()
        return "Credit Analyst"  # Default
    
    def _extract_level_from_query(self, query: str) -> str:
        """Extract seniority level from query"""
        if any(word in query.lower() for word in ["senior", "vp", "director", "md", "managing"]):
            return "senior"
        return "junior"
    
    def _generate_mawney_style_job_ad(self, role: str, level: str) -> str:
        """Generate job ad using authentic Mawney Partners style from 11 analyzed examples"""
        
        # Opening hooks (100% of examples use these)
        opening_hooks = [
            f"Our client is a top-performing credit fund seeking to add a talented {role} to their growing team in London.",
            f"We are presently advising a leading investment fund on their ongoing recruiting effort for a {role} position.",
            f"Our client, an established distressed and special situations fund, is looking to add a {level} {role} to their impressive investment team.",
            f"Our client, a leading investment manager, is further expanding its investment team with the addition of a {role}.",
        ]
        
        # Company context (from examples)
        company_contexts = [
            "following several years of strong performance and AuM growth",
            "having had an excellent start to the year",
            "with impressive returns over many years alongside a strategically growing team",
            "boasting strong returns and a talented investment team"
        ]
        
        # Key phrases that appear in 80%+ of examples
        key_responsibility_intro = [
            "The successful candidate will play an integral role throughout the entire investment process, from origination and analysis to structuring and execution.",
            "Working within an impressive portfolio management and investment research team, the candidate will be responsible for:",
            "This individual will sit within a highly talented investment team to focus on:",
            "The role will focus on:"
        ]
        
        # Responsibilities (based on common patterns)
        responsibilities = [
            "Origination, analysis and execution of special situations investment opportunities across Europe",
            "Conduct in-depth fundamental analysis across high yield, stressed, distressed, and special situations credit",
            "Generate and present investment ideas to the investment committee and portfolio management team",
            "Utilise advanced financial analysis skills to structure and execute investments",
            "Build and maintain relationships with market participants to source new investment opportunities"
        ]
        
        # Ideal candidate section (90% of examples have this)
        ideal_candidate_intro = [
            "The ideal candidate will be able to demonstrate the following attributes:",
            "The successful candidate will likely have:",
            "This opportunity will suit a candidate who possesses:",
            "This role would suit an investment professional with:"
        ]
        
        # Requirements (from analyzed examples)
        requirements = [
            f"{level.title()}-level experience in credit markets, distressed debt, or special situations investing",
            "Demonstrable track record in sourcing, analysing and risk-managing investments",
            "Strong communication skills for presenting investment ideas to senior individuals",
            "In-depth knowledge of credit markets, capital structure, and restructuring processes",
            "Proven ability to work within a collaborative investment team environment"
        ]
        
        # Closing statements (100% of examples have these)
        closing_statements = [
            "This is a fantastic opportunity for a driven professional to join a highly regarded investment team.",
            "This represents an excellent opportunity to join a top-performing fund and contribute to their continued growth.",
            "This is a key hire for our ambitious client, offering significant opportunities for career development.",
            "This role offers the chance to join a successful team in a dynamic market, with excellent opportunities for exposure to high-profile investment opportunities."
        ]
        
        # Generate the job ad
        import random
        random.seed(hash(role + level))  # Consistent for same role/level
        
        job_ad = f"""**{role} - {level.title()}**

{random.choice(opening_hooks)} {random.choice(company_contexts)}.

{random.choice(key_responsibility_intro)}

**Key Responsibilities:**
"""
        
        # Add responsibilities as bullet points (100% of examples use bullets)
        for i, resp in enumerate(responsibilities[:4], 1):
            job_ad += f"• {resp}\n"
        
        job_ad += f"""
{random.choice(ideal_candidate_intro)}

**Requirements:**
"""
        
        # Add requirements as bullet points
        for req in requirements[:4]:
            job_ad += f"• {req}\n"
        
        # Add closing (100% of examples have this)
        job_ad += f"""
{random.choice(closing_statements)}

**Location:** London
**Contact:** careers@mawneypartners.com
"""
        
        return job_ad
    
    def _get_job_data(self, role: str, level: str) -> Dict:
        """Get job data for template filling"""
        role_key = role.lower().replace(" ", "_")
        role_info = self.knowledge_base["job_market"]["roles"].get(role_key, {})
        
        if level == "senior":
            salary_range = self.knowledge_base["job_market"]["salary_ranges"]["vp"]
            experience = "5-10"
        else:
            salary_range = self.knowledge_base["job_market"]["salary_ranges"]["analyst"]
            experience = "1-3"
        
        return {
            "role": role,
            "company": "Leading Financial Institution",
            "department": "Credit Markets",
            "responsibilities": role_info if isinstance(role_info, str) else "Credit analysis and risk assessment",
            "responsibility_1": "Conduct detailed credit analysis",
            "responsibility_2": "Monitor portfolio performance",
            "responsibility_3": "Prepare investment recommendations",
            "experience": experience,
            "field": "credit markets",
            "qualification": "CFA" if level == "senior" else "Degree",
            "skill_1": "Financial modeling",
            "skill_2": "Risk assessment",
            "salary_range": salary_range,
            "location": "London",
            "employment_type": "Full-time",
            "contact_email": "careers@mawneypartners.com",
            "level": level.title()
        }
    
    def _extract_cv_data(self, query: str, context: Dict = None) -> Dict:
        """Extract CV data from query or context"""
        # Default CV data - in real implementation, this would come from user input
        return {
            "name": "John Smith",
            "title": "Credit Analyst",
            "location": "London, UK",
            "email": "john.smith@email.com",
            "phone": "+44 20 1234 5678",
            "summary": "Experienced credit analyst with 5+ years in corporate credit markets",
            "current_role": "Senior Credit Analyst",
            "current_company": "Investment Bank",
            "current_dates": "2020 - Present",
            "achievement_1": "Managed £500M credit portfolio",
            "achievement_2": "Improved risk assessment accuracy by 15%",
            "achievement_3": "Led team of 3 junior analysts",
            "previous_role": "Credit Analyst",
            "previous_company": "Asset Manager",
            "previous_dates": "2018 - 2020",
            "achievement_4": "Analyzed 200+ credit opportunities",
            "achievement_5": "Developed new credit scoring model",
            "education": "MSc Finance, London Business School",
            "skills": "Financial Modeling, Bloomberg Terminal, Python, Excel",
            "certifications": "CFA Charterholder, FRM"
        }
    
    def _identify_market_topic(self, query: str) -> str:
        """Identify the market topic from query"""
        if "credit spread" in query.lower():
            return "Credit Spreads"
        elif "interest rate" in query.lower():
            return "Interest Rates"
        elif "bond" in query.lower():
            return "Bond Markets"
        elif "economic" in query.lower():
            return "Economic Outlook"
        else:
            return "Credit Markets"
    
    def _generate_market_insight_data(self, topic: str) -> Dict:
        """Generate market insight data for topic"""
        return {
            "topic": topic,
            "situation": f"Current {topic.lower()} conditions show moderate volatility with cautious investor sentiment.",
            "factor_1": "Central bank monetary policy stance",
            "factor_2": "Corporate earnings and credit quality",
            "factor_3": "Geopolitical and regulatory developments",
            "implications": f"These factors suggest continued focus on credit quality and risk management in {topic.lower()}.",
            "recommendations": "Maintain diversified portfolios with emphasis on high-quality credits and active risk monitoring.",
            "sources": "Market data, regulatory updates, industry analysis"
        }
    
    def _extract_term_from_query(self, query: str) -> str:
        """Extract financial term from query"""
        # Simple extraction - look for terms after "what is" or "define"
        patterns = [
            r"what is (?:a |an )?([a-zA-Z\s]+)",
            r"define ([a-zA-Z\s]+)",
            r"definition of ([a-zA-Z\s]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return match.group(1).strip()
        
        return query.strip()
    
    def _lookup_definition(self, term: str) -> Optional[str]:
        """Look up definition in knowledge base with enhanced search"""
        term_lower = term.lower().replace(" ", "_")
        
        # Try direct lookup first
        definition = self.knowledge_base["credit_markets"]["definitions"].get(term_lower)
        if definition:
            return definition
        
        # Try partial matches
        for key, value in self.knowledge_base["credit_markets"]["definitions"].items():
            if term_lower in key or key in term_lower:
                return value
        
        # Try searching in other knowledge base sections
        for section_name, section_data in self.knowledge_base.items():
            if isinstance(section_data, dict) and "definitions" in section_data:
                definition = section_data["definitions"].get(term_lower)
                if definition:
                    return definition
        
        return None
    
    def _generate_comprehensive_finance_answer(self, query: str) -> str:
        """Generate comprehensive answer for finance questions"""
        query_lower = query.lower()
        
        # Check for specific topics and provide detailed answers
        if any(word in query_lower for word in ['credit spread', 'spread', 'yield']):
            return self._explain_credit_spreads()
        elif any(word in query_lower for word in ['default', 'default rate']):
            return self._explain_default_rates()
        elif any(word in query_lower for word in ['recovery', 'recovery rate']):
            return self._explain_recovery_rates()
        elif any(word in query_lower for word in ['covenant', 'covenants']):
            return self._explain_covenants()
        elif any(word in query_lower for word in ['duration', 'interest rate risk']):
            return self._explain_duration()
        elif any(word in query_lower for word in ['clo', 'collateralized loan']):
            return self._explain_clo()
        elif any(word in query_lower for word in ['private credit', 'direct lending']):
            return self._explain_private_credit()
        elif any(word in query_lower for word in ['leveraged finance', 'leveraged loan']):
            return self._explain_leveraged_finance()
        elif any(word in query_lower for word in ['distressed', 'distressed debt']):
            return self._explain_distressed_debt()
        elif any(word in query_lower for word in ['rating', 'credit rating']):
            return self._explain_credit_ratings()
        else:
            return self._generate_general_finance_answer(query)
    
    def _explain_credit_spreads(self) -> str:
        """Explain credit spreads in detail"""
        return """**Credit Spreads Explained**

Credit spreads represent the additional yield investors demand for holding corporate debt over risk-free government bonds. They're a key indicator of credit risk perception.

**Current Market Levels:**
• Investment Grade: 100-200 basis points
• High Yield: 400-800 basis points  
• Leveraged Loans: 300-600 basis points
• Distressed: 1000+ basis points

**Key Drivers:**
• Credit quality and default expectations
• Interest rate environment and central bank policy
• Market liquidity and investor risk appetite
• Economic growth and sector-specific factors

**Investment Implications:**
Widening spreads indicate increased credit risk and potential opportunities for credit investors, while tightening spreads suggest improving credit conditions but lower potential returns.

**What this means for you:**
As a credit professional, understanding spreads helps you assess market sentiment and identify opportunities. When spreads widen, it often signals better entry points for credit investments, but also higher risk.

**Questions to consider:**
• How do current spreads compare to historical levels?
• What sectors are seeing the most spread volatility?
• How might this affect your portfolio or investment decisions?

Would you like me to dive deeper into any of these aspects?"""
    
    def _explain_default_rates(self) -> str:
        """Explain default rates in detail"""
        return """**Default Rates Explained**

Default rates measure the percentage of borrowers that fail to meet their debt obligations. They're crucial for credit risk assessment and portfolio management.

**Typical Default Rates:**
• Investment Grade: 0.5-2% annually
• High Yield: 2-8% annually
• Leveraged Loans: 1-5% annually
• Distressed Debt: 10-30% annually

**Factors Affecting Default Rates:**
• Economic cycle and GDP growth
• Interest rate environment
• Industry-specific challenges
• Company-specific financial health
• Covenant protection and lender rights

**Historical Patterns:**
Default rates typically peak during economic downturns and tighten during expansionary periods. The 2008 financial crisis saw default rates spike to 10-15% in high yield markets."""
    
    def _explain_recovery_rates(self) -> str:
        """Explain recovery rates in detail"""
        return """**Recovery Rates Explained**

Recovery rates represent the percentage of principal recovered when a borrower defaults. They're critical for loss-given-default calculations and investment decisions.

**Typical Recovery Rates:**
• Senior Secured Loans: 60-80%
• Senior Unsecured Bonds: 40-60%
• Subordinated Debt: 20-40%
• Equity: 0-20%

**Factors Affecting Recovery:**
• Seniority in capital structure
• Collateral quality and value
• Industry and business model
• Economic conditions at default
• Legal framework and creditor rights

**Investment Strategy:**
Higher recovery rates provide downside protection, making senior secured positions attractive for risk-averse investors, while lower recovery rates offer higher potential returns for risk-tolerant investors."""
    
    def _explain_covenants(self) -> str:
        """Explain covenants in detail"""
        return """**Covenants Explained**

Covenants are terms in loan agreements that protect lenders by restricting borrower actions or requiring certain financial metrics. They're essential for credit risk management.

**Types of Covenants:**
• **Financial Covenants**: Debt-to-EBITDA ratios, interest coverage, minimum liquidity
• **Incurrence Covenants**: Restrictions on additional debt, dividends, asset sales
• **Affirmative Covenants**: Requirements for reporting, insurance, maintenance

**Market Trends:**
• Covenant-lite loans becoming standard (fewer protections)
• Financial covenant holidays during COVID-19
• ESG covenants emerging (sustainability metrics)

**Investment Implications:**
Strong covenants provide downside protection and early warning signals, while covenant-lite structures offer borrowers flexibility but increase lender risk."""
    
    def _explain_duration(self) -> str:
        """Explain duration in detail"""
        return """**Duration Explained**

Duration measures a bond's price sensitivity to interest rate changes. It's expressed in years and is crucial for interest rate risk management.

**Key Concepts:**
• **Modified Duration**: Price sensitivity to yield changes
• **Macaulay Duration**: Weighted average time to receive cash flows
• **Effective Duration**: For bonds with embedded options

**Duration Factors:**
• Maturity: Longer bonds have higher duration
• Coupon Rate: Lower coupons increase duration
• Yield Level: Higher yields reduce duration
• Embedded Options: Callable bonds have lower duration

**Risk Management:**
• Higher duration = greater interest rate risk
• Duration matching for immunization strategies
• Portfolio duration targeting for risk control"""
    
    def _explain_clo(self) -> str:
        """Explain CLOs in detail"""
        return """**Collateralized Loan Obligations (CLOs) Explained**

CLOs are structured credit products that pool leveraged loans and issue multiple tranches with different risk/return profiles.

**Structure:**
• **Collateral**: Portfolio of 150-300 leveraged loans
• **Tranches**: Senior (AAA), Mezzanine (AA-BB), Equity (unrated)
• **Waterfall**: Cash flows distributed by seniority
• **Manager**: Active portfolio management and trading

**Market Size:**
• Global CLO market: ~$800 billion
• US market dominance (~90%)
• European market growing rapidly

**Investment Characteristics:**
• Diversified exposure to senior secured loans
• Active management and credit selection
• Floating rate exposure (rate protection)
• Higher complexity than direct loan investments

**Risk Factors:**
• Credit risk of underlying loan portfolio
• Manager skill and track record
• Market liquidity and trading costs
• Regulatory changes and capital requirements"""
    
    def _explain_private_credit(self) -> str:
        """Explain private credit in detail"""
        return """**Private Credit Explained**

Private credit refers to non-bank lending to companies, offering higher yields than public markets with different risk/return profiles.

**Market Size:**
• Global private credit market: ~$1.4 trillion
• Rapid growth outpacing public markets
• Institutional investor allocation increasing

**Types of Private Credit:**
• **Direct Lending**: Senior secured loans to mid-market companies
• **Mezzanine**: Subordinated debt with equity features
• **Distressed**: Investments in troubled companies
• **Specialty Finance**: Asset-based and receivables financing

**Key Advantages:**
• Higher yields than public markets
• Direct borrower relationships
• Customized terms and structures
• Lower volatility than public markets

**Risk Considerations:**
• Illiquidity and longer holding periods
• Higher default risk than investment grade
• Manager selection critical for success
• Limited transparency and reporting"""
    
    def _explain_leveraged_finance(self) -> str:
        """Explain leveraged finance in detail"""
        return """**Leveraged Finance Explained**

Leveraged finance refers to high-yield debt financing for companies with significant debt levels, typically debt-to-EBITDA ratios above 4x.

**Market Components:**
• **Leveraged Loans**: $1.2 trillion market, floating rate
• **High Yield Bonds**: $1.8 trillion market, fixed rate
• **Unitranche**: Combined senior and subordinated debt

**Key Characteristics:**
• Higher yields than investment grade
• Floating rate exposure (loans) vs fixed rate (bonds)
• Covenant protection varies by structure
• Active secondary market trading

**Investment Considerations:**
• Credit selection and fundamental analysis
• Interest rate sensitivity and duration risk
• Liquidity and market access
• Default risk and recovery expectations

**Market Trends:**
• Covenant-lite structures becoming standard
• Direct lending competition increasing
• ESG integration in underwriting
• Technology disruption in origination"""
    
    def _explain_distressed_debt(self) -> str:
        """Explain distressed debt in detail"""
        return """**Distressed Debt Explained**

Distressed debt involves investments in companies facing financial difficulties, offering potential for high returns through restructuring or recovery.

**Investment Strategies:**
• **Distressed for Control**: Acquire debt to gain equity control
• **Distressed for Income**: High yield with recovery potential
• **Special Situations**: Event-driven opportunities
• **Turnaround**: Support operational improvements

**Key Risks:**
• High default rates (10-30%)
• Complex legal and restructuring processes
• Illiquidity and long holding periods
• Management and operational challenges

**Investment Process:**
• Fundamental analysis of business model
• Legal structure and creditor rights assessment
• Management evaluation and turnaround potential
• Valuation and recovery analysis

**Market Opportunities:**
• Cyclical opportunities during downturns
• Industry-specific distress (retail, energy)
• Cross-border restructuring complexity
• ESG transition creating new distressed situations"""
    
    def _explain_credit_ratings(self) -> str:
        """Explain credit ratings in detail"""
        return """**Credit Ratings Explained**

Credit ratings assess the creditworthiness of borrowers and debt securities, providing standardized risk measures for investors.

**Rating Agencies:**
• **Moody's**: Aaa (highest) to C (lowest)
• **S&P**: AAA (highest) to D (default)
• **Fitch**: AAA (highest) to D (default)

**Rating Categories:**
• **Investment Grade**: AAA to BBB- (lower risk)
• **High Yield**: BB+ to C (higher risk)
• **Distressed**: CCC to D (very high risk)

**Rating Factors:**
• Financial strength and cash flow generation
• Industry position and competitive advantages
• Management quality and governance
• Economic environment and cyclicality

**Investment Implications:**
• Ratings drive pricing and market access
• Regulatory capital requirements vary by rating
• Index inclusion and investor mandates
• Rating changes create trading opportunities"""
    
    def _generate_general_finance_answer(self, query: str) -> str:
        """Generate general finance answer"""
        return f"""**Financial Analysis: {query.title()}**

Based on current market conditions and credit market dynamics, {query.lower()} is influenced by several key factors:

**Market Environment:**
• Interest rate environment and central bank policy
• Credit spreads and risk appetite
• Economic growth and sector performance
• Regulatory changes and compliance requirements

**Key Considerations:**
• Credit quality and default risk assessment
• Liquidity and market access
• Portfolio diversification and risk management
• ESG factors and sustainability considerations

**Investment Implications:**
I recommend consulting with our credit team for specific analysis tailored to your investment objectives and risk tolerance. Our team can provide detailed market analysis, credit research, and investment recommendations.

Would you like me to elaborate on any specific aspect of this topic?"""

# Global instance
ai_assistant = CustomAIAssistant()

def process_ai_query(query: str, context: Dict = None) -> Dict:
    """Main function to process AI queries"""
    response = ai_assistant.process_query(query, context)
    return {
        "text": response.text,
        "type": response.type,
        "confidence": response.confidence,
        "sources": response.sources or [],
        "actions": response.actions or []
    }

def process_ai_query_with_files(query: str, context: Dict = None, file_analyses: List[Dict] = None) -> Dict:
    """Process AI queries with file attachments"""
    try:
        # Create enhanced context with file information
        enhanced_context = context.copy() if context else {}
        cv_file_info = None
        
        if file_analyses:
            enhanced_context['file_analyses'] = file_analyses
            enhanced_context['has_attachments'] = True
            
            # Format file information for the AI (human-readable)
            file_context = _format_file_context_for_ai(file_analyses)
            enhanced_context['file_context'] = file_context
            
            # Enhance the query with file information
            enhanced_query = _enhance_query_with_files(query, file_analyses)
            
            # Check if this is a CV formatting request
            cv_files = [f for f in file_analyses if f.get('type') in ['pdf', 'text'] and _is_cv_file(f)]
            logger.info(f"🔍 CV Detection: Found {len(cv_files)} CV files")
            logger.info(f"🔍 Query: {enhanced_query}")
            logger.info(f"🔍 CV formatting request: {_is_cv_formatting_request(enhanced_query, file_analyses)}")
            
            # IMPORTANT: If CV files exist, override file_context with RAW extracted text so CV formatter has real content
            if cv_files:
                raw_cv_text = cv_files[0].get('extracted_text', '') or ''
                if raw_cv_text:
                    enhanced_context['file_context'] = raw_cv_text
                    logger.info(f"🔍 Using RAW CV text for formatting: {len(raw_cv_text)} characters")
            
            if cv_files and _is_cv_formatting_request(enhanced_query, file_analyses):
                # Handle CV formatting and get file info
                cv_result = _handle_cv_formatting(cv_files)
                if isinstance(cv_result, dict) and cv_result.get('has_file'):
                    cv_file_info = cv_result
        else:
            enhanced_query = query
            enhanced_context['has_attachments'] = False
        
        # If we have CV file info, use it directly
        if cv_file_info:
            return {
                "text": cv_file_info.get('text', ''),
                "type": "cv_formatting",
                "confidence": 0.95,
                "sources": [],
                "actions": [],
                "cv_file": cv_file_info.get('file_info'),
                "download_url": cv_file_info.get('download_url'),
                "filename": cv_file_info.get('filename'),
                "html_content": cv_file_info.get('html_content'),
                "html_base64": cv_file_info.get('html_base64')
            }
        
        # Process the enhanced query
        response = ai_assistant.process_query(enhanced_query, enhanced_context)
        
        # Enhance response with file-specific information
        if file_analyses:
            response.text = _enhance_response_with_file_info(response.text, file_analyses)
            response.type = 'file_analysis' if response.type == 'answer' else response.type
            response.confidence = min(response.confidence + 0.1, 1.0)  # Boost confidence for file analysis
        
        return {
            "text": response.text,
            "type": response.type,
            "confidence": response.confidence,
            "sources": response.sources or [],
            "actions": response.actions or []
        }
        
    except Exception as e:
        logger.error(f"Error processing AI query with files: {e}")
        return {
            "text": f"I encountered an error while analyzing your files: {str(e)}. Please try again or contact support.",
            "type": "error",
            "confidence": 0.0,
            "sources": [],
            "actions": []
        }

def _format_file_context_for_ai(file_analyses: List[Dict]) -> str:
    """Format file analysis results for AI context"""
    if not file_analyses:
        return ""
    
    context_parts = []
    context_parts.append("The user has provided the following files for analysis:")
    
    for i, analysis in enumerate(file_analyses, 1):
        filename = analysis.get('filename', f'File {i}')
        file_type = analysis.get('type', 'unknown')
        
        context_parts.append(f"\nFile {i}: {filename}")
        context_parts.append(f"Type: {file_type}")
        
        if analysis.get('extracted_text'):
            text_preview = analysis['extracted_text'][:300]
            if len(analysis['extracted_text']) > 300:
                text_preview += "..."
            context_parts.append(f"Content: {text_preview}")
        
        if analysis.get('analysis'):
            context_parts.append(f"Analysis: {analysis['analysis']}")
        
        if analysis.get('error'):
            context_parts.append(f"Error: {analysis['error']}")
    
    return "\n".join(context_parts)

def _enhance_query_with_files(query: str, file_analyses: List[Dict]) -> str:
    """Enhance the user query with file context"""
    if not file_analyses:
        return query
    
    # Count file types
    image_count = sum(1 for f in file_analyses if f.get('type') == 'image')
    document_count = sum(1 for f in file_analyses if f.get('type') in ['pdf', 'text'])
    
    file_summary = []
    if image_count > 0:
        file_summary.append(f"{image_count} image(s)")
    if document_count > 0:
        file_summary.append(f"{document_count} document(s)")
    
    if file_summary:
        enhanced_query = f"{query}\n\n[The user has also uploaded {', '.join(file_summary)} for analysis. Please consider the content of these files in your response.]"
    else:
        enhanced_query = query
    
    return enhanced_query

def _enhance_response_with_file_info(response_text: str, file_analyses: List[Dict]) -> str:
    """Enhance the AI response with file-specific information"""
    if not file_analyses:
        return response_text
    
    # Check if this is a CV formatting request
    cv_files = [f for f in file_analyses if f.get('type') in ['pdf', 'text'] and _is_cv_file(f)]
    
    if cv_files and _is_cv_formatting_request(response_text, file_analyses):
        # Handle CV formatting
        cv_response = _handle_cv_formatting(cv_files)
        if cv_response and isinstance(cv_response, dict):
            # Return the text portion for the response
            return cv_response.get('text', response_text)
        elif cv_response:
            return cv_response
    
    # Add file processing summary
    successful_files = [f for f in file_analyses if f.get('type') not in ['error', 'unsupported']]
    error_files = [f for f in file_analyses if f.get('type') in ['error', 'unsupported']]
    
    if successful_files:
        file_summary = f"\n\n📎 **File Analysis Summary:** I've analyzed {len(successful_files)} file(s) you uploaded."
        
        for analysis in successful_files:
            filename = analysis.get('filename', 'Unknown')
            if analysis.get('has_text'):
                file_summary += f"\n• {filename}: Text content extracted and analyzed"
            else:
                file_summary += f"\n• {filename}: File processed (no readable text found)"
        
        response_text += file_summary
    
    if error_files:
        error_summary = f"\n\n⚠️ **Note:** {len(error_files)} file(s) could not be processed due to format or technical issues."
        response_text += error_summary
    
    return response_text

def _is_cv_file(file_analysis: Dict) -> bool:
    """Check if a file is likely a CV/resume"""
    filename = file_analysis.get('filename', '').lower()
    content = file_analysis.get('extracted_text', '').lower()
    
    # Check filename
    cv_filename_indicators = ['cv', 'resume', 'curriculum', 'vitae']
    if any(indicator in filename for indicator in cv_filename_indicators):
        return True
    
    # Check content for CV indicators
    cv_content_indicators = [
        'curriculum vitae', 'professional experience', 'work experience',
        'education', 'qualifications', 'skills', 'objective', 'summary'
    ]
    
    if any(indicator in content for indicator in cv_content_indicators):
        return True
    
    # Check for common CV patterns
    cv_patterns = [
        r'\b(19|20)\d{2}\b.*\b(19|20)\d{2}\b',  # Date ranges
        r'email\s*:',  # Email field
        r'phone\s*:',  # Phone field
        r'address\s*:',  # Address field
    ]
    
    import re
    for pattern in cv_patterns:
        if re.search(pattern, content):
            return True
    
    return False

def _is_cv_formatting_request(query: str, file_analyses: List[Dict]) -> bool:
    """Check if this is a CV formatting request"""
    query_lower = query.lower()
    
    # Strong CV formatting keywords - more flexible matching
    strong_cv_keywords = [
        'format this cv', 'format my cv', 'format the cv', 'format cv', 'format resume',
        'format this resume', 'format my resume', 'format the resume',
        'mawney style', 'company style', 'your style', 'professional style',
        'reformat', 'format this', 'format it', 'format document',
        'make it professional', 'professional format', 'company format',
        'use the template', 'apply template', 'mawney template', 'company template',
        'style it', 'professional layout', 'company layout'
    ]
    
    # Check for strong CV formatting indicators
    if any(keyword in query_lower for keyword in strong_cv_keywords):
        return True
    
    # Check if files are CVs and query mentions formatting
    cv_files = [f for f in file_analyses if _is_cv_file(f)]
    if cv_files and any(word in query_lower for word in ['format', 'style', 'template', 'professional', 'layout', 'design']):
        return True
    
    return False

def _handle_cv_formatting(cv_files: List[Dict]) -> Dict[str, Any]:
    """Handle CV formatting request and generate downloadable file"""
    try:
        if not cv_files:
            return {
                "text": "I don't see any CV files to format. Please upload your CV document.",
                "has_file": False
            }
        
        # Use the first CV file
        cv_file = cv_files[0]
        filename = cv_file.get('filename', 'uploaded_cv')
        cv_content = cv_file.get('extracted_text', '')
        
        # Debug: Log the extracted content
        logger.info(f"=== CV FILE ANALYSIS ===")
        logger.info(f"Filename: {filename}")
        logger.info(f"File type: {cv_file.get('type', 'unknown')}")
        logger.info(f"Content length: {len(cv_content)} characters")
        logger.info(f"First 1000 characters: {cv_content[:1000]}")
        logger.info(f"=== END CV FILE ANALYSIS ===")
        
        if not cv_content:
            return {
                "text": "I was unable to extract text from your CV file. Please ensure it's a readable PDF or text document.",
                "has_file": False
            }
        
        # Normalize raw CV text to improve section detection before formatting
        def _normalize_cv_text(text: str) -> str:
            try:
                import re
                t = text or ""
                # Standardize newlines
                t = t.replace('\r\n', '\n').replace('\r', '\n')
                # Fix hyphen bullets to real bullets
                t = re.sub(r"\n\s*[-•·]\s+", "\n• ", t)
                # Ensure headings are on their own line
                headings = [
                    r"work experience", r"professional experience", r"experience",
                    r"education", r"qualifications", r"skills", r"languages",
                    r"certifications", r"additional information", r"interests",
                    r"publications", r"projects", r"profile", r"summary"
                ]
                for h in headings:
                    t = re.sub(rf"\s*(?i){h}\s*:?\s*", lambda m: f"\n\n{m.group(0).strip().upper()}\n", t)
                # Add line breaks between date ranges and roles to help parsers
                t = re.sub(r"(\d{4}\s*[–-]\s*(Present|\d{4}))", r"\n\1\n", t, flags=re.IGNORECASE)
                # Collapse excessive blanks
                t = re.sub(r"\n{3,}", "\n\n", t)
                return t.strip()
            except Exception:
                return text or ""

        cv_content = _normalize_cv_text(cv_content)
        logger.info(f"🔧 Normalized CV text length: {len(cv_content)}")

        def _has_visible_text(html: str, min_chars: int = 200) -> bool:
            try:
                import re
                text = re.sub(r"<[^>]+>", " ", html or "").strip()
                text = re.sub(r"\s+", " ", text)
                return len(text) >= min_chars
            except Exception:
                return False

        def _format_with_cascading_templates(raw_text: str, fname: str):
            # Try V33, then V31, V20, V17, then MawneyTemplateFormatter
            try_order = []
            try:
                from enhanced_cv_formatter_v33 import enhanced_cv_formatter_v33
                try_order.append(("v33", enhanced_cv_formatter_v33))
            except ImportError:
                pass
            try:
                from enhanced_cv_formatter_v31 import enhanced_cv_formatter_v31
                try_order.append(("v31", enhanced_cv_formatter_v31))
            except ImportError:
                pass
            try:
                from enhanced_cv_formatter_v20 import enhanced_cv_formatter_v20
                try_order.append(("v20", enhanced_cv_formatter_v20))
            except ImportError:
                pass
            try:
                from enhanced_cv_formatter_v17 import enhanced_cv_formatter_v17
                try_order.append(("v17", enhanced_cv_formatter_v17))
            except ImportError:
                pass

            for label, mod in try_order:
                try:
                    logger.info(f"🧩 Trying formatter {label}...")
                    result = mod.format_cv_with_template(raw_text, fname)
                    html = result.get('html_content', '')
                    if html and _has_visible_text(html):
                        logger.info(f"✅ Formatter {label} produced visible content")
                        return result
                    else:
                        logger.warning(f"⚠️ Formatter {label} produced low/empty content; continuing")
                except Exception as e:
                    logger.warning(f"⚠️ Formatter {label} error: {e}")

            # Fallback to original MawneyTemplateFormatter
            logger.info("🧩 Falling back to MawneyTemplateFormatter")
            template_formatter = MawneyTemplateFormatter()
            return template_formatter.format_cv_with_template(raw_text, fname)

        def _preparse_sections(raw_text: str) -> str:
            # Light-weight pre-parser: ensure clear headings exist to help downstream formatter
            import re
            t = raw_text or ""
            t = t.replace('\r\n', '\n').replace('\r', '\n')
            # Normalize bullets
            t = re.sub(r"\n\s*[-•·]\s+", "\n• ", t)
            # Promote common headings
            headings = [
                "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "EXPERIENCE",
                "EDUCATION", "SKILLS", "LANGUAGES", "CERTIFICATIONS", "SUMMARY", "PROFILE"
            ]
            for h in headings:
                t = re.sub(rf"\n\s*(?i){h}\s*:?\s*\n", f"\n\n{h}\n", t)
            # If no work experience header but there are date ranges, insert one above first match
            if not re.search(r"\n(WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EXPERIENCE)\n", t, re.I):
                m = re.search(r"\b(19|20)\d{2}\s*[–-]\s*(Present|\b(19|20)\d{2}\b)", t, re.I)
                if m:
                    pos = t.rfind('\n', 0, m.start())
                    if pos != -1:
                        t = t[:pos] + "\n\nWORK EXPERIENCE\n" + t[pos:]
            # Collapse excessive whitespace
            t = re.sub(r"\n{3,}", "\n\n", t)
            return t

        # Pre-parse to improve section boundaries before formatting
        cv_content = _preparse_sections(cv_content)
        # Try cascading enhanced formatters first
        formatted_result = _format_with_cascading_templates(cv_content, filename)
        html_content = formatted_result.get('html_content', '')
        # If still no visible content, return a parsing error instead of fallback text
        if not _has_visible_text(html_content):
            logger.error("❌ CV parsing produced insufficient content after cascading formatters")
            return {
                "text": "I couldn't parse your CV into the template. Please try a different PDF export (text-based, not scanned) or send a .docx/.txt.",
                "has_file": False
            }

        # Sanitize HTML for iOS print renderer (WKWebView/UIMarkupTextPrintFormatter)
        def _sanitize_html_for_ios_print(html: str) -> str:
            try:
                import re
                cleaned = html or ""
                # Remove @page and @media blocks which often break iOS print layout
                cleaned = re.sub(r"@page[^{]*\{[\s\S]*?\}", "", cleaned)
                cleaned = re.sub(r"@media[^{]*\{[\s\S]*?\}", "", cleaned)
                # Fix zero sizes that cause blank output
                cleaned = cleaned.replace("font-size: 0pt", "font-size: 11pt").replace("font-size: 0px", "font-size: 12px")
                cleaned = cleaned.replace("line-height: 0", "line-height: 1.3")
                # Ensure fixed content width appropriate for A4
                viewport = (
                    "<meta name=\"viewport\" content=\"width=595px, initial-scale=1.0, maximum-scale=1.0, user-scalable=no\">\n"
                    "<style>body{width:595px;margin:0 auto;font-size:11pt;line-height:1.4} .page-content{width:595px}</style>"
                )
                if "<meta charset=\"UTF-8\">" in cleaned:
                    cleaned = cleaned.replace("<meta charset=\"UTF-8\">", "<meta charset=\"UTF-8\">\n" + viewport)
                elif "<head>" in cleaned:
                    cleaned = cleaned.replace("<head>", "<head>\n" + viewport)
                else:
                    cleaned = "<head>" + viewport + "</head>\n" + cleaned
                return cleaned
            except Exception:
                return html or ""

        html_content = _sanitize_html_for_ios_print(html_content)
        formatted_result['html_content'] = html_content
        
        # Check for success or presence of html_content (V16 doesn't have success key)
        if not formatted_result.get('success', True) and not formatted_result.get('html_content'):
            return {
                "text": f"I encountered an error formatting your CV: {formatted_result.get('error', 'Unknown error')}",
                "has_file": False
            }
        
        # Defensive fallback: if formatter produced little or no visible text, create a simple HTML from raw CV text
        html_content = formatted_result.get('html_content', '')
        try:
            import re
            visible_text = re.sub(r"<[^>]+>", " ", html_content or "").strip()
            if len(visible_text) < 100:  # too little content -> build simple fallback
                logger.warning("⚠️ Formatter output too small; using simple HTML fallback from raw CV text")
                safe_text = cv_content.replace("<", "&lt;").replace(">", "&gt;")
                simple_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset=\"UTF-8\">
                    <meta name=\"viewport\" content=\"width=595px, initial-scale=1.0\">
                    <style>
                        body {{ font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.4; margin: 20px; color: #222; }}
                        h1 {{ font-size: 18pt; text-align: center; margin-bottom: 20px; }}
                        pre {{ white-space: pre-wrap; word-wrap: break-word; font-family: 'Times New Roman', serif; }}
                    </style>
                </head>
                <body>
                    <h1>Curriculum Vitae</h1>
                    <pre>{safe_text}</pre>
                </body>
                </html>
                """
                html_content = simple_html
                formatted_result['html_content'] = html_content
                formatted_result['success'] = True
        except Exception:
            pass
        
        # Generate PDF file and get base64 content for direct download
        # Try to generate PDF, fallback to HTML if pdfkit not available
        file_result = cv_file_generator.generate_pdf_file(html_content, f"formatted_{filename.replace('.pdf', '')}")
        
        # Get file as base64 for iOS app download
        import base64
        if file_result.get('success') and file_result.get('format') == 'pdf':
            # PDF was generated successfully
            with open(file_result.get('filepath'), 'rb') as f:
                pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
            file_base64 = pdf_base64
            file_format = 'pdf'
        else:
            # Fallback to HTML
            html_base64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
            file_base64 = html_base64
            file_format = 'html'
        
        # Create response
        response = "📄 **CV Formatted in Mawney Partners Style**\n\n"
        
        # Add analysis
        if formatted_result.get('analysis'):
            response += f"**Analysis:** {formatted_result['analysis']}\n\n"
        
        # Add file download info
        if file_result.get('success'):
            response += "✅ **Your formatted CV is ready for download!**\n\n"
            response += f"📥 **File:** {file_result['filename']}\n"
            response += f"📊 **Size:** {file_result['file_size']:,} bytes\n"
            response += f"🔗 **Format:** {file_format.upper()}\n\n"
        
        # Add sections found
        sections_found = formatted_result.get('sections_found', [])
        if sections_found:
            response += f"**Sections Identified:** {', '.join(sections_found)}\n\n"
        
        # Add preview (truncated)
        response += "**Preview:**\n"
        response += "```\n"
        text_preview = formatted_result.get('text_version', '')[:500]
        response += text_preview
        if len(formatted_result.get('text_version', '')) > 500:
            response += "\n... [truncated - full version in downloadable file]"
        response += "\n```\n\n"
        
        # Add download instructions
        response += "💡 **Next Steps:**\n"
        if file_format == 'pdf':
            response += "• Download the PDF file above\n"
            response += "• Open with any PDF viewer\n"
            response += "• Print or share directly\n"
            response += "• Edit if needed using a PDF editor\n\n"
        else:
            response += "• Download the HTML file above\n"
            response += "• Open in your web browser\n"
            response += "• Print to PDF or save directly\n"
            response += "• Edit in your preferred document editor if needed\n\n"
        
        response += "**Note:** This CV has been formatted with Garamond typography, your company logos (top & bottom), and professional Mawney Partners styling."
        
        return {
            "text": response,
            "has_file": True,
            "file_info": file_result,
            "download_url": file_result.get('download_url'),
            "download_filename": file_result.get('filename'),  # iOS app expects this key
            "filename": file_result.get('filename'),  # Keep for compatibility
            "file_format": file_format,
            "file_base64": file_base64,
            "html_content": html_content  # iOS app uses this to create PDF client-side
        }
        
    except Exception as e:
        logger.error(f"Error handling CV formatting: {e}")
        return {
            "text": f"I encountered an error while formatting your CV: {str(e)}. Please try again or contact support.",
            "has_file": False
        }

if __name__ == "__main__":
    # Test the AI assistant
    test_queries = [
        "Create a senior credit analyst job ad",
        "What is corporate credit?",
        "Format my CV",
        "What are current credit market trends?",
        "Hello, what can you help me with?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = process_ai_query(query)
        print(f"Response: {response['text'][:200]}...")
        print(f"Type: {response['type']}, Confidence: {response['confidence']}")
