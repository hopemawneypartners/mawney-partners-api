"""
Job Advert Analyzer for Mawney Partners
Analyzes job advert examples to extract company-specific style and patterns
"""

import os
import re
import json
import logging
from typing import Dict, List, Any
from collections import Counter
import PyPDF2
import pdfplumber

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobAdvertAnalyzer:
    """Analyzes job advert examples to extract Mawney Partners style patterns"""
    
    def __init__(self, examples_folder: str = "example-job-adverts"):
        self.examples_folder = examples_folder
    
    def analyze_all_job_adverts(self) -> Dict[str, Any]:
        """Analyze all job advert examples and extract style patterns"""
        logger.info("Starting job advert style analysis...")
        
        job_files = self._get_job_advert_files()
        logger.info(f"Found {len(job_files)} job advert files to analyze")
        
        all_extracted_data = []
        
        for i, job_file in enumerate(job_files, 1):
            logger.info(f"Processing job advert {i}/{len(job_files)}: {job_file}")
            try:
                extracted_data = self._analyze_single_job_advert(job_file)
                if extracted_data:
                    all_extracted_data.append(extracted_data)
            except Exception as e:
                logger.error(f"Error processing {job_file}: {e}")
        
        logger.info(f"Successfully analyzed {len(all_extracted_data)} job adverts")
        
        # Build style profile
        style_profile = self._build_style_profile(all_extracted_data)
        
        return {
            "total_adverts_analyzed": len(all_extracted_data),
            "style_profile": style_profile,
            "raw_data": all_extracted_data,
            "recommendations": self._generate_recommendations(style_profile)
        }
    
    def _get_job_advert_files(self) -> List[str]:
        """Get list of job advert files to analyze"""
        if not os.path.exists(self.examples_folder):
            logger.error(f"Examples folder not found: {self.examples_folder}")
            return []
        
        job_files = []
        for filename in sorted(os.listdir(self.examples_folder)):
            # Skip temp files
            if filename.startswith('~$'):
                continue
            if filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
                job_files.append(os.path.join(self.examples_folder, filename))
        
        return job_files
    
    def _analyze_single_job_advert(self, job_path: str) -> Dict[str, Any]:
        """Analyze a single job advert file"""
        try:
            # Extract text from file
            job_text = self._extract_text_from_file(job_path)
            
            if not job_text:
                logger.warning(f"No text extracted from {job_path}")
                return None
            
            # Extract style information
            filename = os.path.basename(job_path)
            style_info = self._extract_job_advert_style(job_text, filename)
            
            return {
                "filename": filename,
                "extracted_text": job_text,
                "style_info": style_info
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {job_path}: {e}")
            return None
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF or other file"""
        try:
            # Try pdfplumber first
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if text.strip():
                    return text
        except Exception as e:
            logger.warning(f"pdfplumber failed for {file_path}: {e}")
        
        try:
            # Fallback to PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            logger.error(f"PyPDF2 failed for {file_path}: {e}")
            return ""
    
    def _extract_job_advert_style(self, job_text: str, filename: str) -> Dict[str, Any]:
        """Extract style information from job advert text"""
        style_info = {
            "opening_line": self._extract_opening_line(job_text),
            "role_title": self._extract_role_title(job_text),
            "company_description": self._extract_company_description(job_text),
            "responsibilities": self._extract_responsibilities(job_text),
            "requirements": self._extract_requirements(job_text),
            "closing_statement": self._extract_closing_statement(job_text),
            "key_phrases": self._extract_key_phrases(job_text),
            "structure": self._analyze_structure(job_text)
        }
        
        return style_info
    
    def _extract_opening_line(self, text: str) -> str:
        """Extract the opening line/hook"""
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 30 and ('our client' in line.lower() or 'we are' in line.lower() or 'seeking' in line.lower()):
                return line[:200]
        return ""
    
    def _extract_role_title(self, text: str) -> str:
        """Extract role title"""
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if any(word in line.lower() for word in ['analyst', 'director', 'manager', 'officer', 'associate', 'vp', 'vice president']):
                return line
        return ""
    
    def _extract_company_description(self, text: str) -> List[str]:
        """Extract company description phrases"""
        descriptions = []
        patterns = [
            r'(top-performing|leading|established|ambitious|growing|impressive|highly regarded)',
            r'(credit fund|investment fund|hedge fund|investment manager|trading desk)',
            r'(strong performance|stellar performance|excellent year|impressive returns)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            descriptions.extend(matches)
        
        return list(set(descriptions))[:10]
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract responsibility bullet points"""
        responsibilities = []
        
        # Look for bullet points or numbered lists
        bullet_pattern = r'[•\-\*]\s*([^\n]+)'
        bullets = re.findall(bullet_pattern, text)
        
        for bullet in bullets:
            if len(bullet) > 20 and any(word in bullet.lower() for word in ['analysis', 'invest', 'manage', 'develop', 'support', 'conduct', 'monitor', 'originate']):
                responsibilities.append(bullet.strip())
        
        return responsibilities[:10]
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract requirements/qualifications"""
        requirements = []
        
        # Look for experience years
        years_pattern = r'(\d+[-–]\d+|\d+\+?)\s*years'
        years = re.findall(years_pattern, text)
        
        # Look for qualification keywords
        qual_keywords = ['experience', 'background', 'skills', 'knowledge', 'ability', 'track record', 'demonstrable']
        
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in qual_keywords):
                if len(line) > 20:
                    requirements.append(line.strip())
        
        return requirements[:10]
    
    def _extract_closing_statement(self, text: str) -> str:
        """Extract closing statement"""
        lines = text.split('\n')
        for line in reversed(lines[-20:]):
            line = line.strip()
            if len(line) > 30 and any(word in line.lower() for word in ['opportunity', 'fantastic', 'excellent', 'join', 'team']):
                return line
        return ""
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract common key phrases"""
        key_phrases = []
        
        common_phrases = [
            'our client', 'we are presently advising', 'top-performing', 'leading',
            'credit fund', 'investment team', 'strong performance', 'key hire',
            'ideal candidate', 'successful candidate', 'this opportunity',
            'fantastic opportunity', 'excellent opportunity', 'join', 'demonstrate',
            'proven track record', 'following', 'ambitious', 'growing'
        ]
        
        text_lower = text.lower()
        for phrase in common_phrases:
            if phrase in text_lower:
                key_phrases.append(phrase)
        
        return key_phrases
    
    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze structural elements"""
        structure = {
            "has_opening_hook": bool(re.search(r'(our client|we are presently)', text, re.IGNORECASE)),
            "has_bullet_points": bool(re.search(r'[•\-\*]\s', text)),
            "has_role_positioning": bool(re.search(r'(vp|director|associate|analyst)', text, re.IGNORECASE)),
            "has_responsibilities_section": bool(re.search(r'(responsibilities|role will focus)', text, re.IGNORECASE)),
            "has_requirements_section": bool(re.search(r'(requirements|ideal candidate|successful candidate)', text, re.IGNORECASE)),
            "has_closing": bool(re.search(r'(opportunity|join)', text, re.IGNORECASE)),
            "paragraph_count": len(text.split('\n\n')),
            "has_company_context": bool(re.search(r'(performance|growth|team|aum)', text, re.IGNORECASE))
        }
        
        return structure
    
    def _build_style_profile(self, all_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build comprehensive style profile from all job advert data"""
        logger.info("Building job advert style profile...")
        
        all_opening_lines = []
        all_role_titles = []
        all_key_phrases = []
        all_closings = []
        all_responsibilities = []
        
        for data in all_data:
            style_info = data.get('style_info', {})
            
            if style_info.get('opening_line'):
                all_opening_lines.append(style_info['opening_line'])
            if style_info.get('role_title'):
                all_role_titles.append(style_info['role_title'])
            if style_info.get('key_phrases'):
                all_key_phrases.extend(style_info['key_phrases'])
            if style_info.get('closing_statement'):
                all_closings.append(style_info['closing_statement'])
            if style_info.get('responsibilities'):
                all_responsibilities.extend(style_info['responsibilities'])
        
        return {
            "opening_patterns": Counter(all_opening_lines).most_common(5),
            "role_title_patterns": Counter(all_role_titles).most_common(10),
            "most_common_phrases": Counter(all_key_phrases).most_common(20),
            "closing_patterns": Counter(all_closings).most_common(5),
            "common_responsibilities": Counter(all_responsibilities).most_common(15),
            "structure_consistency": self._calculate_structure_consistency(all_data)
        }
    
    def _calculate_structure_consistency(self, all_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate how consistent the structure is across adverts"""
        structure_elements = {
            "has_opening_hook": 0,
            "has_bullet_points": 0,
            "has_responsibilities_section": 0,
            "has_requirements_section": 0,
            "has_closing": 0
        }
        
        total = len(all_data)
        if total == 0:
            return structure_elements
        
        for data in all_data:
            structure = data.get('style_info', {}).get('structure', {})
            for key in structure_elements.keys():
                if structure.get(key):
                    structure_elements[key] += 1
        
        # Convert to percentages
        for key in structure_elements:
            structure_elements[key] = (structure_elements[key] / total) * 100
        
        return structure_elements
    
    def _generate_recommendations(self, style_profile: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        structure = style_profile.get('structure_consistency', {})
        
        if structure.get('has_opening_hook', 0) > 80:
            recommendations.append("✓ Consistent opening hook pattern - always use 'Our client' or 'We are presently advising'")
        
        if structure.get('has_bullet_points', 0) > 70:
            recommendations.append("✓ Strong use of bullet points for responsibilities - maintain this format")
        
        if structure.get('has_closing', 0) > 85:
            recommendations.append("✓ Always include closing opportunity statement")
        
        return recommendations
    
    def save_analysis(self, analysis_results: Dict[str, Any], output_file: str = "job_advert_style_analysis.json"):
        """Save analysis results to file"""
        with open(output_file, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        logger.info(f"Analysis results saved to {output_file}")

def main():
    """Main function to run job advert style analysis"""
    analyzer = JobAdvertAnalyzer()
    
    logger.info("Starting job advert style analysis for Mawney Partners...")
    results = analyzer.analyze_all_job_adverts()
    
    # Save results
    analyzer.save_analysis(results)
    
    # Print summary
    print("\n" + "="*60)
    print("MAWNEY PARTNERS JOB ADVERT STYLE ANALYSIS")
    print("="*60)
    print(f"Total job adverts analyzed: {results['total_adverts_analyzed']}")
    
    style_profile = results['style_profile']
    
    print("\n📋 MOST COMMON PHRASES:")
    common_phrases = style_profile.get('most_common_phrases', [])
    for phrase, count in common_phrases[:10]:
        print(f"  • '{phrase}': {count} occurrences")
    
    print("\n🎯 STRUCTURE CONSISTENCY:")
    structure = style_profile.get('structure_consistency', {})
    for element, percentage in structure.items():
        print(f"  • {element}: {percentage:.0f}%")
    
    print("\n💡 RECOMMENDATIONS:")
    for rec in results.get('recommendations', []):
        print(f"  {rec}")
    
    print("\n" + "="*60)
    print("Analysis complete! Check job_advert_style_analysis.json for details.")
    print("="*60)

if __name__ == "__main__":
    main()


