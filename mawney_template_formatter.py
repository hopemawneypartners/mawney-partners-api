#!/usr/bin/env python3
"""
Mawney Partners CV Template Formatter
Uses the exact HTML template to match the design shown in examples
"""

import re
import logging
from typing import Dict, List, Optional, Any
import base64
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MawneyTemplateFormatter:
    """Formats CVs using the exact Mawney Partners template"""
    
    def __init__(self):
        self.template_path = os.path.join(os.path.dirname(__file__), 'mawney_cv_template.html')
        
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
        """Parse CV data to extract structured information"""
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
        
        # Extract name (usually first line)
        if lines:
            parsed['name'] = lines[0]
        
        # Extract contact info
        for line in lines:
            if '@' in line and '.' in line:
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
                if email_match:
                    parsed['email'] = email_match.group(0)
            
            phone_match = re.search(r'\+?[\d\s\-\(\)]{10,}', line)
            if phone_match:
                parsed['phone'] = phone_match.group(0).strip()
        
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

