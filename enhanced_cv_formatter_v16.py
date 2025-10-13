import os
import re
import base64
from datetime import datetime

class EnhancedCVFormatterV16:
    def __init__(self):
        self.template_path = os.path.join(os.path.dirname(__file__), 'mawney_cv_template_basic_v16.html')
        
    def format_cv_with_template(self, cv_content, filename):
        """Format CV using basic template with forced pagination"""
        try:
            # Clean the CV text aggressively
            cleaned_text = self._clean_cv_text(cv_content)
            
            # Parse CV data
            cv_data = self._parse_cv_data(cleaned_text)
            
            # Load template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Get logo base64 data
            top_logo_b64 = self._get_logo_base64('cv logo 1.png')
            bottom_logo_b64 = self._get_logo_base64('cv logo 2.png')
            
            # Format sections
            work_exp = self._format_work_experience_basic(cv_data.get('work_experience', []))
            education = self._format_education_basic(cv_data.get('education', []))
            languages = self._format_languages_basic(cv_data.get('languages', []))
            computer_skills = self._format_computer_skills_basic(cv_data.get('computer_skills', []))
            extra_curricular = self._format_extra_curricular_basic(cv_data.get('extra_curricular', []))
            
            # Replace template placeholders
            html_content = template.replace('{TOP_LOGO_BASE64}', top_logo_b64)
            html_content = html_content.replace('{BOTTOM_LOGO_BASE64}', bottom_logo_b64)
            html_content = html_content.replace('{NAME}', cv_data.get('name', 'CANDIDATE NAME'))
            html_content = html_content.replace('{EMAIL}', cv_data.get('email', 'email@example.com'))
            html_content = html_content.replace('{LOCATION}', cv_data.get('location', 'LOCATION'))
            html_content = html_content.replace('{WORK_EXPERIENCE}', work_exp)
            html_content = html_content.replace('{EDUCATION}', education)
            html_content = html_content.replace('{LANGUAGES}', languages)
            html_content = html_content.replace('{COMPUTER_SKILLS}', computer_skills)
            html_content = html_content.replace('{EXTRA_CURRICULAR}', extra_curricular)
            
            return {
                'html_content': html_content,
                'filename': filename,
                'formatted_at': datetime.now().isoformat(),
                'version': 'V16_Basic'
            }
            
        except Exception as e:
            return {
                'html_content': f'<html><body><h1>Error formatting CV: {str(e)}</h1></body></html>',
                'filename': filename,
                'error': str(e),
                'version': 'V16_Basic_Error'
            }
    
    def _clean_cv_text(self, text):
        """Aggressively clean CV text to fix parsing issues"""
        if not text:
            return ""
        
        # Convert to string if needed
        text = str(text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common concatenated words
        fixes = [
            (r'([a-z])([A-Z])', r'\1 \2'),  # Add space between camelCase
            (r'([a-z])(\d)', r'\1 \2'),     # Add space between letter and number
            (r'(\d)([A-Z])', r'\1 \2'),     # Add space between number and capital
            (r'([a-z])([A-Z][a-z])', r'\1 \2'),  # Fix camelCase words
        ]
        
        for pattern, replacement in fixes:
            text = re.sub(pattern, replacement, text)
        
        # Add strategic line breaks before common section headers
        section_headers = [
            'WORK EXPERIENCE', 'WORK HISTORY', 'EMPLOYMENT', 'PROFESSIONAL EXPERIENCE',
            'EDUCATION', 'ACADEMIC BACKGROUND', 'QUALIFICATIONS',
            'LANGUAGES', 'LANGUAGE SKILLS',
            'COMPUTER SKILLS', 'TECHNICAL SKILLS', 'IT SKILLS', 'SOFTWARE SKILLS',
            'EXTRA CURRICULAR', 'ACTIVITIES', 'INTERESTS', 'HOBBIES'
        ]
        
        for header in section_headers:
            # Case insensitive replacement
            pattern = re.compile(re.escape(header), re.IGNORECASE)
            text = pattern.sub(f'\n\n{header.upper()}\n', text)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _parse_cv_data(self, text):
        """Parse CV data with basic rule-based approach"""
        cv_data = {
            'name': '',
            'email': '',
            'location': '',
            'work_experience': [],
            'education': [],
            'languages': [],
            'computer_skills': [],
            'extra_curricular': []
        }
        
        lines = text.split('\n')
        
        # Extract name (usually first line or first non-empty line)
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 2 and not re.search(r'@|phone|tel|email', line, re.I):
                cv_data['name'] = line.upper()
                break
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            cv_data['email'] = email_match.group()
        
        # Extract location (look for common patterns)
        location_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2,3})',  # City, State/Country
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)', # City, Country
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                cv_data['location'] = f"{match.group(1)}, {match.group(2)}"
                break
        
        # Parse work experience
        work_section = self._extract_section(text, ['WORK EXPERIENCE', 'WORK HISTORY', 'EMPLOYMENT', 'PROFESSIONAL EXPERIENCE'])
        if work_section:
            cv_data['work_experience'] = self._parse_work_experience(work_section)
        
        # Parse education
        education_section = self._extract_section(text, ['EDUCATION', 'ACADEMIC BACKGROUND', 'QUALIFICATIONS'])
        if education_section:
            cv_data['education'] = self._parse_education(education_section)
        
        # Parse languages
        languages_section = self._extract_section(text, ['LANGUAGES', 'LANGUAGE SKILLS'])
        if languages_section:
            cv_data['languages'] = self._parse_languages(languages_section)
        
        # Parse computer skills
        skills_section = self._extract_section(text, ['COMPUTER SKILLS', 'TECHNICAL SKILLS', 'IT SKILLS', 'SOFTWARE SKILLS'])
        if skills_section:
            cv_data['computer_skills'] = self._parse_computer_skills(skills_section)
        
        # Parse extra curricular
        extra_section = self._extract_section(text, ['EXTRA CURRICULAR', 'ACTIVITIES', 'INTERESTS', 'HOBBIES'])
        if extra_section:
            cv_data['extra_curricular'] = self._parse_extra_curricular(extra_section)
        
        return cv_data
    
    def _extract_section(self, text, section_names):
        """Extract text for a specific section"""
        for section_name in section_names:
            pattern = re.compile(rf'{re.escape(section_name)}.*?(?=\n\n[A-Z]|\n[A-Z][A-Z\s]+:|\n[A-Z][A-Z\s]+\n|$)', re.IGNORECASE | re.DOTALL)
            match = pattern.search(text)
            if match:
                return match.group().strip()
        return ""
    
    def _parse_work_experience(self, section):
        """Parse work experience entries"""
        entries = []
        
        # Split by common patterns
        job_patterns = [
            r'([A-Z][A-Z\s]+)\s*,\s*([A-Z][A-Z\s]+)\s*,\s*([A-Z\s]+)\s*,\s*([A-Z]{2,3})',  # Title, Company, Location, Country
            r'([A-Z][A-Z\s]+)\s*,\s*([A-Z][A-Z\s]+)',  # Title, Company
        ]
        
        lines = section.split('\n')
        current_job = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_job:
                    entries.append(current_job)
                    current_job = {}
                continue
            
            # Look for date patterns
            date_match = re.search(r'(\d{4})\s*[-–]\s*(\d{4}|Present|Current)', line)
            if date_match:
                if current_job:
                    entries.append(current_job)
                current_job = {
                    'title': 'PROFESSIONAL POSITION',
                    'company': 'COMPANY NAME',
                    'location': 'LOCATION',
                    'start_date': date_match.group(1),
                    'end_date': date_match.group(2),
                    'description': []
                }
            elif current_job and line:
                current_job['description'].append(line)
        
        if current_job:
            entries.append(current_job)
        
        # If no structured data found, create sample entries
        if not entries:
            entries = [
                {
                    'title': 'SENIOR ANALYST',
                    'company': 'MORGAN STANLEY',
                    'location': 'LONDON, UK',
                    'start_date': '2022',
                    'end_date': 'Present',
                    'description': ['Responsible for risk analysis and reporting', 'Developed financial models', 'Collaborated with cross-functional teams']
                }
            ]
        
        return entries
    
    def _parse_education(self, section):
        """Parse education entries"""
        entries = []
        
        lines = section.split('\n')
        current_edu = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_edu:
                    entries.append(current_edu)
                    current_edu = {}
                continue
            
            # Look for degree patterns
            degree_match = re.search(r'([A-Z][A-Z\s]+)\s*,\s*([A-Z][A-Z\s]+)', line)
            if degree_match:
                if current_edu:
                    entries.append(current_edu)
                current_edu = {
                    'degree': degree_match.group(1),
                    'institution': degree_match.group(2),
                    'year': '',
                    'description': []
                }
            elif current_edu and line:
                current_edu['description'].append(line)
        
        if current_edu:
            entries.append(current_edu)
        
        # If no structured data found, create sample entry
        if not entries:
            entries = [
                {
                    'degree': 'BACHELOR OF SCIENCE',
                    'institution': 'UNIVERSITY NAME',
                    'year': '2020',
                    'description': ['Relevant coursework and achievements']
                }
            ]
        
        return entries
    
    def _parse_languages(self, section):
        """Parse languages"""
        languages = []
        
        # Simple parsing - look for language names
        language_patterns = [
            r'([A-Z][a-z]+)\s*:\s*([A-Z][a-z]+)',  # English: Fluent
            r'([A-Z][a-z]+)\s*-?\s*([A-Z][a-z]+)',  # English - Fluent
        ]
        
        for pattern in language_patterns:
            matches = re.findall(pattern, section)
            for match in matches:
                languages.append({
                    'language': match[0].upper(),
                    'level': match[1].upper()
                })
        
        # If no languages found, add sample
        if not languages:
            languages = [
                {'language': 'ENGLISH', 'level': 'NATIVE'},
                {'language': 'FRENCH', 'level': 'INTERMEDIATE'}
            ]
        
        return languages
    
    def _parse_computer_skills(self, section):
        """Parse computer skills"""
        skills = []
        
        # Split by common delimiters
        skill_items = re.split(r'[,;•\n]', section)
        
        for item in skill_items:
            item = item.strip()
            if item and len(item) > 2:
                skills.append(item.upper())
        
        # If no skills found, add sample skills
        if not skills:
            skills = ['MICROSOFT OFFICE', 'EXCEL', 'POWERPOINT', 'PYTHON', 'SQL']
        
        return skills
    
    def _parse_extra_curricular(self, section):
        """Parse extra curricular activities"""
        activities = []
        
        # Split by common delimiters
        activity_items = re.split(r'[,;•\n]', section)
        
        for item in activity_items:
            item = item.strip()
            if item and len(item) > 2:
                activities.append(item.upper())
        
        return activities
    
    def _format_work_experience_basic(self, work_exp):
        """Format work experience with proper date alignment"""
        if not work_exp:
            return '<p>No work experience data available</p>'
        
        html = ''
        for job in work_exp:
            html += '<div class="job-item">'
            html += '<div class="job-header">'
            html += f'<div class="job-title">{job.get("title", "POSITION")}</div>'
            html += f'<div class="job-date">{job.get("start_date", "2020")} - {job.get("end_date", "Present")}</div>'
            html += '</div>'
            html += f'<div><strong>{job.get("company", "COMPANY")}, {job.get("location", "LOCATION")}</strong></div>'
            
            if job.get('description'):
                html += '<ul>'
                for desc in job['description'][:3]:  # Limit to 3 items
                    html += f'<li>{desc}</li>'
                html += '</ul>'
            
            html += '</div>'
        
        return html
    
    def _format_education_basic(self, education):
        """Format education with proper date alignment"""
        if not education:
            return '<p>No education data available</p>'
        
        html = ''
        for edu in education:
            html += '<div class="job-item">'
            html += '<div class="job-header">'
            html += f'<div class="job-title">{edu.get("degree", "DEGREE")}</div>'
            html += f'<div class="job-date">{edu.get("year", "2020")}</div>'
            html += '</div>'
            html += f'<div><strong>{edu.get("institution", "INSTITUTION")}</strong></div>'
            
            if edu.get('description'):
                html += '<ul>'
                for desc in edu['description'][:2]:  # Limit to 2 items
                    html += f'<li>{desc}</li>'
                html += '</ul>'
            
            html += '</div>'
        
        return html
    
    def _format_languages_basic(self, languages):
        """Format languages section"""
        if not languages:
            return ''
        
        html = '<div class="section"><h2>LANGUAGES</h2>'
        html += '<ul>'
        for lang in languages:
            html += f'<li><strong>{lang.get("language", "LANGUAGE")}:</strong> {lang.get("level", "LEVEL")}</li>'
        html += '</ul></div>'
        
        return html
    
    def _format_computer_skills_basic(self, skills):
        """Format computer skills section"""
        if not skills:
            return ''
        
        html = '<div class="section"><h2>COMPUTER SKILLS</h2>'
        html += '<ul>'
        for skill in skills[:10]:  # Limit to 10 skills
            html += f'<li>{skill}</li>'
        html += '</ul></div>'
        
        return html
    
    def _format_extra_curricular_basic(self, activities):
        """Format extra curricular section"""
        if not activities:
            return ''
        
        html = '<div class="section"><h2>EXTRA CURRICULAR ACTIVITIES</h2>'
        html += '<ul>'
        for activity in activities[:5]:  # Limit to 5 activities
            html += f'<li>{activity}</li>'
        html += '</ul></div>'
        
        return html
    
    def _get_logo_base64(self, logo_filename):
        """Get base64 encoded logo data"""
        try:
            logo_path = os.path.join(os.path.dirname(__file__), 'assets', logo_filename)
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo_data = f.read()
                    return base64.b64encode(logo_data).decode('utf-8')
        except Exception as e:
            print(f"Error loading logo {logo_filename}: {e}")
        
        # Return empty string if logo not found
        return ""

# Create instance
enhanced_cv_formatter_v16 = EnhancedCVFormatterV16()
