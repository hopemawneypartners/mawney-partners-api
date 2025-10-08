"""
CV Formatting Module for Mawney Partners
Handles CV parsing, analysis, and reformatting in company style
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CVFormatter:
    """Handles CV formatting and generation in Mawney Partners style"""
    
    def __init__(self):
        self.company_style = self._initialize_company_style()
        self.sections = self._initialize_sections()
        
    def _initialize_company_style(self) -> Dict[str, Any]:
        """Initialize Mawney Partners CV style template based on analysis of 43 examples"""
        return {
            "header": {
                "name_font_size": "24pt",
                "name_style": "bold",
                "title_font_size": "14pt", 
                "title_style": "italic",
                "contact_font_size": "11pt",
                "contact_style": "normal"
            },
            "sections": {
                "font_size": "11pt",
                "section_headers": "12pt bold",
                "spacing": "0.5em",
                "margin": "1em"
            },
            "colors": {
                "primary": "#2c3e50",  # Dark blue-gray
                "secondary": "#3498db", # Blue
                "accent": "#e74c3c",   # Red accent
                "text": "#2c3e50"      # Dark text
            },
            "layout": {
                "margins": "1 inch",
                "line_spacing": "1.15",
                "font_family": "Arial, sans-serif",
                "average_line_length": 62  # Based on analysis
            },
            "common_sections": [
                "EDUCATION",
                "PROFESSIONAL EXPERIENCE", 
                "WORK EXPERIENCE",
                "EXPERIENCE",
                "LANGUAGES",
                "INTERESTS",
                "ADDITIONAL INFORMATION",
                "OTHER"
            ]
        }
    
    def _initialize_sections(self) -> Dict[str, str]:
        """Initialize CV section templates in Mawney Partners style based on analysis"""
        return {
            "professional_summary": """
PROFESSIONAL SUMMARY
{content}

""",
            "core_competencies": """
CORE COMPETENCIES
{content}

""",
            "professional_experience": """
PROFESSIONAL EXPERIENCE

{content}

""",
            "work_experience": """
WORK EXPERIENCE

{content}

""",
            "education": """
EDUCATION

{content}

""",
            "languages": """
LANGUAGES

{content}

""",
            "interests": """
INTERESTS

{content}

""",
            "certifications": """
CERTIFICATIONS & LICENSES

{content}

""",
            "additional_information": """
ADDITIONAL INFORMATION

{content}

""",
            "other": """
OTHER

{content}

"""
        }
    
    def format_cv(self, cv_data: str, filename: str = "uploaded_cv") -> Dict[str, Any]:
        """
        Format CV in Mawney Partners style
        
        Args:
            cv_data: Extracted text from CV document
            filename: Original filename
            
        Returns:
            Dictionary containing formatted CV and metadata
        """
        try:
            logger.info(f"Formatting CV: {filename}")
            
            # Parse the CV content
            parsed_cv = self._parse_cv_content(cv_data)
            
            # Apply Mawney Partners formatting
            formatted_cv = self._apply_company_formatting(parsed_cv)
            
            # Generate HTML and plain text versions
            html_cv = self._generate_html_cv(formatted_cv)
            text_cv = self._generate_text_cv(formatted_cv)
            
            return {
                "success": True,
                "filename": filename,
                "formatted_cv": formatted_cv,
                "html_version": html_cv,
                "text_version": text_cv,
                "sections_found": list(parsed_cv.keys()),
                "formatting_applied": "Mawney Partners Style",
                "analysis": self._analyze_cv_quality(parsed_cv)
            }
            
        except Exception as e:
            logger.error(f"Error formatting CV {filename}: {str(e)}")
            return {
                "success": False,
                "filename": filename,
                "error": str(e),
                "formatted_cv": None
            }
    
    def _parse_cv_content(self, cv_text: str) -> Dict[str, Any]:
        """Parse CV content and extract structured information"""
        cv_text = cv_text.strip()
        
        # Initialize parsed structure
        parsed = {
            "personal_info": {},
            "professional_summary": "",
            "core_competencies": [],
            "professional_experience": [],
            "education": [],
            "certifications": [],
            "additional_info": []
        }
        
        # Extract personal information
        parsed["personal_info"] = self._extract_personal_info(cv_text)
        
        # Extract professional summary
        parsed["professional_summary"] = self._extract_professional_summary(cv_text)
        
        # Extract core competencies/skills
        parsed["core_competencies"] = self._extract_core_competencies(cv_text)
        
        # Extract professional experience (check both variations)
        parsed["professional_experience"] = self._extract_professional_experience(cv_text)
        parsed["work_experience"] = self._extract_work_experience(cv_text)
        
        # Extract education
        parsed["education"] = self._extract_education(cv_text)
        
        # Extract certifications
        parsed["certifications"] = self._extract_certifications(cv_text)
        
        # Extract additional information
        parsed["additional_info"] = self._extract_additional_info(cv_text)
        
        return parsed
    
    def _extract_personal_info(self, cv_text: str) -> Dict[str, str]:
        """Extract personal information from CV"""
        info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, cv_text)
        if emails:
            info["email"] = emails[0]
        
        # Extract phone number
        phone_patterns = [
            r'\+?[\d\s\-\(\)]{10,}',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
            r'\d{3}-\d{3}-\d{4}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, cv_text)
            if phones:
                info["phone"] = phones[0].strip()
                break
        
        # Extract LinkedIn (simple pattern)
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        linkedin_matches = re.findall(linkedin_pattern, cv_text.lower())
        if linkedin_matches:
            info["linkedin"] = f"https://www.{linkedin_matches[0]}"
        
        # Extract name (first line or after common headers)
        lines = cv_text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            if line and len(line) > 2 and len(line) < 50:
                # Skip common headers
                if not any(header in line.lower() for header in ['curriculum', 'vitae', 'resume', 'cv', 'email', 'phone', 'address']):
                    info["name"] = line
                    break
        
        return info
    
    def _extract_professional_summary(self, cv_text: str) -> str:
        """Extract professional summary section"""
        summary_keywords = [
            'professional summary', 'summary', 'profile', 'objective', 
            'career objective', 'executive summary', 'about'
        ]
        
        # Look for summary sections
        for keyword in summary_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?=\n\n|\n[A-Z][A-Z\s]+\n|$)'
            match = re.search(pattern, cv_text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                if len(summary) > 20:  # Ensure it's substantial
                    return summary[:500]  # Limit length
        
        # If no explicit summary, try to extract first substantial paragraph
        paragraphs = cv_text.split('\n\n')
        for para in paragraphs[:3]:
            para = para.strip()
            if len(para) > 50 and len(para) < 300:
                # Check if it looks like a summary (not a header or list)
                if not para.isupper() and not para.startswith(('•', '-', '*', '1.', '2.')):
                    return para[:500]
        
        return ""
    
    def _extract_core_competencies(self, cv_text: str) -> List[str]:
        """Extract core competencies/skills"""
        skills_keywords = [
            'skills', 'competencies', 'core competencies', 'technical skills',
            'key skills', 'expertise', 'capabilities'
        ]
        
        skills = []
        
        for keyword in skills_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?=\n\n|\n[A-Z][A-Z\s]+\n|$)'
            match = re.search(pattern, cv_text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                # Extract skills from various formats
                skills.extend(self._parse_skills_content(content))
                break
        
        # If no explicit skills section, extract from throughout document
        if not skills:
            skills = self._extract_skills_from_text(cv_text)
        
        return list(set(skills))[:15]  # Remove duplicates, limit to 15
    
    def _extract_professional_experience(self, cv_text: str) -> List[Dict[str, str]]:
        """Extract professional experience"""
        experience_keywords = [
            'experience', 'work experience', 'professional experience',
            'employment', 'career history', 'work history'
        ]
        
        experiences = []
        
        for keyword in experience_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?=\n\n[A-Z][A-Z\s]+\n|$)'
            match = re.search(pattern, cv_text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                experiences = self._parse_experience_content(content)
                break
        
        # If no explicit experience section, try to extract from full text
        if not experiences:
            experiences = self._extract_experience_from_text(cv_text)
        
        return experiences[:10]  # Limit to 10 most recent
    
    def _extract_work_experience(self, cv_text: str) -> List[Dict[str, str]]:
        """Extract work experience (alternative to professional experience)"""
        experience_keywords = ['work experience', 'work history', 'employment history']
        
        experiences = []
        
        for keyword in experience_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?=\n\n[A-Z][A-Z\s]+\n|$)'
            match = re.search(pattern, cv_text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                experiences = self._parse_experience_content(content)
                break
        
        # If no explicit work experience section, try to extract from full text
        if not experiences:
            experiences = self._extract_experience_from_text(cv_text)
        
        return experiences[:10]  # Limit to 10 most recent
    
    def _extract_education(self, cv_text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education_keywords = ['education', 'academic', 'qualifications', 'degrees']
        
        education = []
        
        for keyword in education_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?=\n\n[A-Z][A-Z\s]+\n|$)'
            match = re.search(pattern, cv_text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                education = self._parse_education_content(content)
                break
        
        return education[:5]  # Limit to 5 entries
    
    def _extract_certifications(self, cv_text: str) -> List[str]:
        """Extract certifications and licenses"""
        cert_keywords = [
            'certifications', 'certificates', 'licenses', 'licences',
            'professional certifications', 'credentials'
        ]
        
        certifications = []
        
        for keyword in cert_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?=\n\n[A-Z][A-Z\s]+\n|$)'
            match = re.search(pattern, cv_text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                certifications = self._parse_certifications_content(content)
                break
        
        return certifications[:10]  # Limit to 10
    
    def _extract_additional_info(self, cv_text: str) -> List[str]:
        """Extract additional information"""
        additional_keywords = [
            'additional', 'other', 'miscellaneous', 'interests',
            'languages', 'volunteer', 'awards', 'publications'
        ]
        
        additional = []
        
        for keyword in additional_keywords:
            pattern = rf'{keyword}[:\s]*(.*?)(?=\n\n[A-Z][A-Z\s]+\n|$)'
            match = re.search(pattern, cv_text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                additional.extend(self._parse_additional_content(content))
                break
        
        return additional[:10]  # Limit to 10
    
    def _parse_skills_content(self, content: str) -> List[str]:
        """Parse skills from content"""
        skills = []
        
        # Handle bullet points
        bullet_pattern = r'[•\-\*]\s*([^\n]+)'
        bullets = re.findall(bullet_pattern, content)
        skills.extend([skill.strip() for skill in bullets])
        
        # Handle comma-separated
        if ',' in content and len(skills) == 0:
            skills.extend([skill.strip() for skill in content.split(',')])
        
        # Handle line-separated
        if '\n' in content and len(skills) == 0:
            lines = content.split('\n')
            skills.extend([line.strip() for line in lines if line.strip()])
        
        return [skill for skill in skills if len(skill) > 2 and len(skill) < 50]
    
    def _extract_skills_from_text(self, cv_text: str) -> List[str]:
        """Extract skills from throughout the document"""
        # Common financial/credit skills
        financial_skills = [
            'credit analysis', 'risk assessment', 'financial modeling', 'portfolio management',
            'debt restructuring', 'corporate finance', 'investment banking', 'private credit',
            'leveraged finance', 'distressed debt', 'CLO', 'credit spreads', 'duration analysis',
            'Excel', 'Bloomberg', 'VBA', 'Python', 'SQL', 'PowerBI', 'Tableau'
        ]
        
        found_skills = []
        for skill in financial_skills:
            if skill.lower() in cv_text.lower():
                found_skills.append(skill)
        
        return found_skills
    
    def _parse_experience_content(self, content: str) -> List[Dict[str, str]]:
        """Parse experience from content"""
        experiences = []
        
        # Split by common separators
        sections = re.split(r'\n\s*\n', content)
        
        for section in sections:
            section = section.strip()
            if len(section) > 20:
                exp = self._parse_single_experience(section)
                if exp:
                    experiences.append(exp)
        
        return experiences
    
    def _parse_single_experience(self, section: str) -> Optional[Dict[str, str]]:
        """Parse a single experience entry"""
        lines = section.split('\n')
        if len(lines) < 2:
            return None
        
        # Extract company and title (usually first line)
        first_line = lines[0].strip()
        
        # Try to extract dates
        date_pattern = r'\b(19|20)\d{2}\b|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(19|20)\d{2}\b'
        dates = re.findall(date_pattern, first_line + ' ' + lines[1] if len(lines) > 1 else first_line)
        
        return {
            "title": first_line,
            "company": first_line,  # Will be refined
            "dates": dates[0] if dates else "",
            "description": '\n'.join(lines[1:])[:500] if len(lines) > 1 else ""
        }
    
    def _extract_experience_from_text(self, cv_text: str) -> List[Dict[str, str]]:
        """Extract experience from full text"""
        # This is a simplified version - could be enhanced with NLP
        experiences = []
        
        # Look for common job title patterns
        title_patterns = [
            r'(Senior|Principal|VP|Vice President|Director|Manager|Analyst|Associate)\s+[A-Za-z\s]+',
            r'[A-Za-z]+\s+(Analyst|Manager|Director|Associate|VP)'
        ]
        
        for pattern in title_patterns:
            matches = re.finditer(pattern, cv_text, re.IGNORECASE)
            for match in matches:
                title = match.group(0).strip()
                if len(title) > 5 and len(title) < 100:
                    experiences.append({
                        "title": title,
                        "company": "Company Name",  # Placeholder
                        "dates": "",
                        "description": ""
                    })
        
        return experiences[:5]
    
    def _parse_education_content(self, content: str) -> List[Dict[str, str]]:
        """Parse education from content"""
        education = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 10:
                education.append({
                    "degree": line,
                    "institution": "",
                    "year": ""
                })
        
        return education
    
    def _parse_certifications_content(self, content: str) -> List[str]:
        """Parse certifications from content"""
        certs = []
        
        # Handle bullet points
        bullet_pattern = r'[•\-\*]\s*([^\n]+)'
        bullets = re.findall(bullet_pattern, content)
        certs.extend([cert.strip() for cert in bullets])
        
        # Handle line-separated
        if len(certs) == 0:
            lines = content.split('\n')
            certs.extend([line.strip() for line in lines if line.strip()])
        
        return [cert for cert in certs if len(cert) > 3]
    
    def _parse_additional_content(self, content: str) -> List[str]:
        """Parse additional information from content"""
        items = []
        
        # Handle bullet points
        bullet_pattern = r'[•\-\*]\s*([^\n]+)'
        bullets = re.findall(bullet_pattern, content)
        items.extend([item.strip() for item in bullets])
        
        # Handle line-separated
        if len(items) == 0:
            lines = content.split('\n')
            items.extend([line.strip() for line in lines if line.strip()])
        
        return items
    
    def _apply_company_formatting(self, parsed_cv: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Mawney Partners formatting to parsed CV"""
        formatted = {
            "header": self._format_header(parsed_cv.get("personal_info", {})),
            "professional_summary": self._format_professional_summary(parsed_cv.get("professional_summary", "")),
            "core_competencies": self._format_core_competencies(parsed_cv.get("core_competencies", [])),
            "professional_experience": self._format_professional_experience(parsed_cv.get("professional_experience", [])),
            "work_experience": self._format_work_experience(parsed_cv.get("work_experience", [])),
            "education": self._format_education(parsed_cv.get("education", [])),
            "languages": self._format_languages(parsed_cv.get("languages", [])),
            "interests": self._format_interests(parsed_cv.get("interests", [])),
            "certifications": self._format_certifications(parsed_cv.get("certifications", [])),
            "additional_info": self._format_additional_info(parsed_cv.get("additional_info", [])),
            "other": self._format_other(parsed_cv.get("other", []))
        }
        
        return formatted
    
    def _format_header(self, personal_info: Dict[str, str]) -> str:
        """Format CV header in Mawney Partners style"""
        name = personal_info.get("name", "Your Name")
        email = personal_info.get("email", "")
        phone = personal_info.get("phone", "")
        linkedin = personal_info.get("linkedin", "")
        
        header = f"{name.upper()}\n"
        
        contact_info = []
        if email:
            contact_info.append(email)
        if phone:
            contact_info.append(phone)
        if linkedin:
            contact_info.append(linkedin)
        
        if contact_info:
            header += " | ".join(contact_info) + "\n"
        
        return header + "\n"
    
    def _format_professional_summary(self, summary: str) -> str:
        """Format professional summary"""
        if not summary:
            return ""
        
        return self.sections["professional_summary"].format(content=summary.strip())
    
    def _format_core_competencies(self, competencies: List[str]) -> str:
        """Format core competencies"""
        if not competencies:
            return ""
        
        # Group competencies logically
        formatted_skills = " • ".join(competencies[:10])
        return self.sections["core_competencies"].format(content=formatted_skills)
    
    def _format_professional_experience(self, experiences: List[Dict[str, str]]) -> str:
        """Format professional experience"""
        if not experiences:
            return ""
        
        formatted_experiences = []
        for exp in experiences:
            exp_text = f"{exp.get('title', '')}"
            if exp.get('dates'):
                exp_text += f" | {exp['dates']}"
            if exp.get('description'):
                exp_text += f"\n{exp['description']}"
            formatted_experiences.append(exp_text)
        
        return self.sections["professional_experience"].format(content="\n\n".join(formatted_experiences))
    
    def _format_education(self, education: List[Dict[str, str]]) -> str:
        """Format education"""
        if not education:
            return ""
        
        formatted_education = []
        for edu in education:
            formatted_education.append(edu.get("degree", ""))
        
        return self.sections["education"].format(content="\n".join(formatted_education))
    
    def _format_certifications(self, certifications: List[str]) -> str:
        """Format certifications"""
        if not certifications:
            return ""
        
        formatted_certs = " • ".join(certifications)
        return self.sections["certifications"].format(content=formatted_certs)
    
    def _format_additional_info(self, additional: List[str]) -> str:
        """Format additional information"""
        if not additional:
            return ""
        
        formatted_info = " • ".join(additional)
        return self.sections["additional_information"].format(content=formatted_info)
    
    def _format_work_experience(self, experiences: List[Dict[str, str]]) -> str:
        """Format work experience"""
        if not experiences:
            return ""
        
        formatted_experiences = []
        for exp in experiences:
            exp_text = f"{exp.get('title', '')}"
            if exp.get('dates'):
                exp_text += f" | {exp['dates']}"
            if exp.get('description'):
                exp_text += f"\n{exp['description']}"
            formatted_experiences.append(exp_text)
        
        return self.sections["work_experience"].format(content="\n\n".join(formatted_experiences))
    
    def _format_languages(self, languages: List[str]) -> str:
        """Format languages"""
        if not languages:
            return ""
        
        formatted_languages = " • ".join(languages)
        return self.sections["languages"].format(content=formatted_languages)
    
    def _format_interests(self, interests: List[str]) -> str:
        """Format interests"""
        if not interests:
            return ""
        
        formatted_interests = " • ".join(interests)
        return self.sections["interests"].format(content=formatted_interests)
    
    def _format_other(self, other: List[str]) -> str:
        """Format other information"""
        if not other:
            return ""
        
        formatted_other = " • ".join(other)
        return self.sections["other"].format(content=formatted_other)
    
    def _generate_html_cv(self, formatted_cv: Dict[str, Any]) -> str:
        """Generate HTML version of formatted CV"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CV - Mawney Partners Style</title>
    <style>
        body {{
            font-family: {self.company_style['layout']['font_family']};
            color: {self.company_style['colors']['text']};
            line-height: {self.company_style['layout']['line_spacing']};
            margin: {self.company_style['layout']['margins']};
        }}
        .header {{
            text-align: center;
            margin-bottom: 2em;
        }}
        .name {{
            font-size: {self.company_style['header']['name_font_size']};
            font-weight: bold;
            color: {self.company_style['colors']['primary']};
            margin-bottom: 0.5em;
        }}
        .contact {{
            font-size: {self.company_style['header']['contact_font_size']};
        }}
        .section {{
            margin-bottom: 1.5em;
        }}
        .section-header {{
            font-size: {self.company_style['sections']['section_headers']};
            color: {self.company_style['colors']['primary']};
            border-bottom: 2px solid {self.company_style['colors']['secondary']};
            margin-bottom: 0.5em;
            padding-bottom: 0.2em;
        }}
        .content {{
            font-size: {self.company_style['sections']['font_size']};
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="name">{formatted_cv['header'].split(chr(10))[0]}</div>
        <div class="contact">{' | '.join(formatted_cv['header'].split(chr(10))[1:]) if len(formatted_cv['header'].split(chr(10))) > 1 else ''}</div>
    </div>
"""
        
        # Add sections
        sections = [
            ('professional_summary', 'Professional Summary'),
            ('core_competencies', 'Core Competencies'),
            ('professional_experience', 'Professional Experience'),
            ('work_experience', 'Work Experience'),
            ('education', 'Education'),
            ('languages', 'Languages'),
            ('interests', 'Interests'),
            ('certifications', 'Certifications'),
            ('additional_info', 'Additional Information'),
            ('other', 'Other')
        ]
        
        for section_key, section_title in sections:
            if formatted_cv.get(section_key):
                html += f"""
    <div class="section">
        <div class="section-header">{section_title}</div>
        <div class="content">{formatted_cv[section_key].replace(chr(10), '<br>')}</div>
    </div>
"""
        
        html += "</body></html>"
        return html
    
    def _generate_text_cv(self, formatted_cv: Dict[str, Any]) -> str:
        """Generate plain text version of formatted CV"""
        text_cv = ""
        
        # Add header
        text_cv += formatted_cv.get('header', '')
        
        # Add sections
        sections = [
            'professional_summary',
            'core_competencies', 
            'professional_experience',
            'work_experience',
            'education',
            'languages',
            'interests',
            'certifications',
            'additional_info',
            'other'
        ]
        
        for section in sections:
            if formatted_cv.get(section):
                text_cv += formatted_cv[section]
        
        return text_cv.strip()
    
    def _analyze_cv_quality(self, parsed_cv: Dict[str, Any]) -> str:
        """Analyze CV quality and provide feedback"""
        analysis_parts = []
        
        # Check completeness
        if parsed_cv.get("personal_info", {}).get("name"):
            analysis_parts.append("✓ Name identified")
        else:
            analysis_parts.append("⚠ Name not clearly identified")
        
        if parsed_cv.get("professional_summary"):
            analysis_parts.append("✓ Professional summary found")
        else:
            analysis_parts.append("⚠ Professional summary missing")
        
        if parsed_cv.get("professional_experience"):
            exp_count = len(parsed_cv["professional_experience"])
            analysis_parts.append(f"✓ {exp_count} professional experience entries found")
        else:
            analysis_parts.append("⚠ Professional experience not clearly structured")
        
        if parsed_cv.get("education"):
            analysis_parts.append("✓ Education information found")
        else:
            analysis_parts.append("⚠ Education information missing")
        
        # Check for financial/credit industry relevance
        all_text = " ".join([
            parsed_cv.get("professional_summary", ""),
            " ".join(parsed_cv.get("core_competencies", [])),
            " ".join([exp.get("description", "") for exp in parsed_cv.get("professional_experience", [])])
        ]).lower()
        
        financial_keywords = [
            "credit", "finance", "banking", "investment", "risk", "portfolio",
            "corporate", "debt", "equity", "analysis", "modeling"
        ]
        
        found_keywords = [keyword for keyword in financial_keywords if keyword in all_text]
        if found_keywords:
            analysis_parts.append(f"✓ Financial industry relevance detected: {', '.join(found_keywords[:5])}")
        
        return " | ".join(analysis_parts)

# Global instance
cv_formatter = CVFormatter()
