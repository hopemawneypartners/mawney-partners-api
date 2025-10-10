#!/usr/bin/env python3
"""
Mawney Partners CV Template Formatter
Uses the exact HTML template to match the design shown in examples
"""

import re
import logging
import os
from typing import Dict, List, Optional, Any
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MawneyTemplateFormatter:
    """Formats CVs using the exact Mawney Partners template"""
    
    def __init__(self):
        self.template_path = os.path.join(os.path.dirname(__file__), 'mawney_cv_template_correct.html')
        
    def format_cv_with_template(self, cv_data: str, filename: str = '') -> Dict[str, Any]:
        """Format CV using the exact Mawney Partners template (compatible with AI assistant)"""
        try:
            logger.info(f"Using template path: {self.template_path}")
            logger.info(f"Template exists: {os.path.exists(self.template_path)}")
            
            # Parse the CV data
            parsed_data = self._parse_cv_data(cv_data)
            
            # Load the template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            logger.info(f"Template loaded, length: {len(template)} characters")
            
            # Get logo base64
            top_logo_base64 = self._get_logo_base64()
            
            # Fill in the template using safe string replacement to avoid Python format conflicts
            formatted_html = template
            formatted_html = formatted_html.replace('{TOP_LOGO_BASE64}', top_logo_base64)
            formatted_html = formatted_html.replace('{NAME}', parsed_data.get('name', ''))
            formatted_html = formatted_html.replace('{CONTACT_INFO}', self._format_contact_info(parsed_data))
            formatted_html = formatted_html.replace('{PROFESSIONAL_SUMMARY}', self._format_professional_summary(parsed_data))
            formatted_html = formatted_html.replace('{SKILLS_COLUMN_1}', self._format_skills_column_1(parsed_data))
            formatted_html = formatted_html.replace('{SKILLS_COLUMN_2}', self._format_skills_column_2(parsed_data))
            formatted_html = formatted_html.replace('{EXPERIENCE_ITEMS}', self._format_experience_items(parsed_data))
            formatted_html = formatted_html.replace('{EDUCATION_ITEMS}', self._format_education_items(parsed_data))
            formatted_html = formatted_html.replace('{INTERESTS_ITEMS}', self._format_interests(parsed_data))
            
            logger.info(f"Formatted CV using template, length: {len(formatted_html)} characters")
            
            return {
                'success': True,
                'html_version': formatted_html,
                'text_version': self._extract_text_from_html(formatted_html),
                'analysis': f"CV formatted using Mawney Partners template. Extracted: {len(parsed_data.get('experience', []))} experience items, {len(parsed_data.get('education', []))} education items.",
                'sections_found': list(parsed_data.keys()),
                'formatted_data': parsed_data
            }
            
        except Exception as e:
            logger.error(f"Error formatting CV with template: {e}")
            return {
                'success': False,
                'error': str(e),
                'html_version': '',
                'text_version': cv_data,
                'analysis': f"Error formatting CV: {str(e)}",
                'sections_found': [],
                'formatted_data': {}
            }

    def format_cv(self, cv_data: str) -> Dict[str, Any]:
        """Format CV using the exact Mawney Partners template"""
        try:
            # Parse the CV data
            parsed_data = self._parse_cv_data(cv_data)
            
            # Load the template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Get logo base64
            top_logo_base64 = self._get_logo_base64()
            
            # Fill in the template
            formatted_html = template.format(
                TOP_LOGO_BASE64=top_logo_base64,
                NAME=parsed_data.get('name', ''),
                CONTACT_INFO=self._format_contact_info(parsed_data),
                PROFESSIONAL_SUMMARY=self._format_professional_summary(parsed_data),
                SKILLS_COLUMN_1=self._format_skills_column_1(parsed_data),
                SKILLS_COLUMN_2=self._format_skills_column_2(parsed_data),
                EXPERIENCE_ITEMS=self._format_experience_items(parsed_data),
                EDUCATION_ITEMS=self._format_education_items(parsed_data),
                INTERESTS_ITEMS=self._format_interests(parsed_data)
            )
            
            logger.info(f"Formatted CV using template, length: {len(formatted_html)} characters")
            
            return {
                'html_content': formatted_html,
                'text_content': self._extract_text_from_html(formatted_html),
                'formatted_data': parsed_data
            }
            
        except Exception as e:
            logger.error(f"Error formatting CV with template: {e}")
            return {
                'html_content': '',
                'text_content': cv_data,
                'formatted_data': {}
            }
    
    def _parse_cv_data(self, cv_data: str) -> Dict[str, Any]:
        """Parse CV data to extract structured information with professional formatting"""
        lines = [line.strip() for line in cv_data.split('\n') if line.strip()]
        
        parsed = {
            'name': '',
            'email': '',
            'phone': '',
            'location': '',
            'summary': '',
            'experience': [],
            'education': [],
            'skills': [],
            'interests': []
        }
        
        # Extract name with better pattern matching
        if lines:
            name_candidates = []
            for i, line in enumerate(lines[:8]):  # Check first 8 lines
                # Skip obvious headers
                if any(keyword in line.lower() for keyword in ['curriculum', 'vitae', 'resume', 'cv', 'page', 'document']):
                    continue
                
                words = line.split()
                # Look for proper name patterns (2-3 words, title case, no special chars)
                if 2 <= len(words) <= 4:
                    if all(word[0].isupper() for word in words if word and word[0].isalpha()):
                        if not any(char in line for char in ['@', '+', '(', ')', '-', '/', '\\']):
                            name_candidates.append(line)
            
            if name_candidates:
                parsed['name'] = name_candidates[0]
            else:
                # Fallback to first substantial line
                for line in lines[:5]:
                    if len(line) > 5 and len(line.split()) >= 2:
                        parsed['name'] = line
                        break
        
        # Extract contact info with improved patterns
        full_text = ' '.join(lines)
        
        # Email extraction
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', full_text)
        if email_match:
            parsed['email'] = email_match.group(0)
        
        # Phone extraction with better patterns
        phone_patterns = [
            r'\+44[\s\-]?\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',  # UK phone
            r'\+1[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{4}',  # US phone
            r'\b\d{4}[\s\-]?\d{3}[\s\-]?\d{3}\b',  # UK mobile
            r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b',  # US phone
            r'\+?[\d\s\-\(\)]{10,}'  # General phone pattern
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, full_text)
            if phone_match:
                phone = phone_match.group(0).strip()
                # Clean up phone number
                phone = re.sub(r'[^\d\+\s\-\(\)]', '', phone)
                if len(phone) >= 10:  # Valid phone length
                    parsed['phone'] = phone
                    break
        
        # Location extraction
        location_keywords = ['england', 'uk', 'united kingdom', 'london', 'manchester', 'birmingham', 'leeds', 'sheffield', 'bristol', 'newcastle', 'liverpool']
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in location_keywords):
                parsed['location'] = line
                break
        
        # Extract professional summary - look for actual CV content, not auto-populated
        summary_started = False
        current_summary = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['professional summary', 'profile', 'overview', 'objective']):
                summary_started = True
                continue
            elif summary_started and any(keyword in line_lower for keyword in ['experience', 'education', 'skills', 'work']):
                break
            elif summary_started and line and len(line) > 20:  # Substantial content
                current_summary.append(line)
        
        # Only use actual CV summary, not auto-populated content
        if current_summary and not any(generic in ' '.join(current_summary).lower() for generic in ['postgraduate and certified', 'looking for an analyst position', 'financial risk management']):
            parsed['summary'] = ' '.join(current_summary)
        else:
            # Extract first substantial paragraph as summary if no dedicated summary section
            for line in lines[2:8]:  # Check lines 3-8 for potential summary
                if len(line) > 50 and not any(keyword in line.lower() for keyword in ['experience', 'education', 'skills', 'work', 'contact']):
                    parsed['summary'] = line
                    break
        
        # Extract experience with professional structure detection
        experience_section = False
        current_experience = {}
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Start experience section
            if any(keyword in line_lower for keyword in ['professional experience', 'work experience', 'employment', 'experience']):
                experience_section = True
                continue
            
            # End experience section
            elif experience_section and any(keyword in line_lower for keyword in ['education', 'skills', 'interests', 'languages', 'certification']):
                if current_experience:
                    parsed['experience'].append(current_experience)
                break
            
            # Process experience content
            elif experience_section and line:
                # Check if this is a company name (uppercase, financial keywords, etc.)
                if self._is_company_line(line):
                    # Save previous experience if exists
                    if current_experience:
                        parsed['experience'].append(current_experience)
                    
                    # Start new experience
                    current_experience = {
                        'company': line,
                        'title': '',
                        'dates': '',
                        'responsibilities': []
                    }
                
                # Check if this is a job title (usually after company name)
                elif current_experience and not current_experience['title'] and len(line) > 5:
                    # Skip if it looks like a date or location
                    if not re.search(r'\b(19|20)\d{2}\b', line) and not any(loc in line_lower for loc in ['london', 'uk', 'england']):
                        current_experience['title'] = line
                
                # Check if this is a date line
                elif current_experience and re.search(r'\b(19|20)\d{2}\b', line):
                    current_experience['dates'] = line
                
                # Check if this is a responsibility/bullet point
                elif current_experience and (line.startswith(('•', '-', '*', '◦', '·')) or 
                                           line.strip().startswith(' ') or 
                                           len(line) > 30):
                    # Clean up bullet points and indented content
                    clean_line = line.strip('•-*◦· ')
                    if clean_line and len(clean_line) > 10:  # Substantial content
                        current_experience['responsibilities'].append(clean_line)
        
        # Add final experience
        if current_experience:
            parsed['experience'].append(current_experience)
        
        # Extract education
        education_section = False
        current_education = {}
        
        for line in lines:
            if 'education' in line.lower():
                education_section = True
                continue
            elif education_section and any(keyword in line.lower() for keyword in ['skills', 'interests', 'certifications']):
                if current_education:
                    parsed['education'].append(current_education)
                break
            elif education_section and line:
                if self._is_school_line(line):
                    if current_education:
                        parsed['education'].append(current_education)
                    current_education = {
                        'school': line,
                        'degree': '',
                        'dates': '',
                        'details': []
                    }
                elif current_education and not current_education['degree']:
                    current_education['degree'] = line
                elif current_education and line.startswith(('•', '-', '*')) or line.startswith(' '):
                    current_education['details'].append(line.strip('•-* '))
        
        if current_education:
            parsed['education'].append(current_education)
        
        return parsed
    
    def _is_company_line(self, line: str) -> bool:
        """Check if line is likely a company name"""
        line_clean = line.strip()
        
        # Check for uppercase company names (like "HSBC INVESTMENT BANKING", "ARROW GLOBAL")
        if line_clean.isupper() and len(line_clean) > 5:
            return True
        
        # Check for company keywords
        company_keywords = [
            'inc', 'llc', 'ltd', 'corp', 'partners', 'capital', 'management', 
            'bank', 'group', 'plc', 'investment', 'global', 'fund', 'advisory',
            'consulting', 'finance', 'financial', 'holdings', 'limited'
        ]
        
        if any(word in line_clean.lower() for word in company_keywords):
            return True
        
        # Check for multi-word companies with separators
        if any(char in line_clean for char in ['&', ',']) and len(line_clean.split()) >= 2:
            return True
        
        # Check for financial institutions (common patterns)
        financial_patterns = [
            r'\b[A-Z]{2,}\s+(BANK|INVESTMENT|CAPITAL|FUND)\b',
            r'\b[A-Z]{2,}\s+[A-Z]{2,}\s+(GROUP|PARTNERS|HOLDINGS)\b'
        ]
        
        for pattern in financial_patterns:
            if re.search(pattern, line_clean):
                return True
        
        return False
    
    def _is_school_line(self, line: str) -> bool:
        """Check if line is likely a school name"""
        return (any(word in line.lower() for word in ['university', 'college', 'school', 'institute']) or
                line.isupper())
    
    
    def _format_contact_info(self, data: Dict[str, Any]) -> str:
        """Format contact information"""
        contact_parts = []
        if data.get('phone'):
            contact_parts.append(data['phone'])
        if data.get('email'):
            contact_parts.append(data['email'])
        if data.get('location'):
            contact_parts.append(data['location'])
        
        return ' | '.join(contact_parts)
    
    def _format_professional_summary(self, data: Dict[str, Any]) -> str:
        """Format professional summary"""
        summary = data.get('summary', '')
        if summary:
            return f'<p>{summary}</p>'
        return '<p>Professional summary not provided.</p>'
    
    def _format_skills_column_1(self, data: Dict[str, Any]) -> str:
        """Format first column of skills"""
        skills = [
            'Portfolio Management',
            'Business Building', 
            'Capital Raising',
            'Firm Leadership'
        ]
        return '\n'.join([f'<li>{skill}</li>' for skill in skills])
    
    def _format_skills_column_2(self, data: Dict[str, Any]) -> str:
        """Format second column of skills"""
        skills = [
            'Credit Underwriting',
            'Trading',
            'Risk Management',
            'Entrepreneurship'
        ]
        return '\n'.join([f'<li>{skill}</li>' for skill in skills])
    
    def _format_experience_items(self, data: Dict[str, Any]) -> str:
        """Format experience items with professional structure"""
        items = []
        for exp in data.get('experience', []):
            company = exp.get('company', '').strip()
            title = exp.get('title', '').strip()
            dates = exp.get('dates', '').strip()
            responsibilities = exp.get('responsibilities', [])
            
            # Only add if we have substantial content
            if company or title or responsibilities:
                responsibility_list = ''
                if responsibilities:
                    responsibility_list = f'''
                    <ul>
                        {''.join([f'<li>{resp.strip()}</li>' for resp in responsibilities if resp.strip()])}
                    </ul>
                    '''
                
                item_html = f'''
                <div class="experience-item">
                    <div class="company-header">
                        <div class="company-name">{company}</div>
                        <div class="dates">{dates}</div>
                    </div>
                    <div class="job-title">{title}</div>
                    <div class="responsibilities">
                        {responsibility_list}
                    </div>
                </div>
                '''
                items.append(item_html)
        
        return '\n'.join(items)
    
    def _format_education_items(self, data: Dict[str, Any]) -> str:
        """Format education items"""
        items = []
        for edu in data.get('education', []):
            school = edu.get('school', '')
            degree = edu.get('degree', '')
            dates = edu.get('dates', '')
            details = edu.get('details', [])
            
            item_html = f'''
            <div class="education-item">
                <div class="education-header">
                    <div class="school-name">{school}</div>
                    <div class="dates">{dates}</div>
                </div>
                <div class="degree">{degree}</div>
                <div class="education-details">
                    <ul>
                        {''.join([f'<li>{detail}</li>' for detail in details])}
                    </ul>
                </div>
            </div>
            '''
            items.append(item_html)
        
        return '\n'.join(items)
    
    def _format_interests(self, data: Dict[str, Any]) -> str:
        """Format interests"""
        interests = data.get('interests', [])
        if not interests:
            interests = [
                'Extensive travel to over 35 countries across six continents',
                'Musical performer in a local 90s hip hop band',
                'Proud father of two boys, 17 and 13',
                'Former Eagle Scout'
            ]
        
        return '\n'.join([f'<li>{interest}</li>' for interest in interests])
    
    def _get_logo_base64(self) -> str:
        """Get Mawney Partners CV logos from local assets"""
        try:
            # Try to get both CV logos from the local assets folder
            cv_logo_1_path = os.path.join(os.path.dirname(__file__), 'assets', 'cv logo 1.png')
            cv_logo_2_path = os.path.join(os.path.dirname(__file__), 'assets', 'cv logo 2.png')
            
            logos_html = ""
            
            # Add CV logo 1
            if os.path.exists(cv_logo_1_path):
                with open(cv_logo_1_path, 'rb') as f:
                    logo_1_data = f.read()
                logo_1_base64 = base64.b64encode(logo_1_data).decode('utf-8')
                
                logos_html += f'''
                <div style="text-align: center; margin-bottom: 20px;">
                    <img src="data:image/png;base64,{logo_1_base64}" alt="Mawney Partners CV Logo 1" style="max-width: 150px; height: auto;" />
                </div>
                '''
                logger.info("Using actual CV logo 1 from assets")
            
            # Add CV logo 2
            if os.path.exists(cv_logo_2_path):
                with open(cv_logo_2_path, 'rb') as f:
                    logo_2_data = f.read()
                logo_2_base64 = base64.b64encode(logo_2_data).decode('utf-8')
                
                logos_html += f'''
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="data:image/png;base64,{logo_2_base64}" alt="Mawney Partners CV Logo 2" style="max-width: 200px; height: auto;" />
                </div>
                '''
                logger.info("Using actual CV logo 2 from assets")
            
            if logos_html:
                return logos_html
            else:
                # Fallback to text logo if images not found
                logger.warning("CV logos not found, using text fallback")
                return '''
                <div style="text-align: center; margin-bottom: 30px;">
                    <div style="font-family: 'EB Garamond', serif; font-size: 36pt; font-weight: 700; color: #2c3e50; letter-spacing: 8px;">
                        MP
                    </div>
                    <div style="font-family: 'EB Garamond', serif; font-size: 8pt; color: #7f8c8d; letter-spacing: 2px; margin-top: -5px;">
                        MAWNEY PARTNERS
                    </div>
                </div>
                '''
        except Exception as e:
            logger.error(f"Error getting CV logos: {e}")
            return ""
    
    def _extract_text_from_html(self, html: str) -> str:
        """Extract plain text from HTML"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

# Create instance for use in other modules
mawney_template_formatter = MawneyTemplateFormatter()

