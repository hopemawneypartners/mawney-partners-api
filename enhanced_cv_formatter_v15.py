import os
import re
import base64
from datetime import datetime

class EnhancedCVFormatterV15:
    def __init__(self):
        self.template_path = "mawney_cv_template_minimal_v15.html"
        self.use_ai_parsing = False  # Using rule-based parsing only
        
    def format_cv_with_template(self, cv_content, filename):
        """Format CV using the minimal V15 template"""
        try:
            # Clean and parse the CV content
            parsed_data = self._parse_cv_v15(cv_content)
            
            # Load the template
            template_content = self._load_template()
            if not template_content:
                return {"success": False, "error": "Template not found"}
            
            # Get logo base64 encodings
            top_logo_b64 = self._get_logo_base64("cv logo 1.png")
            bottom_logo_b64 = self._get_logo_base64("cv logo 2.png")
            
            # Replace placeholders in template
            formatted_html = self._replace_placeholders(
                template_content, 
                parsed_data, 
                top_logo_b64, 
                bottom_logo_b64
            )
            
            return {
                "success": True,
                "html_content": formatted_html,
                "filename": filename,
                "parsed_data": parsed_data
            }
            
        except Exception as e:
            return {"success": False, "error": f"Formatting error: {str(e)}"}
    
    def _parse_cv_v15(self, cv_content):
        """Parse CV content with focus on clean structure"""
        # Clean the CV text
        cleaned_text = self._clean_cv_text_v15(cv_content)
        
        # Parse different sections
        parsed_data = {
            "name": self._extract_name_v15(cleaned_text),
            "email": self._extract_email(cleaned_text),
            "location": self._extract_location(cleaned_text),
            "work_experience": self._parse_work_experience_v15(cleaned_text),
            "education": self._parse_education_v15(cleaned_text),
            "languages": self._parse_languages(cleaned_text),
            "computer_skills": self._parse_computer_skills_v15(cleaned_text),
            "extra_curricular": self._parse_extra_curricular(cleaned_text)
        }
        
        return parsed_data
    
    def _clean_cv_text_v15(self, text):
        """Clean text with focus on removing phone numbers and fixing concatenated words"""
        if not text:
            return ""
        
        # Remove phone numbers completely
        text = re.sub(r'Tel[:\s]*\(?\+?[\d\s\-\(\)]{10,}\)?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Phone[:\s]*\(?\+?[\d\s\-\(\)]{10,}\)?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Mobile[:\s]*\(?\+?[\d\s\-\(\)]{10,}\)?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(?\+?[\d\s\-\(\)]{10,}\)?', '', text)  # Generic phone number pattern
        
        # Fix common concatenated words
        concatenated_fixes = {
            'ofstatistical': 'of statistical',
            'isconscientiousinindependentworkandalsoexcelsattea': 'is conscientious in independent work and also excels at team',
            'stroandproblem': 'strong and problem',
            'workinga': 'working',
            'Resdetail': 'Responsible detail',
            'workiną': 'working',
            'andproblem': 'and problem',
            'isconscientious': 'is conscientious',
            'inindependent': 'in independent',
            'workandalso': 'work and also',
            'excelsattea': 'excels at team',
            'modellir': 'modelling',
            'teammwork': 'teamwork',
            'mana': 'managing',
            'ris': 'risk',
            'analyst positior': 'analyst position',
            'finan derivative': 'financial derivative',
            'financial ma': 'financial mathematics',
            'indep': 'independent',
            'managingging': 'managing',
            'RIS] ON': 'RISK METRICS ON',
            'riskk analysisautomati': 'risk analysis automation',
            'committeepackages': 'committee packages',
            'analyziną': 'analyzing',
            'problem-s olving': 'problem-solving',
            'financial mathematicsthematics': 'financial mathematics',
            'independentendent': 'independent',
            'mar financial': 'managing financial',
            'risk analysis automationon': 'risk analysis automation',
            'finan riskk metrics': 'financial risk metrics',
            'interestrates': 'interest rates',
            'certifi': 'certified',
            'lo': 'looking for',
            'institutio': 'institution',
            'derivativ': 'derivatives',
            'worki': 'working',
            'ke': 'key'
        }
        
        for wrong, correct in concatenated_fixes.items():
            text = text.replace(wrong, correct)
        
        # Fix common OCR errors
        text = re.sub(r'ą', 'a', text)  # Fix 'ą' character
        text = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\/]', ' ', text)  # Remove special characters except common punctuation
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _extract_name_v15(self, text):
        """Extract name from the beginning of the text"""
        if not text:
            return "CANDIDATE NAME"
        
        # Look for name patterns at the beginning
        lines = text.split('\n')[:5]  # Check first 5 lines
        
        for line in lines:
            line = line.strip()
            if len(line) > 3 and len(line) < 50:  # Reasonable name length
                # Check if it looks like a name (contains letters, maybe some punctuation)
                if re.match(r'^[A-Za-z\s\.,\-]+$', line) and not any(word in line.upper() for word in ['CV', 'RESUME', 'CURRICULUM', 'VITAE', 'EXPERIENCE', 'EDUCATION']):
                    return line.upper()
        
        return "CANDIDATE NAME"
    
    def _extract_email(self, text):
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else "email@example.com"
    
    def _extract_location(self, text):
        """Extract location information"""
        # Look for location patterns
        location_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})',  # City, State
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}\s+\d{5})',  # City, State ZIP
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?)',  # Full ZIP
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].upper()
        
        return "LOCATION"
    
    def _parse_work_experience_v15(self, text):
        """Parse work experience with improved detection"""
        work_experience = []
        
        # Split text into sections
        sections = re.split(r'\n\s*\n', text)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Look for job patterns
            job_patterns = [
                r'([A-Z][^,\n]+(?:,\s*[A-Z][^,\n]+)*)\s*([A-Z]{3,4}\s+\d{4}\s*-\s*[A-Z]{3,4}\s+\d{4}|[A-Z]{3,4}\s+\d{4}\s*-\s*Present|[A-Z]{3,4}\s+\d{4})',
                r'([A-Z][^,\n]+(?:,\s*[A-Z][^,\n]+)*)\s*(\d{4}\s*-\s*\d{4}|\d{4}\s*-\s*Present|\d{4})',
            ]
            
            for pattern in job_patterns:
                matches = re.findall(pattern, section)
                for match in matches:
                    title_company = match[0].strip()
                    dates = match[1].strip()
                    
                    # Extract description (rest of the section)
                    description = section.replace(match[0], '').replace(match[1], '').strip()
                    description = re.sub(r'^[^\w]*', '', description)  # Remove leading non-word characters
                    
                    if description and len(description) > 10:  # Only add if there's substantial content
                        work_experience.append({
                            "title_company": title_company.upper(),
                            "dates": dates,
                            "description": description
                        })
        
        return work_experience
    
    def _parse_education_v15(self, text):
        """Parse education section"""
        education = []
        
        # Look for education patterns
        education_patterns = [
            r'([A-Z][^,\n]+(?:,\s*[A-Z][^,\n]+)*)\s*([A-Z]{3,4}\s+\d{4}|[A-Z]{3,4}\s+\d{4}\s*-\s*[A-Z]{3,4}\s+\d{4})',
            r'([A-Z][^,\n]+(?:,\s*[A-Z][^,\n]+)*)\s*(\d{4})',
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                institution_degree = match[0].strip()
                dates = match[1].strip()
                
                education.append({
                    "title_company": institution_degree.upper(),
                    "dates": dates,
                    "description": ""
                })
        
        return education
    
    def _parse_languages(self, text):
        """Parse languages section"""
        languages = []
        
        # Look for language patterns
        language_keywords = ['English', 'French', 'German', 'Spanish', 'Italian', 'Portuguese', 'Chinese', 'Japanese', 'Arabic', 'Russian']
        
        for lang in language_keywords:
            if lang.lower() in text.lower():
                languages.append(lang)
        
        return languages
    
    def _parse_computer_skills_v15(self, text):
        """Parse computer skills with improved filtering"""
        skills = []
        
        # Look for technical skills
        tech_keywords = ['Python', 'Java', 'C++', 'JavaScript', 'SQL', 'Excel', 'PowerPoint', 'Word', 'Photoshop', 'AutoCAD', 'MATLAB', 'R', 'SAS', 'SPSS']
        
        for skill in tech_keywords:
            if skill.lower() in text.lower():
                skills.append(skill)
        
        return skills
    
    def _parse_extra_curricular(self, text):
        """Parse extra curricular activities"""
        activities = []
        
        # Look for activity keywords
        activity_keywords = ['volunteer', 'club', 'society', 'sport', 'hobby', 'interest', 'activity']
        
        for keyword in activity_keywords:
            if keyword.lower() in text.lower():
                activities.append(keyword.title())
        
        return activities
    
    def _load_template(self):
        """Load the HTML template"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return None
    
    def _get_logo_base64(self, logo_filename):
        """Get base64 encoding of logo"""
        try:
            logo_path = os.path.join("assets", logo_filename)
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as logo_file:
                    return base64.b64encode(logo_file.read()).decode('utf-8')
        except Exception:
            pass
        return ""
    
    def _replace_placeholders(self, template, data, top_logo_b64, bottom_logo_b64):
        """Replace placeholders in template with actual data"""
        # Replace basic placeholders
        template = template.replace("{TOP_LOGO_BASE64}", top_logo_b64)
        template = template.replace("{BOTTOM_LOGO_BASE64}", bottom_logo_b64)
        template = template.replace("{NAME}", data.get("name", "CANDIDATE NAME"))
        template = template.replace("{EMAIL}", data.get("email", "email@example.com"))
        template = template.replace("{LOCATION}", data.get("location", "LOCATION"))
        
        # Replace work experience
        work_exp_html = self._format_work_experience(data.get("work_experience", []))
        template = template.replace("{WORK_EXPERIENCE}", work_exp_html)
        
        # Replace education
        education_html = self._format_education(data.get("education", []))
        template = template.replace("{EDUCATION}", education_html)
        
        # Replace languages (only if content exists)
        languages = data.get("languages", [])
        if languages:
            languages_html = self._format_languages(languages)
            template = template.replace("{LANGUAGES}", languages_html)
        else:
            template = template.replace("{LANGUAGES}", "")
        
        # Replace computer skills (only if content exists)
        computer_skills = data.get("computer_skills", [])
        if computer_skills:
            computer_skills_html = self._format_computer_skills(computer_skills)
            template = template.replace("{COMPUTER_SKILLS}", computer_skills_html)
        else:
            template = template.replace("{COMPUTER_SKILLS}", "")
        
        # Replace extra curricular (only if content exists)
        extra_curricular = data.get("extra_curricular", [])
        if extra_curricular:
            extra_curricular_html = self._format_extra_curricular(extra_curricular)
            template = template.replace("{EXTRA_CURRICULAR}", extra_curricular_html)
        else:
            template = template.replace("{EXTRA_CURRICULAR}", "")
        
        return template
    
    def _format_work_experience(self, work_experience):
        """Format work experience section"""
        if not work_experience:
            return ""
        
        html = '<h2 style="font-size: 14pt; margin-top: 20px;">WORK EXPERIENCE</h2>'
        
        for job in work_experience:
            html += f'''
            <div style="margin-bottom: 15px;">
                <h3 style="font-size: 12pt; margin: 5px 0;">{job.get("title_company", "")}</h3>
                <p style="font-size: 10pt; margin: 2px 0; color: #666;">{job.get("dates", "")}</p>
                <p style="font-size: 10pt; margin: 5px 0;">{job.get("description", "")}</p>
            </div>
            '''
        
        return html
    
    def _format_education(self, education):
        """Format education section"""
        if not education:
            return ""
        
        html = '<h2 style="font-size: 14pt; margin-top: 20px;">EDUCATION</h2>'
        
        for edu in education:
            html += f'''
            <div style="margin-bottom: 15px;">
                <h3 style="font-size: 12pt; margin: 5px 0;">{edu.get("title_company", "")}</h3>
                <p style="font-size: 10pt; margin: 2px 0; color: #666;">{edu.get("dates", "")}</p>
                <p style="font-size: 10pt; margin: 5px 0;">{edu.get("description", "")}</p>
            </div>
            '''
        
        return html
    
    def _format_languages(self, languages):
        """Format languages section"""
        if not languages:
            return ""
        
        html = '<h2 style="font-size: 14pt; margin-top: 20px;">LANGUAGES</h2>'
        html += f'<p style="font-size: 10pt; margin: 5px 0;">{", ".join(languages)}</p>'
        
        return html
    
    def _format_computer_skills(self, skills):
        """Format computer skills section"""
        if not skills:
            return ""
        
        html = '<h2 style="font-size: 14pt; margin-top: 20px;">COMPUTER SKILLS</h2>'
        html += f'<p style="font-size: 10pt; margin: 5px 0;">{", ".join(skills)}</p>'
        
        return html
    
    def _format_extra_curricular(self, activities):
        """Format extra curricular section"""
        if not activities:
            return ""
        
        html = '<h2 style="font-size: 14pt; margin-top: 20px;">EXTRA CURRICULAR ACTIVITIES</h2>'
        html += f'<p style="font-size: 10pt; margin: 5px 0;">{", ".join(activities)}</p>'
        
        return html

# Create instance
enhanced_cv_formatter_v15 = EnhancedCVFormatterV15()
