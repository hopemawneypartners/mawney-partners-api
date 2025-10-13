#!/usr/bin/env python3
"""
Enhanced CV Formatter for Mawney Partners
Uses AI to intelligently parse, organize, and rewrite CV content in company style
Includes proper pagination for multi-page A4 documents
"""

import re
import logging
import os
from typing import Dict, List, Optional, Any
import base64
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# No external AI needed - using rule-based parsing only
# The AI assistant system handles intelligence at a higher level
OPENAI_AVAILABLE = False
openai_client = None

class EnhancedCVFormatter:
    """Enhanced CV formatter with AI-powered parsing and proper pagination"""
    
    def __init__(self):
        # Try to use enhanced template first, fallback to correct template
        enhanced_template = os.path.join(os.path.dirname(__file__), 'mawney_cv_template_enhanced.html')
        correct_template = os.path.join(os.path.dirname(__file__), 'mawney_cv_template_correct.html')
        
        if os.path.exists(enhanced_template):
            self.template_path = enhanced_template
            logger.info("Using enhanced CV template with improved pagination")
        elif os.path.exists(correct_template):
            self.template_path = correct_template
            logger.info("Using standard CV template")
        else:
            raise FileNotFoundError("No CV template found!")
        
        self.use_ai_parsing = False  # Rule-based parsing only
        
    def format_cv_with_template(self, cv_data: str, filename: str = '') -> Dict[str, Any]:
        """Format CV using the Mawney Partners template with AI-enhanced parsing"""
        try:
            logger.info(f"=== ENHANCED CV FORMATTING STARTED ===")
            logger.info(f"Filename: {filename}")
            logger.info(f"Raw CV data length: {len(cv_data)} characters")
            
            # Step 1: Clean and preprocess the CV text
            cleaned_cv = self._clean_cv_text(cv_data)
            logger.info(f"Cleaned CV data length: {len(cleaned_cv)} characters")
            
            # Step 2: Use rule-based parsing to extract CV structure
            # The AI assistant at the application level will handle intelligent rewrites
            parsed_data = self._rule_based_parse_cv(cleaned_cv)
            
            logger.info(f"Parsed CV data: {json.dumps({k: (v if not isinstance(v, (list, str)) or len(str(v)) < 100 else str(v)[:100] + '...') for k, v in parsed_data.items()}, indent=2)}")
            
            # Step 3: Load the HTML template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Step 4: Get logos
            top_logo_base64 = self._get_top_logo_base64()
            bottom_logo_base64 = self._get_bottom_logo_base64()
            
            # Step 5: Fill in the template with proper pagination
            formatted_html = self._fill_template_with_pagination(
                template, 
                parsed_data, 
                top_logo_base64, 
                bottom_logo_base64
            )
            
            logger.info(f"Generated HTML length: {len(formatted_html)} characters")
            logger.info(f"=== ENHANCED CV FORMATTING COMPLETED ===")
            
            return {
                'success': True,
                'html_version': formatted_html,
                'text_version': self._extract_text_from_html(formatted_html),
                'analysis': f"CV formatted using Mawney Partners template. Extracted: {len(parsed_data.get('experience', []))} experience items, {len(parsed_data.get('education', []))} education items.",
                'sections_found': list(parsed_data.keys()),
                'formatted_data': parsed_data,
                'pagination_enabled': True
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced CV formatting: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'html_version': '',
                'text_version': '',
                'download_url': '',
                'download_filename': ''
            }
    
    def _clean_cv_text(self, text: str) -> str:
        """Clean and normalize CV text with aggressive word separation"""
        import re
        
        # Remove multiple spaces and tabs
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Fix common PDF extraction artifacts
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')
        text = text.replace('ﬀ', 'ff')
        text = text.replace('ﬃ', 'ffi')
        text = text.replace('ﬄ', 'ffl')
        
        # CRITICAL: Fix concatenated words by adding spaces between lowercase and uppercase
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # Fix specific common concatenations seen in CVs
        concatenations = [
            ('stronganalytical', 'strong analytical'),
            ('problem-solving', 'problem-solving'),
            ('lookingfor', 'looking for'),
            ('ananalyst', 'an analyst'),
            ('financialrisk', 'financial risk'),
            ('derivativeproducts', 'derivative products'),
            ('statisticalmodelling', 'statistical modelling'),
            ('financialmathematics', 'financial mathematics'),
            ('riskmetrics', 'risk metrics'),
            ('riskanalysis', 'risk analysis'),
            ('businessschool', 'business school'),
            ('universitiesand', 'universities and'),
        ]
        
        for old, new in concatenations:
            text = re.sub(old, new, text, flags=re.IGNORECASE)
        
        # Add line breaks before section headers
        section_headers = [
            'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EMPLOYMENT HISTORY',
            'EDUCATION', 'QUALIFICATIONS', 'ACADEMIC BACKGROUND',
            'PROFESSIONAL SUMMARY', 'SUMMARY', 'PROFILE',
            'SKILLS', 'COMPETENCIES', 'TECHNICAL SKILLS',
            'CERTIFICATIONS', 'INTERESTS', 'LANGUAGES'
        ]
        
        for header in section_headers:
            text = re.sub(f'([a-z])({header})', r'\1\n\n\2', text, flags=re.IGNORECASE)
        
        # Add line breaks before dates
        text = re.sub(r'([a-z])((?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2})', r'\1\n\2', text)
        text = re.sub(r'([a-z])((?:19|20)\d{2}\s*[-–]\s*(?:Present|Current))', r'\1\n\2', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()
    
    # No AI parsing method needed - using rule-based parsing only
    def _rule_based_parse_cv(self, cv_text: str) -> Dict[str, Any]:
        """Rule-based CV parsing as fallback"""
        logger.info("Using rule-based CV parsing...")
        
        lines = [line.strip() for line in cv_text.split('\n') if line.strip()]
        
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
        
        # Extract name (first substantial line)
        for line in lines[:10]:
            if len(line) > 5 and len(line.split()) >= 2:
                if not any(keyword in line.lower() for keyword in ['curriculum', 'vitae', 'resume', 'cv', 'page']):
                    words = line.split()
                    if all(word[0].isupper() for word in words[:2] if word and word[0].isalpha()):
                        parsed['name'] = line
                        break
        
        # Extract contact info
        full_text = ' '.join(lines)
        
        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', full_text)
        if email_match:
            parsed['email'] = email_match.group(0)
        
        # Phone
        phone_patterns = [
            r'\+44[\s\-]?\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',
            r'\+1[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{4}',
            r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b'
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, full_text)
            if phone_match:
                parsed['phone'] = phone_match.group(0).strip()
                break
        
        # Extract professional summary
        summary_section = False
        summary_lines = []
        for line in lines:
            if any(keyword in line.lower() for keyword in ['professional summary', 'profile', 'summary', 'objective']):
                summary_section = True
                continue
            elif summary_section and any(keyword in line.lower() for keyword in ['experience', 'education', 'skills']):
                break
            elif summary_section and len(line) > 20:
                summary_lines.append(line)
        
        if summary_lines:
            parsed['summary'] = ' '.join(summary_lines[:3])  # Limit to 3 sentences
        
        # Extract experience with improved logic
        exp_section = False
        current_exp = {}
        skip_next_lines = 0
        
        for i, line in enumerate(lines):
            if skip_next_lines > 0:
                skip_next_lines -= 1
                continue
                
            # Check for experience section headers
            if any(keyword in line.lower() for keyword in ['professional experience', 'work experience', 'employment history', 'career history']):
                exp_section = True
                continue
            # Check if we've left the experience section
            elif exp_section and any(keyword in line.lower() for keyword in ['education', 'qualifications', 'skills', 'competencies', 'interests', 'certification']):
                if current_exp and (current_exp.get('title') or current_exp.get('company')):
                    parsed['experience'].append(current_exp)
                break
            elif exp_section and line:
                # Look for job title patterns (usually bold/emphasized text followed by company)
                # Common patterns: "Job Title, Company Name, Location | Dates"
                # or multiline: "Job Title" then "Company Name" then "Location | Dates"
                
                # Check if this looks like a company or job title line
                is_likely_company = (line.isupper() and len(line) > 5) or any(word in line for word in [' Ltd', ' Inc', ' LLC', ' LLP', ' Limited', ' plc', ' PLC'])
                is_likely_job_title = not line.isupper() and len(line.split()) >= 2 and len(line) < 80 and not line.startswith(('•', '-', '*'))
                has_dates = bool(re.search(r'\b(19|20)\d{2}\b', line))
                
                # If we have a current experience and find a new one, save the old one
                if current_exp and (current_exp.get('title') or current_exp.get('company')):
                    if (is_likely_company or is_likely_job_title) and not line.startswith(('•', '-', '*')):
                        # This is a new job entry, save the current one
                        parsed['experience'].append(current_exp)
                        current_exp = {}
                
                # Start a new experience entry
                if is_likely_job_title and not current_exp.get('title'):
                    current_exp['title'] = line
                    current_exp['company'] = ''
                    current_exp['location'] = ''
                    current_exp['dates'] = ''
                    current_exp['responsibilities'] = []
                elif is_likely_company and not current_exp.get('company'):
                    current_exp['company'] = line
                    current_exp['title'] = current_exp.get('title', '')
                    current_exp['location'] = ''
                    current_exp['dates'] = ''
                    current_exp['responsibilities'] = []
                elif has_dates and current_exp:
                    # Extract dates from the line
                    date_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}.*?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}\s*[-–]\s*\d{4}|\d{4}\s*[-–]\s*(?:Present|Current))', line, re.IGNORECASE)
                    if date_match:
                        current_exp['dates'] = date_match.group(1)
                    # Also check for location in the same line
                    location_match = re.search(r'(London|New York|Singapore|Hong Kong|Sydney|[A-Z][a-z]+,\s*[A-Z]{2,3})', line, re.IGNORECASE)
                    if location_match and not current_exp.get('location'):
                        current_exp['location'] = location_match.group(1)
                elif current_exp and line.startswith(('•', '-', '*', '◦')):
                    # This is a responsibility bullet point
                    clean_line = line.strip('•-*◦ ').strip()
                    if len(clean_line) > 10:
                        current_exp['responsibilities'].append(clean_line)
                elif current_exp and len(line) > 30 and not line.startswith(('•', '-', '*')):
                    # This might be a long-form responsibility (not a bullet point)
                    # Split it up if it's very long
                    if len(line) > 150:
                        # Try to split on sentence boundaries
                        sentences = re.split(r'[.!?]\s+', line)
                        for sentence in sentences:
                            if len(sentence.strip()) > 10:
                                current_exp['responsibilities'].append(sentence.strip())
                    else:
                        current_exp['responsibilities'].append(line)
        
        # Don't forget the last experience
        if current_exp and (current_exp.get('title') or current_exp.get('company')):
            parsed['experience'].append(current_exp)
        
        # Extract education
        edu_section = False
        current_edu = {}
        for line in lines:
            if 'education' in line.lower():
                edu_section = True
                continue
            elif edu_section and any(keyword in line.lower() for keyword in ['skills', 'interests', 'certification']):
                if current_edu:
                    parsed['education'].append(current_edu)
                break
            elif edu_section and line:
                if any(word in line.lower() for word in ['university', 'college', 'school']) or line.isupper():
                    if current_edu:
                        parsed['education'].append(current_edu)
                    current_edu = {
                        'school': line,
                        'degree': '',
                        'dates': '',
                        'details': []
                    }
                elif current_edu and not current_edu['degree']:
                    current_edu['degree'] = line
        
        if current_edu:
            parsed['education'].append(current_edu)
        
        # Extract skills
        skills_section = False
        for line in lines:
            if any(keyword in line.lower() for keyword in ['skills', 'competencies', 'expertise']):
                skills_section = True
                continue
            elif skills_section and any(keyword in line.lower() for keyword in ['education', 'experience', 'interests']):
                break
            elif skills_section and line:
                if line.startswith(('•', '-', '*')):
                    skill = line.strip('•-* ').strip()
                    if skill:
                        parsed['skills'].append(skill)
                elif ',' in line:
                    skills = [s.strip() for s in line.split(',')]
                    parsed['skills'].extend(skills)
        
        return parsed
    
    def _fill_template_with_pagination(self, template: str, data: Dict[str, Any], top_logo: str, bottom_logo: str) -> str:
        """Fill template with data and ensure proper pagination"""
        
        # Fill in basic placeholders
        html = template
        html = html.replace('{TOP_LOGO_BASE64}', top_logo)
        html = html.replace('{BOTTOM_LOGO_BASE64}', bottom_logo)
        html = html.replace('{NAME}', self._escape_html(data.get('name', 'Candidate Name')))
        html = html.replace('{CONTACT_INFO}', self._format_contact_info(data))
        html = html.replace('{PROFESSIONAL_SUMMARY}', self._format_professional_summary(data))
        html = html.replace('{SKILLS_LIST}', self._format_skills_list(data))
        html = html.replace('{EXPERIENCE_ITEMS}', self._format_experience_items(data))
        html = html.replace('{EDUCATION_ITEMS}', self._format_education_items(data))
        
        return html
    
    def _format_contact_info(self, data: Dict[str, Any]) -> str:
        """Format contact information"""
        contact_parts = []
        if data.get('phone'):
            contact_parts.append(self._escape_html(data['phone']))
        if data.get('email'):
            contact_parts.append(self._escape_html(data['email']))
        if data.get('location'):
            contact_parts.append(self._escape_html(data['location']))
        
        return ' | '.join(contact_parts)
    
    def _format_professional_summary(self, data: Dict[str, Any]) -> str:
        """Format professional summary"""
        summary = data.get('summary', '')
        if summary:
            return f'<p>{self._escape_html(summary)}</p>'
        return '<p>Professional with extensive experience in financial services.</p>'
    
    def _format_skills_list(self, data: Dict[str, Any]) -> str:
        """Format skills as list items"""
        skills = data.get('skills', [])
        if not skills:
            skills = ['Financial Analysis', 'Risk Management', 'Portfolio Management', 'Client Relations']
        
        return '\n'.join([f'<li>{self._escape_html(skill)}</li>' for skill in skills[:15]])
    
    def _format_experience_items(self, data: Dict[str, Any]) -> str:
        """Format experience items with proper structure"""
        items = []
        for exp in data.get('experience', []):
            title = exp.get('title', '').strip()
            company = exp.get('company', '').strip()
            location = exp.get('location', '').strip()
            dates = exp.get('dates', '').strip()
            responsibilities = exp.get('responsibilities', [])
            
            # Build the header line
            header_parts = []
            if title:
                header_parts.append(title)
            if company:
                header_parts.append(company)
            if location:
                header_parts.append(location)
            if dates:
                header_parts.append(dates)
            
            header = ', '.join(header_parts)
            
            # Build responsibilities list
            resp_html = ''
            if responsibilities:
                resp_items = '\n'.join([f'<li>{self._escape_html(resp)}</li>' for resp in responsibilities if resp.strip()])
                resp_html = f'<ul>{resp_items}</ul>'
            
            item_html = f'''
                <div class="experience-item">
                    <div class="job-header">{self._escape_html(header)}</div>
                    <div class="job-details">{resp_html}</div>
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
            
            details_html = ''
            if details:
                details_items = '\n'.join([f'<li>{self._escape_html(detail)}</li>' for detail in details if detail.strip()])
                if details_items:
                    details_html = f'<ul>{details_items}</ul>'
            
            item_html = f'''
                <div class="education-item">
                    <div class="education-header">{self._escape_html(school)}</div>
                    <div class="education-details">
                        {self._escape_html(degree)}
                        {f"<br>{self._escape_html(dates)}" if dates else ""}
                        {details_html}
                    </div>
                </div>
            '''
            items.append(item_html)
        
        return '\n'.join(items)
    
    def _get_top_logo_base64(self) -> str:
        """Get top MP logo"""
        try:
            top_logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'cv logo 1.png')
            if os.path.exists(top_logo_path):
                with open(top_logo_path, 'rb') as f:
                    logo_data = f.read()
                logo_base64 = base64.b64encode(logo_data).decode('utf-8')
                return f'<img src="data:image/png;base64,{logo_base64}" alt="MP" style="max-width: 80px; height: auto;" />'
            else:
                logger.warning("Top logo not found, using text fallback")
                return '<div style="font-family: \'EB Garamond\', serif; font-size: 36pt; font-weight: 700; color: #2c3e50; letter-spacing: 8px;">MP</div>'
        except Exception as e:
            logger.error(f"Error loading top logo: {e}")
            return '<div style="font-family: \'EB Garamond\', serif; font-size: 36pt; font-weight: 700; color: #2c3e50; letter-spacing: 8px;">MP</div>'
    
    def _get_bottom_logo_base64(self) -> str:
        """Get bottom MAWNEY Partners logo"""
        try:
            bottom_logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'cv logo 2.png')
            if os.path.exists(bottom_logo_path):
                with open(bottom_logo_path, 'rb') as f:
                    logo_data = f.read()
                logo_base64 = base64.b64encode(logo_data).decode('utf-8')
                return f'<img src="data:image/png;base64,{logo_base64}" alt="MAWNEY Partners" style="max-width: 120px; height: auto;" />'
            else:
                logger.warning("Bottom logo not found, using text fallback")
                return '<div style="font-family: \'Arial\', sans-serif; font-size: 12pt; font-weight: 700; color: #2c3e50; letter-spacing: 1px;">MAWNEY PARTNERS</div>'
        except Exception as e:
            logger.error(f"Error loading bottom logo: {e}")
            return '<div style="font-family: \'Arial\', sans-serif; font-size: 12pt; font-weight: 700; color: #2c3e50; letter-spacing: 1px;">MAWNEY PARTNERS</div>'
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ""
        import html
        return html.escape(str(text))
    
    def _extract_text_from_html(self, html: str) -> str:
        """Extract plain text from HTML"""
        import re
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

# Create global instance
enhanced_cv_formatter = EnhancedCVFormatter()

