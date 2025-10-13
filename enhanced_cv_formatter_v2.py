#!/usr/bin/env python3
"""
Enhanced CV Formatter V2 for Mawney Partners
Completely rewritten to fix content parsing, rewriting, and organizing issues
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

class EnhancedCVFormatterV2:
    """Enhanced CV formatter with proper content parsing and organization"""
    
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
        
    def format_cv_with_template(self, cv_data: str, filename: str = '') -> Dict[str, Any]:
        """Format CV using the Mawney Partners template with improved parsing"""
        try:
            logger.info(f"=== ENHANCED CV FORMATTING V2 STARTED ===")
            logger.info(f"Filename: {filename}")
            logger.info(f"Raw CV data length: {len(cv_data)} characters")
            
            # Step 1: Clean and preprocess the CV text
            cleaned_cv = self._clean_cv_text(cv_data)
            logger.info(f"Cleaned CV data length: {len(cleaned_cv)} characters")
            
            # Step 2: Parse CV with improved logic
            parsed_data = self._parse_cv_content(cleaned_cv)
            logger.info(f"Parsed CV data: {json.dumps({k: (v if not isinstance(v, (list, str)) or len(str(v)) < 100 else str(v)[:100] + '...') for k, v in parsed_data.items()}, indent=2)}")
            
            # Step 3: Load the HTML template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Step 4: Get logos
            top_logo_base64 = self._get_top_logo_base64()
            bottom_logo_base64 = self._get_bottom_logo_base64()
            
            # Step 5: Fill in the template
            formatted_html = self._fill_template_with_data(
                template, 
                parsed_data, 
                top_logo_base64, 
                bottom_logo_base64
            )
            
            logger.info(f"Generated HTML length: {len(formatted_html)} characters")
            logger.info(f"=== ENHANCED CV FORMATTING V2 COMPLETED ===")
            
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
            logger.error(f"Error in enhanced CV formatting V2: {e}", exc_info=True)
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
            ('theuniversities', 'the universities'),
            ('andbusiness', 'and business'),
            ('schoolsranking', 'schools ranking'),
            ('usingquantitativemethods', 'using quantitative methods'),
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
    
    def _parse_cv_content(self, cv_text: str) -> Dict[str, Any]:
        """Parse CV content with improved logic for better extraction"""
        logger.info("Using enhanced CV parsing V2...")
        
        lines = [line.strip() for line in cv_text.split('\n') if line.strip()]
        
        parsed = {
            'name': '',
            'email': '',
            'phone': '',
            'location': '',
            'experience': [],
            'education': [],
            'languages': [],
            'computer_skills': [],
            'extra_curricular': []
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
        
        # Extract experience with COMPLETELY NEW LOGIC
        parsed['experience'] = self._extract_experience_enhanced(lines)
        
        # Extract education with COMPLETELY NEW LOGIC
        parsed['education'] = self._extract_education_enhanced(lines)
        
        # Extract languages and computer skills
        parsed['languages'], parsed['computer_skills'] = self._extract_languages_and_skills(lines)
        
        # Extract extra curricular activities
        parsed['extra_curricular'] = self._extract_extra_curricular(lines)
        
        return parsed
    
    def _extract_experience_enhanced(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Enhanced experience extraction with better parsing and rewriting"""
        experience = []
        in_experience_section = False
        current_experience = {}
        
        for i, line in enumerate(lines):
            # Check for experience section start
            if any(keyword in line.lower() for keyword in ['professional experience', 'work experience', 'employment history', 'career history']):
                in_experience_section = True
                continue
            
            # Check if we've left the experience section
            if in_experience_section and any(keyword in line.lower() for keyword in ['education', 'qualifications', 'skills', 'competencies', 'interests', 'certification', 'languages']):
                if current_experience:
                    experience.append(current_experience)
                break
            
            if in_experience_section and line:
                # Look for company/job patterns
                if self._is_company_or_job_line(line):
                    # Save previous experience
                    if current_experience and (current_experience.get('company') or current_experience.get('title')):
                        experience.append(current_experience)
                    
                    # Start new experience
                    current_experience = self._parse_experience_line(line)
                elif current_experience:
                    # This is likely a responsibility or detail
                    if line.startswith(('•', '-', '*', '◦')):
                        clean_line = line.strip('•-*◦ ').strip()
                        if len(clean_line) > 10:
                            current_experience['responsibilities'].append(clean_line)
                    elif len(line) > 20:
                        # Long line might be a responsibility
                        current_experience['responsibilities'].append(line)
        
        # Don't forget the last experience
        if current_experience and (current_experience.get('company') or current_experience.get('title')):
            experience.append(current_experience)
        
        # Clean and rewrite responsibilities
        for exp in experience:
            exp['responsibilities'] = self._rewrite_responsibilities(exp.get('responsibilities', []))
        
        return experience
    
    def _is_company_or_job_line(self, line: str) -> bool:
        """Check if line is likely a company or job title"""
        # Check for company indicators
        company_indicators = [
            'LTD', 'LLC', 'INC', 'CORP', 'PLC', 'PARTNERS', 'CAPITAL', 
            'MANAGEMENT', 'BANK', 'GROUP', 'INVESTMENT', 'GLOBAL', 'FUND'
        ]
        
        # Check for job title indicators
        job_title_indicators = [
            'ANALYST', 'MANAGER', 'DIRECTOR', 'OFFICER', 'SPECIALIST',
            'ASSOCIATE', 'VP', 'VICE PRESIDENT', 'PRESIDENT', 'CEO',
            'CFO', 'COO', 'HEAD', 'LEAD', 'SENIOR', 'JUNIOR'
        ]
        
        line_upper = line.upper()
        
        # Check if it's a company name (all caps, contains company indicators)
        if line.isupper() and len(line) > 5:
            if any(indicator in line_upper for indicator in company_indicators):
                return True
        
        # Check if it's a job title (title case, contains job indicators)
        if line.istitle() and any(indicator in line_upper for indicator in job_title_indicators):
            return True
        
        # Check for date patterns (suggests this is a job entry)
        if re.search(r'\b(19|20)\d{2}\b', line):
            return True
        
        return False
    
    def _parse_experience_line(self, line: str) -> Dict[str, Any]:
        """Parse a single experience line to extract company, title, dates"""
        # Extract dates
        date_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}.*?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}\s*[-–]\s*\d{4}|\d{4}\s*[-–]\s*(?:Present|Current|Now))', line, re.IGNORECASE)
        dates = date_match.group(1) if date_match else ""
        
        # Remove dates from the line to get company/title
        clean_line = re.sub(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}.*?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}\s*[-–]\s*\d{4}|\d{4}\s*[-–]\s*(?:Present|Current|Now))', '', line, flags=re.IGNORECASE).strip()
        
        # Determine if this is a company or job title
        if line.isupper() and len(clean_line) > 5:
            # This is a company name
            return {
                'company': clean_line,
                'title': '',
                'dates': dates,
                'responsibilities': []
            }
        else:
            # This is a job title
            return {
                'company': '',
                'title': clean_line,
                'dates': dates,
                'responsibilities': []
            }
    
    def _rewrite_responsibilities(self, responsibilities: List[str]) -> List[str]:
        """Rewrite and clean up responsibilities to be more concise and impactful"""
        rewritten = []
        
        for resp in responsibilities:
            # Clean up the responsibility
            clean_resp = resp.strip()
            if len(clean_resp) < 10:
                continue
            
            # Remove redundant words and make more concise
            clean_resp = re.sub(r'\b(was|were|is|are|been|being)\s+(responsible for|in charge of|tasked with)\s+', '', clean_resp, flags=re.IGNORECASE)
            clean_resp = re.sub(r'\b(helped|assisted|supported|worked on|involved in)\s+', '', clean_resp, flags=re.IGNORECASE)
            
            # Capitalize first letter
            if clean_resp and not clean_resp[0].isupper():
                clean_resp = clean_resp[0].upper() + clean_resp[1:]
            
            # Add action verb if missing
            if not any(verb in clean_resp.lower() for verb in ['managed', 'developed', 'created', 'implemented', 'analyzed', 'led', 'designed', 'built', 'executed', 'delivered', 'achieved']):
                if clean_resp.lower().startswith('the '):
                    clean_resp = 'Managed ' + clean_resp[4:]
                elif not clean_resp.lower().startswith(('managed', 'developed', 'created', 'implemented', 'analyzed', 'led', 'designed', 'built', 'executed', 'delivered', 'achieved')):
                    clean_resp = 'Developed ' + clean_resp
            
            # Limit length
            if len(clean_resp) > 150:
                # Try to find a good break point
                sentences = clean_resp.split('.')
                if len(sentences) > 1:
                    clean_resp = sentences[0] + '.'
                else:
                    clean_resp = clean_resp[:147] + '...'
            
            if len(clean_resp) > 10:
                rewritten.append(clean_resp)
        
        return rewritten[:6]  # Limit to 6 most important responsibilities
    
    def _extract_education_enhanced(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Enhanced education extraction with better parsing"""
        education = []
        in_education_section = False
        current_education = {}
        
        for i, line in enumerate(lines):
            # Check for education section start
            if 'education' in line.lower():
                in_education_section = True
                continue
            
            # Check if we've left the education section
            if in_education_section and any(keyword in line.lower() for keyword in ['skills', 'competencies', 'interests', 'certification', 'languages', 'experience']):
                if current_education:
                    education.append(current_education)
                break
            
            if in_education_section and line:
                # Look for university/school patterns
                if any(word in line.lower() for word in ['university', 'college', 'school', 'institute']) or line.isupper():
                    # Save previous education
                    if current_education and current_education.get('school'):
                        education.append(current_education)
                    
                    # Start new education
                    current_education = {
                        'school': line,
                        'degree': '',
                        'dates': '',
                        'details': []
                    }
                elif current_education and not current_education['degree']:
                    # This is likely the degree
                    current_education['degree'] = line
                elif current_education and line.startswith(('•', '-', '*')):
                    # This is a detail
                    clean_line = line.strip('•-* ').strip()
                    if len(clean_line) > 5:
                        current_education['details'].append(clean_line)
        
        # Don't forget the last education
        if current_education and current_education.get('school'):
            education.append(current_education)
        
        return education
    
    def _extract_languages_and_skills(self, lines: List[str]) -> tuple[List[str], List[str]]:
        """Extract languages and computer skills"""
        languages = []
        computer_skills = []
        
        in_skills_section = False
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['languages', 'skills', 'computer', 'technical']):
                in_skills_section = True
                continue
            
            if in_skills_section and any(keyword in line.lower() for keyword in ['education', 'experience', 'interests', 'certification']):
                break
            
            if in_skills_section and line:
                if line.startswith(('•', '-', '*')):
                    clean_line = line.strip('•-* ').strip()
                    
                    # Categorize as language or computer skill
                    if any(lang in clean_line.lower() for lang in ['english', 'french', 'spanish', 'german', 'italian', 'chinese', 'japanese', 'arabic', 'russian', 'portuguese', 'native', 'fluent', 'basic', 'intermediate', 'advanced']):
                        languages.append(clean_line)
                    elif any(skill in clean_line.lower() for skill in ['ms office', 'excel', 'word', 'powerpoint', 'vba', 'c++', 'python', 'java', 'sql', 'bloomberg', 'reuters', 'it:', 'computer:', 'software']):
                        computer_skills.append(clean_line)
        
        return languages, computer_skills
    
    def _extract_extra_curricular(self, lines: List[str]) -> List[str]:
        """Extract extra curricular activities"""
        activities = []
        
        in_activities_section = False
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['extra curricular', 'activities', 'interests', 'hobbies', 'volunteer']):
                in_activities_section = True
                continue
            
            if in_activities_section and any(keyword in line.lower() for keyword in ['education', 'experience', 'skills', 'certification']):
                break
            
            if in_activities_section and line:
                if line.startswith(('•', '-', '*')):
                    clean_line = line.strip('•-* ').strip()
                    if len(clean_line) > 10:
                        activities.append(clean_line)
        
        return activities
    
    def _fill_template_with_data(self, template: str, data: Dict[str, Any], top_logo: str, bottom_logo: str) -> str:
        """Fill template with data"""
        
        # Fill in basic placeholders
        html = template
        html = html.replace('{TOP_LOGO_BASE64}', top_logo)
        html = html.replace('{BOTTOM_LOGO_BASE64}', bottom_logo)
        html = html.replace('{NAME}', self._escape_html(data.get('name', 'Candidate Name')))
        html = html.replace('{CONTACT_INFO}', self._format_contact_info(data))
        html = html.replace('{EXPERIENCE_ITEMS}', self._format_experience_items_enhanced(data))
        html = html.replace('{EDUCATION_ITEMS}', self._format_education_items_enhanced(data))
        html = html.replace('{SKILLS_LIST}', self._format_skills_enhanced(data))
        
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
    
    def _format_experience_items_enhanced(self, data: Dict[str, Any]) -> str:
        """Format experience items with proper company/title/dates layout"""
        items = []
        for exp in data.get('experience', []):
            company = exp.get('company', '').strip()
            title = exp.get('title', '').strip()
            dates = exp.get('dates', '').strip()
            responsibilities = exp.get('responsibilities', [])
            
            # Build the header with company/title on left, dates on right
            if company and title:
                header_text = f"{company}, {title}"
            elif company:
                header_text = company
            elif title:
                header_text = title
            else:
                continue
            
            # Build responsibilities list
            resp_html = ''
            if responsibilities:
                resp_items = '\n'.join([f'<li>{self._escape_html(resp)}</li>' for resp in responsibilities if resp.strip()])
                resp_html = f'<ul>{resp_items}</ul>'
            
            # Format with proper layout
            item_html = f'''
                <div class="experience-item">
                    <div class="job-header">
                        <div class="job-title-company">{self._escape_html(header_text)}</div>
                        <div class="job-dates">{self._escape_html(dates)}</div>
                    </div>
                    <div class="job-details">{resp_html}</div>
                </div>
            '''
            items.append(item_html)
        
        return '\n'.join(items)
    
    def _format_education_items_enhanced(self, data: Dict[str, Any]) -> str:
        """Format education items with proper layout"""
        items = []
        for edu in data.get('education', []):
            school = edu.get('school', '')
            degree = edu.get('degree', '')
            dates = edu.get('dates', '')
            details = edu.get('details', [])
            
            if not school:
                continue
            
            details_html = ''
            if details:
                details_items = '\n'.join([f'<li>{self._escape_html(detail)}</li>' for detail in details if detail.strip()])
                if details_items:
                    details_html = f'<ul>{details_items}</ul>'
            
            item_html = f'''
                <div class="education-item">
                    <div class="education-header">
                        <div class="job-title-company">{self._escape_html(school)}</div>
                        <div class="job-dates">{self._escape_html(dates)}</div>
                    </div>
                    <div class="education-details">
                        {self._escape_html(degree)}
                        {details_html}
                    </div>
                </div>
            '''
            items.append(item_html)
        
        return '\n'.join(items)
    
    def _format_skills_enhanced(self, data: Dict[str, Any]) -> str:
        """Format skills - only include if relevant information exists"""
        skills_html = ''
        
        # Languages
        languages = data.get('languages', [])
        if languages:
            skills_html += '<div class="section-header">LANGUAGES</div>\n'
            skills_html += '<ul class="skills-list">\n'
            skills_html += '\n'.join([f'<li>{self._escape_html(lang)}</li>' for lang in languages])
            skills_html += '</ul>\n'
        
        # Computer Skills
        computer_skills = data.get('computer_skills', [])
        if computer_skills:
            skills_html += '<div class="section-header">COMPUTER SKILLS</div>\n'
            skills_html += '<ul class="skills-list">\n'
            skills_html += '\n'.join([f'<li>{self._escape_html(skill)}</li>' for skill in computer_skills])
            skills_html += '</ul>\n'
        
        # Extra Curricular
        extra_curricular = data.get('extra_curricular', [])
        if extra_curricular:
            skills_html += '<div class="section-header">EXTRA CURRICULAR ACTIVITIES</div>\n'
            skills_html += '<ul class="skills-list">\n'
            skills_html += '\n'.join([f'<li>{self._escape_html(activity)}</li>' for activity in extra_curricular])
            skills_html += '</ul>\n'
        
        return skills_html
    
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
                return f'<img src="data:image/png;base64,{logo_base64}" alt="MAWNEY Partners" style="max-width: 110px; height: auto;" />'
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
enhanced_cv_formatter_v2 = EnhancedCVFormatterV2()

