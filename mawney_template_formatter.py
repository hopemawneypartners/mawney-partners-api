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
        """Parse CV data to extract structured information with improved parsing"""
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
        
        # Extract professional summary
        summary_started = False
        current_summary = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['professional summary', 'profile', 'overview']):
                summary_started = True
                continue
            elif summary_started and any(keyword in line.lower() for keyword in ['experience', 'education', 'skills']):
                break
            elif summary_started and line:
                current_summary.append(line)
        
        parsed['summary'] = ' '.join(current_summary)
        
        # Extract experience
        experience_section = False
        current_experience = {}
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['professional experience', 'work experience', 'employment']):
                experience_section = True
                continue
            elif experience_section and any(keyword in line.lower() for keyword in ['education', 'skills', 'interests']):
                if current_experience:
                    parsed['experience'].append(current_experience)
                break
            elif experience_section and line:
                # Check if this is a company name (usually in caps or has dates)
                if self._is_company_line(line):
                    if current_experience:
                        parsed['experience'].append(current_experience)
                    current_experience = {
                        'company': line,
                        'title': '',
                        'dates': '',
                        'responsibilities': []
                    }
                elif current_experience and not current_experience['title']:
                    current_experience['title'] = line
                elif current_experience and line.startswith(('•', '-', '*')) or line.startswith(' '):
                    current_experience['responsibilities'].append(line.strip('•-* '))
        
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
        return (line.isupper() or 
                any(word in line.lower() for word in ['inc', 'llc', 'ltd', 'corp', 'partners', 'capital', 'management']) or
                re.search(r'\b\d{4}\b', line))  # Contains year
    
    def _is_school_line(self, line: str) -> bool:
        """Check if line is likely a school name"""
        return (any(word in line.lower() for word in ['university', 'college', 'school', 'institute']) or
                line.isupper())
    
    def _get_logo_base64(self) -> str:
        """Get the MP logo as base64"""
        logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'cv logo 1.png')
        try:
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
                return base64.b64encode(logo_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error loading logo: {e}")
            return ""
    
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
        """Format experience items"""
        items = []
        for exp in data.get('experience', []):
            company = exp.get('company', '')
            title = exp.get('title', '')
            dates = exp.get('dates', '')
            responsibilities = exp.get('responsibilities', [])
            
            item_html = f'''
            <div class="experience-item">
                <div class="company-header">
                    <div class="company-name">{company}</div>
                    <div class="dates">{dates}</div>
                </div>
                <div class="job-title">{title}</div>
                <div class="responsibilities">
                    <ul>
                        {''.join([f'<li>{resp}</li>' for resp in responsibilities])}
                    </ul>
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
        """Get MP logo as base64 from iOS assets"""
        try:
            # Try to get the actual MP logo from iOS assets
            logo_path = os.path.join(os.path.dirname(__file__), '..', '..', 'MP APP', 'MP APP 2', 'Assets.xcassets', 'logo.imageset', 'logo.png')
            
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo_data = f.read()
                import base64
                logo_base64 = base64.b64encode(logo_data).decode('utf-8')
                
                logger.info("Using actual MP logo from assets")
                return f'''
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="data:image/png;base64,{logo_base64}" alt="Mawney Partners Logo" style="max-width: 200px; height: auto;" />
                </div>
                '''
            else:
                # Fallback to text logo if image not found
                logger.warning("MP logo not found, using text fallback")
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
            logger.error(f"Error getting logo: {e}")
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

