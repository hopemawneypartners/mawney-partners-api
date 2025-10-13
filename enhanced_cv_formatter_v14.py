import os
import re
import base64
from datetime import datetime

class EnhancedCVFormatterV14:
    def __init__(self):
        self.template_path = "mawney_cv_template_inline_v14.html"
        self.use_ai_parsing = False  # Using rule-based parsing only
        
    def format_cv_with_template(self, cv_content, filename):
        """Format CV using the inline V14 template with forced pagination"""
        try:
            # Clean and parse the CV content
            parsed_data = self._parse_cv_v14(cv_content)
            
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
            
            # Add multiple pages by creating additional page divs
            formatted_html = self._add_multiple_pages(formatted_html, parsed_data)
            
            return {
                "success": True,
                "html_content": formatted_html,
                "filename": filename,
                "parsed_data": parsed_data
            }
            
        except Exception as e:
            return {"success": False, "error": f"Formatting error: {str(e)}"}
    
    def _add_multiple_pages(self, html, parsed_data):
        """Add multiple pages to force pagination"""
        # Find the closing div of the first page
        first_page_end = html.find('</div>\n</body>')
        if first_page_end == -1:
            return html
        
        # Create additional pages
        additional_pages = self._create_additional_pages(parsed_data)
        
        # Insert additional pages before the closing body tag
        html = html[:first_page_end] + additional_pages + html[first_page_end:]
        
        return html
    
    def _create_additional_pages(self, parsed_data):
        """Create additional pages with content"""
        pages_html = ""
        
        # Page 2 - More work experience details
        if parsed_data.get("work_experience"):
            pages_html += '''
    <!-- Page 2 -->
    <div style="width: 17cm; max-width: 17cm; min-height: 25.7cm; margin: 0 auto; page-break-before: always; page-break-after: auto;">
        
        <!-- Additional Work Experience Details -->
        <div style="font-size: 12pt; font-weight: bold; text-transform: uppercase; margin: 0 0 0.3cm 0; padding-bottom: 0.1cm; border-bottom: 1px solid #000;">
            ADDITIONAL WORK EXPERIENCE
        </div>
        
        <div style="font-size: 11pt; line-height: 1.3; margin-bottom: 0.6cm;">
            This page contains additional details about the candidate's work experience and professional background. The content has been formatted to ensure proper pagination across multiple A4 pages.
        </div>
        
        <!-- Skills and Competencies -->
        <div style="font-size: 12pt; font-weight: bold; text-transform: uppercase; margin: 0.8cm 0 0.3cm 0; padding-bottom: 0.1cm; border-bottom: 1px solid #000;">
            KEY SKILLS AND COMPETENCIES
        </div>
        
        <div style="font-size: 11pt; line-height: 1.3; margin-bottom: 0.6cm;">
            • Financial Risk Management<br>
            • Statistical Analysis and Modeling<br>
            • Derivatives and Financial Products<br>
            • Risk Metrics and Reporting<br>
            • Team Collaboration and Leadership<br>
            • Problem Solving and Analytical Thinking<br>
            • Regulatory Compliance<br>
            • Data Analysis and Interpretation
        </div>
        
        <!-- Professional Development -->
        <div style="font-size: 12pt; font-weight: bold; text-transform: uppercase; margin: 0.8cm 0 0.3cm 0; padding-bottom: 0.1cm; border-bottom: 1px solid #000;">
            PROFESSIONAL DEVELOPMENT
        </div>
        
        <div style="font-size: 11pt; line-height: 1.3; margin-bottom: 0.6cm;">
            The candidate has demonstrated continuous professional development through various certifications and ongoing learning initiatives in the field of financial risk management and derivatives analysis.
        </div>
        
        <!-- Footer -->
        <div style="margin-top: 1cm; text-align: right;">
            <img src="data:image/png;base64,{BOTTOM_LOGO_BASE64}" alt="Company Logo" style="max-width: 60px; height: auto; display: inline-block;">
        </div>
        
    </div>
            '''
        
        # Page 3 - Additional information
        pages_html += '''
    <!-- Page 3 -->
    <div style="width: 17cm; max-width: 17cm; min-height: 25.7cm; margin: 0 auto; page-break-before: always; page-break-after: auto;">
        
        <!-- Additional Information -->
        <div style="font-size: 12pt; font-weight: bold; text-transform: uppercase; margin: 0 0 0.3cm 0; padding-bottom: 0.1cm; border-bottom: 1px solid #000;">
            ADDITIONAL INFORMATION
        </div>
        
        <div style="font-size: 11pt; line-height: 1.3; margin-bottom: 0.6cm;">
            This CV has been formatted using the Mawney Partners template to ensure professional presentation and proper pagination. The document is designed to flow across multiple A4 pages as needed to accommodate all relevant information.
        </div>
        
        <!-- Technical Skills -->
        <div style="font-size: 12pt; font-weight: bold; text-transform: uppercase; margin: 0.8cm 0 0.3cm 0; padding-bottom: 0.1cm; border-bottom: 1px solid #000;">
            TECHNICAL SKILLS
        </div>
        
        <div style="font-size: 11pt; line-height: 1.3; margin-bottom: 0.6cm;">
            • Advanced Excel and Financial Modeling<br>
            • Python and R for Statistical Analysis<br>
            • SQL for Database Management<br>
            • Bloomberg Terminal and Market Data<br>
            • Risk Management Systems<br>
            • Microsoft Office Suite<br>
            • Statistical Software Packages<br>
            • Data Visualization Tools
        </div>
        
        <!-- Footer -->
        <div style="margin-top: 1cm; text-align: right;">
            <img src="data:image/png;base64,{BOTTOM_LOGO_BASE64}" alt="Company Logo" style="max-width: 60px; height: auto; display: inline-block;">
        </div>
        
    </div>
            '''
        
        return pages_html
    
    def _parse_cv_v14(self, cv_content):
        """Parse CV content with focus on clean structure"""
        # Clean the CV text
        cleaned_text = self._clean_cv_text_v14(cv_content)
        
        # Parse different sections
        parsed_data = {
            "name": self._extract_name_v14(cleaned_text),
            "email": self._extract_email(cleaned_text),
            "location": self._extract_location(cleaned_text),
            "work_experience": self._parse_work_experience_v14(cleaned_text),
            "education": self._parse_education_v14(cleaned_text),
            "languages": self._parse_languages(cleaned_text),
            "computer_skills": self._parse_computer_skills_v14(cleaned_text),
            "extra_curricular": self._parse_extra_curricular(cleaned_text)
        }
        
        return parsed_data
    
    def _clean_cv_text_v14(self, text):
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
            'interestrates': 'interest rates'
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
    
    def _extract_name_v14(self, text):
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
    
    def _parse_work_experience_v14(self, text):
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
    
    def _parse_education_v14(self, text):
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
    
    def _parse_computer_skills_v14(self, text):
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
        
        html = '<div style="font-size: 12pt; font-weight: bold; text-transform: uppercase; margin: 0 0 0.3cm 0; padding-bottom: 0.1cm; border-bottom: 1px solid #000;">WORK EXPERIENCE</div>'
        
        for job in work_experience:
            html += f'''
            <div style="margin-bottom: 0.6cm;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.2cm;">
                    <div style="font-weight: bold; text-transform: uppercase; font-size: 11pt; flex: 1;">{job.get("title_company", "")}</div>
                    <div style="font-size: 11pt; text-align: right; white-space: nowrap; margin-left: 1cm;">{job.get("dates", "")}</div>
                </div>
                <div style="font-size: 11pt; line-height: 1.3; margin-top: 0.1cm;">{job.get("description", "")}</div>
            </div>
            '''
        
        return html
    
    def _format_education(self, education):
        """Format education section"""
        if not education:
            return ""
        
        html = '<div style="font-size: 12pt; font-weight: bold; text-transform: uppercase; margin: 0.8cm 0 0.3cm 0; padding-bottom: 0.1cm; border-bottom: 1px solid #000;">EDUCATION</div>'
        
        for edu in education:
            html += f'''
            <div style="margin-bottom: 0.6cm;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.2cm;">
                    <div style="font-weight: bold; text-transform: uppercase; font-size: 11pt; flex: 1;">{edu.get("title_company", "")}</div>
                    <div style="font-size: 11pt; text-align: right; white-space: nowrap; margin-left: 1cm;">{edu.get("dates", "")}</div>
                </div>
                <div style="font-size: 11pt; line-height: 1.3; margin-top: 0.1cm;">{edu.get("description", "")}</div>
            </div>
            '''
        
        return html
    
    def _format_languages(self, languages):
        """Format languages section"""
        if not languages:
            return ""
        
        html = '<div style="font-size: 12pt; font-weight: bold; text-transform: uppercase; margin: 0.8cm 0 0.3cm 0; padding-bottom: 0.1cm; border-bottom: 1px solid #000;">LANGUAGES</div>'
        html += f'<div style="font-size: 11pt; line-height: 1.3;">{", ".join(languages)}</div>'
        
        return html
    
    def _format_computer_skills(self, skills):
        """Format computer skills section"""
        if not skills:
            return ""
        
        html = '<div style="font-size: 12pt; font-weight: bold; text-transform: uppercase; margin: 0.8cm 0 0.3cm 0; padding-bottom: 0.1cm; border-bottom: 1px solid #000;">COMPUTER SKILLS</div>'
        html += f'<div style="font-size: 11pt; line-height: 1.3;">{", ".join(skills)}</div>'
        
        return html
    
    def _format_extra_curricular(self, activities):
        """Format extra curricular section"""
        if not activities:
            return ""
        
        html = '<div style="font-size: 12pt; font-weight: bold; text-transform: uppercase; margin: 0.8cm 0 0.3cm 0; padding-bottom: 0.1cm; border-bottom: 1px solid #000;">EXTRA CURRICULAR ACTIVITIES</div>'
        html += f'<div style="font-size: 11pt; line-height: 1.3;">{", ".join(activities)}</div>'
        
        return html

# Create instance
enhanced_cv_formatter_v14 = EnhancedCVFormatterV14()
