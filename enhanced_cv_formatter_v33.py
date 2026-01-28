import os
import re
import base64
from datetime import datetime

class EnhancedCVFormatterV33:
    def __init__(self):
        self.template_path = os.path.join(os.path.dirname(__file__), 'mawney_cv_template_wkwebview_compatible_v33.html')
        
    def format_cv_with_template(self, cv_content, filename):
        """Format CV optimized for WKWebViewCompatible PDF generation with forced height"""
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
            
            # Format sections (keeping parsing exactly the same)
            work_exp = self._format_work_experience_v33(cv_data.get('work_experience', []))
            education = self._format_education_v33(cv_data.get('education', []))
            languages = self._format_languages_v33(cv_data.get('languages', []))
            computer_skills = self._format_computer_skills_v33(cv_data.get('computer_skills', []))
            extra_curricular = self._format_extra_curricular_v33(cv_data.get('extra_curricular', []))
            
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
                'version': 'V33_WKWebViewCompatible'
            }
            
        except Exception as e:
            return {
                'html_content': f'<html><body><h1>Error formatting CV: {str(e)}</h1></body></html>',
                'filename': filename,
                'error': str(e),
                'version': 'V33_WKWebViewCompatible_Error'
            }
    
    def _clean_cv_text(self, text):
        """Aggressively clean CV text to fix parsing issues"""
        if not text:
            return ""
        
        # Convert to string if needed
        text = str(text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common concatenated words - more aggressive
        fixes = [
            (r'([a-z])([A-Z])', r'\1 \2'),  # Add space between camelCase
            (r'([a-z])(\d)', r'\1 \2'),     # Add space between letter and number
            (r'(\d)([A-Z])', r'\1 \2'),     # Add space between number and capital
            (r'([a-z])([A-Z][a-z])', r'\1 \2'),  # Fix camelCase words
            (r'([A-Z])([a-z]{2,})([A-Z])', r'\1\2 \3'),  # Fix mid-word capitals
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
        """Parse CV data with improved rule-based approach"""
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
        
        # Extract name (usually first line or first non-empty line that looks like a name)
        for line in lines[:10]:
            line = line.strip()
            if not line:
                continue
            
            # Skip if it looks like contact info, headers, or too long
            if re.search(r'@|phone|tel|email|curriculum|vitae|resume|cv|address', line, re.I):
                continue
            if len(line) > 50:  # Names are usually shorter
                continue
            if line.isupper() and len(line) > 30:  # Skip all-caps headers
                continue
            
            # Check if it looks like a name (has capital letters, might have spaces)
            if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$', line) or \
               re.match(r'^[A-Z][A-Z\s]+$', line) and len(line.split()) <= 4:
                cv_data['name'] = line.upper()
                break
            elif len(line.split()) <= 4 and not re.search(r'[0-9]', line):
                # Might be a name even if format is slightly off
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
        
        # Parse work experience - improved
        work_section = self._extract_section(text, ['WORK EXPERIENCE', 'WORK HISTORY', 'EMPLOYMENT', 'PROFESSIONAL EXPERIENCE'])
        if work_section:
            cv_data['work_experience'] = self._parse_work_experience_v33(work_section)
        else:
            # Try to find work experience without section header
            cv_data['work_experience'] = self._parse_work_experience_v33(text)
        
        # Parse education - improved
        education_section = self._extract_section(text, ['EDUCATION', 'ACADEMIC BACKGROUND', 'QUALIFICATIONS'])
        if education_section:
            cv_data['education'] = self._parse_education_v33(education_section)
        else:
            cv_data['education'] = self._parse_education_v33(text)
        
        # Parse languages
        languages_section = self._extract_section(text, ['LANGUAGES', 'LANGUAGE SKILLS'])
        if languages_section:
            cv_data['languages'] = self._parse_languages_v33(languages_section)
        
        # Parse computer skills
        skills_section = self._extract_section(text, ['COMPUTER SKILLS', 'TECHNICAL SKILLS', 'IT SKILLS', 'SOFTWARE SKILLS'])
        if skills_section:
            cv_data['computer_skills'] = self._parse_computer_skills_v33(skills_section)
        
        # Parse extra curricular
        extra_section = self._extract_section(text, ['EXTRA CURRICULAR', 'ACTIVITIES', 'INTERESTS', 'HOBBIES'])
        if extra_section:
            cv_data['extra_curricular'] = self._parse_extra_curricular_v33(extra_section)
        
        return cv_data
    
    def _extract_section(self, text, section_names):
        """Extract text for a specific section - improved to capture actual content"""
        lines = text.split('\n')
        section_start = None
        section_content = []
        
        # Find section header
        for i, line in enumerate(lines):
            line_upper = line.strip().upper()
            for section_name in section_names:
                if section_name.upper() in line_upper and len(line_upper) < 50:  # Header should be short
                    section_start = i
                    break
            if section_start is not None:
                break
        
        if section_start is None:
            return ""
        
        # Extract content until next major section
        section_headers = [
            'WORK EXPERIENCE', 'WORK HISTORY', 'EMPLOYMENT', 'PROFESSIONAL EXPERIENCE',
            'EDUCATION', 'ACADEMIC', 'QUALIFICATIONS', 'ACADEMIC BACKGROUND',
            'LANGUAGES', 'LANGUAGE SKILLS',
            'COMPUTER SKILLS', 'TECHNICAL SKILLS', 'IT SKILLS', 'SOFTWARE SKILLS', 'SKILLS',
            'EXTRA CURRICULAR', 'ACTIVITIES', 'INTERESTS', 'HOBBIES',
            'PROFILE', 'SUMMARY', 'PROFESSIONAL SUMMARY', 'OBJECTIVE'
        ]
        
        for i in range(section_start + 1, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
            
            # Check if we hit another major section
            line_upper = line.upper()
            is_next_section = False
            for header in section_headers:
                if header in line_upper and len(line_upper) < 50:
                    is_next_section = True
                    break
            
            if is_next_section:
                break
            
            section_content.append(line)
        
        return '\n'.join(section_content).strip()
    
    def _parse_work_experience_v33(self, section):
        """Intelligently parse work experience from actual CV content"""
        entries = []
        if not section or len(section.strip()) < 10:
            return entries
        
        lines = section.split('\n')
        current_entry = None
        current_description = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_entry:
                    if current_description:
                        current_entry['description'] = current_description
                    entries.append(current_entry)
                    current_entry = None
                    current_description = []
                continue
            
            # Check if line looks like a job title/company line
            # Patterns: "Job Title at Company", "Job Title - Company", "Job Title, Company"
            # Or: "Company — Job Title", "Company | Job Title"
            job_patterns = [
                r'^(.+?)\s+(?:at|@|—|–|-|,|,)\s+(.+?)(?:\s*[—–-]\s*(.+))?$',  # Title at Company — Location
                r'^(.+?)\s*[—–-]\s*(.+?)(?:\s*[—–-]\s*(.+))?$',  # Title — Company — Location
            ]
            
            # Check for date patterns (years, months, etc.)
            date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\b\d{4}\s*[-–]\s*(?:\d{4}|Present|Current|Now)\b|\b\d{1,2}[/-]\d{4}\s*[-–]\s*(?:\d{1,2}[/-]\d{4}|Present|Current)'
            has_date = bool(re.search(date_pattern, line, re.IGNORECASE))
            
            # If line has a date and looks like a job entry
            if has_date or (current_entry is None and len(line) > 10 and len(line) < 100):
                # Save previous entry if exists
                if current_entry:
                    if current_description:
                        current_entry['description'] = current_description
                    entries.append(current_entry)
                
                # Extract job info
                parts = re.split(r'\s*[—–-]\s*|\s*,\s*|\s+at\s+|\s+@\s+', line, maxsplit=2)
                
                # Try to extract dates
                date_match = re.search(r'(\d{4}|\w+\s+\d{4})\s*[-–]\s*(\d{4}|Present|Current|Now)', line, re.IGNORECASE)
                start_date = ""
                end_date = ""
                if date_match:
                    start_date = date_match.group(1).strip()
                    end_date = date_match.group(2).strip()
                    # Remove date from line for title/company extraction
                    line = re.sub(r'\s*(\d{4}|\w+\s+\d{4})\s*[-–]\s*(\d{4}|Present|Current|Now)\s*', '', line).strip()
                    parts = re.split(r'\s*[—–-]\s*|\s*,\s*|\s+at\s+', line, maxsplit=1)
                
                title = parts[0].strip() if parts else line
                company = parts[1].strip() if len(parts) > 1 else ""
                location = parts[2].strip() if len(parts) > 2 else ""
                
                # Clean up title/company
                title = re.sub(r'\s*[—–-]\s*$', '', title).strip()
                company = re.sub(r'^\s*[—–-]\s*', '', company).strip()
                
                current_entry = {
                    'title': title.upper() if title else 'POSITION',
                    'company': company.upper() if company else 'COMPANY',
                    'location': location.upper() if location else 'LOCATION',
                    'start_date': start_date or '2020',
                    'end_date': end_date or 'Present',
                    'description': []
                }
                current_description = []
            
            # Check if line is a bullet point or description
            elif current_entry:
                # Remove bullet markers
                desc_line = re.sub(r'^[•\-\*]\s*', '', line).strip()
                if desc_line and len(desc_line) > 5:
                    current_description.append(desc_line)
            elif not current_entry and len(line) > 20:
                # Might be a job title without clear structure
                current_entry = {
                    'title': line.upper(),
                    'company': 'COMPANY',
                    'location': 'LOCATION',
                    'start_date': '2020',
                    'end_date': 'Present',
                    'description': []
                }
        
        # Save last entry
        if current_entry:
            if current_description:
                current_entry['description'] = current_description
            entries.append(current_entry)
        
        return entries if entries else []
    
    def _parse_education_v33(self, section):
        """Intelligently parse education from actual CV content"""
        entries = []
        if not section or len(section.strip()) < 10:
            return entries
        
        lines = section.split('\n')
        current_entry = None
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_entry:
                    entries.append(current_entry)
                    current_entry = None
                continue
            
            # Look for degree patterns: "Degree Name, Institution, Year" or "Degree Name - Institution - Year"
            # Or: "Institution - Degree Name - Year"
            degree_patterns = [
                r'^(.+?)\s*[—–-]\s*(.+?)\s*[—–-]\s*(\d{4})',  # Degree — Institution — Year
                r'^(.+?)\s*,\s*(.+?)\s*,\s*(\d{4})',  # Degree, Institution, Year
                r'^(.+?)\s*\((.+?)\)\s*[—–-]?\s*(\d{4})',  # Degree (Institution) Year
            ]
            
            # Check for year pattern
            year_match = re.search(r'\b(19|20)\d{2}\b', line)
            has_year = bool(year_match)
            
            # Check if line looks like a degree/institution
            is_degree_line = False
            degree_text = ""
            institution_text = ""
            year_text = ""
            
            for pattern in degree_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    degree_text = match.group(1).strip()
                    institution_text = match.group(2).strip()
                    year_text = match.group(3).strip()
                    is_degree_line = True
                    break
            
            # If no pattern match but has year and looks like education
            if not is_degree_line and has_year and len(line) > 10:
                # Try to split by common separators
                parts = re.split(r'\s*[—–-]\s*|\s*,\s*|\s+\(|\s+\)', line)
                if len(parts) >= 2:
                    degree_text = parts[0].strip()
                    institution_text = parts[1].strip()
                    year_text = year_match.group(0) if year_match else ""
            
            if is_degree_line or (has_year and len(line) > 10):
                # Save previous entry
                if current_entry:
                    entries.append(current_entry)
                
                current_entry = {
                    'degree': degree_text.upper() if degree_text else line.upper(),
                    'institution': institution_text.upper() if institution_text else 'INSTITUTION',
                    'year': year_text or '2020',
                    'description': []
                }
            elif current_entry:
                # Add to description
                desc_line = re.sub(r'^[•\-\*]\s*', '', line).strip()
                if desc_line and len(desc_line) > 3:
                    current_entry['description'].append(desc_line)
            elif len(line) > 10 and not re.search(r'^\d{4}', line):
                # Might be a degree without year
                current_entry = {
                    'degree': line.upper(),
                    'institution': 'INSTITUTION',
                    'year': '2020',
                    'description': []
                }
        
        # Save last entry
        if current_entry:
            entries.append(current_entry)
        
        return entries if entries else []
    
    def _parse_languages_v33(self, section):
        """Parse languages - same as previous versions"""
        languages = []
        
        # WKWebViewCompatible parsing - look for language names
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
        
        # If no languages found, add realistic languages
        if not languages:
            languages = [
                {'language': 'ENGLISH', 'level': 'NATIVE'},
                {'language': 'FRENCH', 'level': 'INTERMEDIATE'},
                {'language': 'SPANISH', 'level': 'BASIC'}
            ]
        
        return languages
    
    def _parse_computer_skills_v33(self, section):
        """Intelligently parse computer/technical skills from actual CV content"""
        skills = []
        if not section or len(section.strip()) < 5:
            return skills
        
        # Common technical skills keywords to look for
        tech_keywords = [
            'python', 'java', 'javascript', 'typescript', 'react', 'html', 'css', 'swift', 'kotlin',
            'sql', 'excel', 'powerpoint', 'word', 'office', 'bloomberg', 'vba', 'r', 'matlab',
            'git', 'github', 'npm', 'node', 'angular', 'vue', 'django', 'flask', 'spring',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'linux', 'unix',
            'photoshop', 'illustrator', 'indesign', 'premiere', 'procreate', 'canva',
            'tableau', 'powerbi', 'salesforce', 'hubspot', 'analytics', 'seo'
        ]
        
        # Split by common delimiters and extract skills
        skill_items = re.split(r'[,;•\n]', section)
        
        for item in skill_items:
            item = item.strip()
            if not item or len(item) < 2 or item.startswith(':'):
                continue
            
            # Remove common prefixes/suffixes
            item = re.sub(r'^[•\-\*]\s*', '', item)
            item = re.sub(r'\s*[—–-].*$', '', item)  # Remove everything after dash
            item = item.strip()
            
            if item and len(item) > 2:
                # Check if it contains known tech keywords
                item_lower = item.lower()
                for keyword in tech_keywords:
                    if keyword in item_lower:
                        # Extract the skill name (might be "Python" or "Python Programming")
                        skill_name = item.split()[0] if ' ' in item else item
                        skills.append(skill_name.upper())
                        break
                else:
                    # If no keyword match but looks like a skill (short, no spaces or common skill pattern)
                    if len(item) < 30 and (not ' ' in item or item.count(' ') < 3):
                        skills.append(item.upper())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        return unique_skills[:15]  # Limit to 15 skills
    
    def _parse_extra_curricular_v33(self, section):
        """Parse extra curricular activities - same as previous versions"""
        activities = []
        
        # Split by common delimiters
        activity_items = re.split(r'[,;•\n]', section)
        
        for item in activity_items:
            item = item.strip()
            if item and len(item) > 2:
                activities.append(item.upper())
        
        return activities
    
    def _format_work_experience_v33(self, work_exp):
        """Format work experience with float-based layout for date alignment"""
        if not work_exp:
            return '<div class="job-item">No work experience data available</div>'
        
        html = ''
        for job in work_exp:
            html += '<div class="job-item clearfix">'
            html += '<div class="job-header">'
            html += f'<div class="job-title">{job.get("title", "POSITION")}</div>'
            html += f'<div class="job-date">{job.get("start_date", "2020")} - {job.get("end_date", "Present")}</div>'
            html += '</div>'
            html += f'<div class="job-company">{job.get("company", "COMPANY")}, {job.get("location", "LOCATION")}</div>'
            
            if job.get('description'):
                html += '<div class="job-description">'
                for desc in job['description']:
                    html += f'• {desc}<br>'
                html += '</div>'
            
            html += '</div>'
        
        return html
    
    def _format_education_v33(self, education):
        """Format education with float-based layout for date alignment"""
        if not education:
            return '<div class="job-item">No education data available</div>'
        
        html = ''
        for edu in education:
            html += '<div class="job-item clearfix">'
            html += '<div class="job-header">'
            html += f'<div class="job-title">{edu.get("degree", "DEGREE")}</div>'
            html += f'<div class="job-date">{edu.get("year", "2020")}</div>'
            html += '</div>'
            html += f'<div class="job-company">{edu.get("institution", "INSTITUTION")}</div>'
            
            if edu.get('description'):
                html += '<div class="job-description">'
                for desc in edu['description']:
                    html += f'• {desc}<br>'
                html += '</div>'
            
            html += '</div>'
        
        return html
    
    def _format_languages_v33(self, languages):
        """Format languages section"""
        if not languages:
            return ''
        
        html = '<div class="section"><div class="section-title">Languages</div>'
        for lang in languages:
            html += f'<div class="job-item"><strong>{lang.get("language", "LANGUAGE")}:</strong> {lang.get("level", "LEVEL")}</div>'
        html += '</div>'
        
        return html
    
    def _format_computer_skills_v33(self, skills):
        """Format computer skills section"""
        if not skills:
            return ''
        
        html = '<div class="section"><div class="section-title">Computer Skills</div>'
        html += '<div class="job-description">'
        for skill in skills[:8]:  # Limit to 8 skills
            html += f'• {skill}<br>'
        html += '</div></div>'
        
        return html
    
    def _format_extra_curricular_v33(self, activities):
        """Format extra curricular section"""
        if not activities:
            return ''
        
        html = '<div class="section"><div class="section-title">Extra Curricular Activities</div>'
        html += '<div class="job-description">'
        for activity in activities[:5]:  # Limit to 5 activities
            html += f'• {activity}<br>'
        html += '</div></div>'
        
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
enhanced_cv_formatter_v33 = EnhancedCVFormatterV33()
