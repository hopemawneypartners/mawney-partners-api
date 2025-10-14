"""
CV Style Analyzer for Mawney Partners
Analyzes 43 CV examples to extract company-specific formatting patterns
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
import statistics
from file_analyzer import file_analyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CVStyleAnalyzer:
    """Analyzes CV examples to extract Mawney Partners formatting patterns"""
    
    def __init__(self, examples_folder: str = "example-cvs"):
        self.examples_folder = examples_folder
        self.analysis_results = {
            "header_styles": [],
            "section_headers": [],
            "font_patterns": [],
            "layout_patterns": [],
            "color_patterns": [],
            "spacing_patterns": [],
            "content_structure": [],
            "common_elements": []
        }
    
    def analyze_all_cvs(self) -> Dict[str, Any]:
        """Analyze all CV examples and extract style patterns"""
        logger.info("Starting comprehensive CV style analysis...")
        
        cv_files = self._get_cv_files()
        logger.info(f"Found {len(cv_files)} CV files to analyze")
        
        all_extracted_data = []
        
        for i, cv_file in enumerate(cv_files, 1):
            logger.info(f"Processing CV {i}/{len(cv_files)}: {cv_file}")
            try:
                extracted_data = self._analyze_single_cv(cv_file)
                if extracted_data:
                    all_extracted_data.append(extracted_data)
            except Exception as e:
                logger.error(f"Error processing {cv_file}: {e}")
        
        logger.info(f"Successfully analyzed {len(all_extracted_data)} CVs")
        
        # Analyze patterns across all CVs
        style_profile = self._build_style_profile(all_extracted_data)
        
        return {
            "total_cvs_analyzed": len(all_extracted_data),
            "style_profile": style_profile,
            "raw_data": all_extracted_data,
            "recommendations": self._generate_recommendations(style_profile)
        }
    
    def _get_cv_files(self) -> List[str]:
        """Get list of CV files to analyze"""
        if not os.path.exists(self.examples_folder):
            logger.error(f"Examples folder not found: {self.examples_folder}")
            return []
        
        cv_files = []
        for filename in sorted(os.listdir(self.examples_folder)):
            if filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
                cv_files.append(os.path.join(self.examples_folder, filename))
        
        return cv_files
    
    def _analyze_single_cv(self, cv_path: str) -> Dict[str, Any]:
        """Analyze a single CV file"""
        try:
            # Read file data
            with open(cv_path, 'rb') as f:
                file_data = f.read()
            
            # Determine MIME type
            filename = os.path.basename(cv_path)
            mime_type = self._get_mime_type(filename)
            
            # Analyze file content
            analysis = file_analyzer.analyze_file(file_data, filename, mime_type)
            
            if not analysis.get('extracted_text'):
                logger.warning(f"No text extracted from {filename}")
                return None
            
            # Extract style information
            cv_text = analysis['extracted_text']
            style_info = self._extract_style_info(cv_text, filename)
            
            return {
                "filename": filename,
                "extracted_text": cv_text,
                "style_info": style_info,
                "file_analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {cv_path}: {e}")
            return None
    
    def _get_mime_type(self, filename: str) -> str:
        """Determine MIME type from filename"""
        ext = filename.lower().split('.')[-1]
        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _extract_style_info(self, cv_text: str, filename: str) -> Dict[str, Any]:
        """Extract style information from CV text"""
        style_info = {
            "header_patterns": self._extract_header_patterns(cv_text),
            "section_headers": self._extract_section_headers(cv_text),
            "font_indicators": self._extract_font_indicators(cv_text),
            "layout_indicators": self._extract_layout_indicators(cv_text),
            "content_structure": self._extract_content_structure(cv_text),
            "formatting_patterns": self._extract_formatting_patterns(cv_text),
            "spacing_patterns": self._extract_spacing_patterns(cv_text)
        }
        
        return style_info
    
    def _extract_header_patterns(self, cv_text: str) -> Dict[str, Any]:
        """Extract header formatting patterns"""
        lines = cv_text.split('\n')
        header_info = {
            "name_line": None,
            "contact_info": [],
            "title_line": None,
            "header_structure": []
        }
        
        # Analyze first 10 lines for header patterns
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if not line:
                continue
            
            # Check for name (usually first substantial line)
            if not header_info["name_line"] and len(line) > 2 and len(line) < 50:
                if not any(word in line.lower() for word in ['curriculum', 'vitae', 'resume', 'cv']):
                    header_info["name_line"] = line
            
            # Check for contact info
            if any(indicator in line.lower() for indicator in ['@', 'phone', 'tel', 'mobile', 'email']):
                header_info["contact_info"].append(line)
            
            # Check for professional title
            if any(title in line.lower() for title in ['analyst', 'manager', 'director', 'associate', 'vp']):
                if not header_info["title_line"]:
                    header_info["title_line"] = line
        
        return header_info
    
    def _extract_section_headers(self, cv_text: str) -> List[str]:
        """Extract section headers"""
        section_headers = []
        
        # Common section header patterns
        header_patterns = [
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS headers
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',  # Title Case headers
            r'^\*\*[^*]+\*\*$',  # Bold headers
            r'^[A-Z][a-z]+:',  # Headers with colon
        ]
        
        lines = cv_text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 3 and len(line) < 50:
                for pattern in header_patterns:
                    if re.match(pattern, line):
                        section_headers.append(line)
                        break
        
        return section_headers
    
    def _extract_font_indicators(self, cv_text: str) -> Dict[str, Any]:
        """Extract font-related indicators"""
        font_info = {
            "bold_indicators": [],
            "italic_indicators": [],
            "underline_indicators": [],
            "size_indicators": []
        }
        
        # Look for formatting indicators in text
        bold_patterns = [r'\*\*([^*]+)\*\*', r'__([^_]+)__']
        italic_patterns = [r'\*([^*]+)\*', r'_([^_]+)_']
        
        for pattern in bold_patterns:
            matches = re.findall(pattern, cv_text)
            font_info["bold_indicators"].extend(matches)
        
        for pattern in italic_patterns:
            matches = re.findall(pattern, cv_text)
            font_info["italic_indicators"].extend(matches)
        
        return font_info
    
    def _extract_layout_indicators(self, cv_text: str) -> Dict[str, Any]:
        """Extract layout indicators"""
        layout_info = {
            "line_spacing": [],
            "indentation_patterns": [],
            "alignment_patterns": [],
            "bullet_styles": []
        }
        
        lines = cv_text.split('\n')
        
        # Analyze indentation
        for line in lines:
            if line.strip():
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces > 0:
                    layout_info["indentation_patterns"].append(leading_spaces)
        
        # Analyze bullet styles
        bullet_patterns = [r'^[•\-\*]\s', r'^\d+\.\s', r'^[a-z]\)\s']
        for pattern in bullet_patterns:
            matches = re.findall(pattern, cv_text, re.MULTILINE)
            layout_info["bullet_styles"].extend(matches)
        
        return layout_info
    
    def _extract_content_structure(self, cv_text: str) -> Dict[str, Any]:
        """Extract content structure patterns"""
        structure = {
            "sections": [],
            "paragraph_lengths": [],
            "list_patterns": [],
            "date_formats": []
        }
        
        # Extract sections
        sections = cv_text.split('\n\n')
        for section in sections:
            section = section.strip()
            if len(section) > 20:
                structure["sections"].append({
                    "length": len(section),
                    "lines": len(section.split('\n')),
                    "has_bullets": '•' in section or '-' in section or '*' in section
                })
        
        # Extract date formats
        date_patterns = [
            r'\b(19|20)\d{2}\b',  # Years
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+(19|20)\d{2}\b',  # Month Year
            r'\b\d{1,2}/\d{1,2}/(19|20)\d{2}\b',  # MM/DD/YYYY
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, cv_text)
            structure["date_formats"].extend(matches)
        
        return structure
    
    def _extract_formatting_patterns(self, cv_text: str) -> Dict[str, Any]:
        """Extract general formatting patterns"""
        patterns = {
            "separator_lines": [],
            "special_characters": [],
            "numbering_styles": [],
            "emphasis_patterns": []
        }
        
        # Look for separator lines
        lines = cv_text.split('\n')
        for line in lines:
            if len(line.strip()) > 3 and all(c in '-_=*' for c in line.strip()):
                patterns["separator_lines"].append(line.strip())
        
        # Count special characters
        char_counts = Counter(cv_text)
        special_chars = {char: count for char, count in char_counts.items() 
                        if char in '•*_-=+|()[]{}'}
        patterns["special_characters"] = special_chars
        
        return patterns
    
    def _extract_spacing_patterns(self, cv_text: str) -> Dict[str, Any]:
        """Extract spacing patterns"""
        spacing = {
            "empty_lines": 0,
            "line_lengths": [],
            "paragraph_spacing": []
        }
        
        lines = cv_text.split('\n')
        
        # Count empty lines
        spacing["empty_lines"] = sum(1 for line in lines if not line.strip())
        
        # Analyze line lengths
        for line in lines:
            if line.strip():
                spacing["line_lengths"].append(len(line))
        
        # Analyze paragraph spacing
        current_paragraph_length = 0
        for line in lines:
            if line.strip():
                current_paragraph_length += 1
            else:
                if current_paragraph_length > 0:
                    spacing["paragraph_spacing"].append(current_paragraph_length)
                    current_paragraph_length = 0
        
        return spacing
    
    def _build_style_profile(self, all_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build comprehensive style profile from all CV data"""
        logger.info("Building comprehensive style profile...")
        
        profile = {
            "header_analysis": self._analyze_headers(all_data),
            "section_analysis": self._analyze_sections(all_data),
            "layout_analysis": self._analyze_layout(all_data),
            "content_analysis": self._analyze_content(all_data),
            "formatting_analysis": self._analyze_formatting(all_data)
        }
        
        return profile
    
    def _analyze_headers(self, all_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze header patterns across all CVs"""
        header_patterns = []
        contact_patterns = []
        
        for data in all_data:
            style_info = data.get('style_info', {})
            header_info = style_info.get('header_patterns', {})
            
            if header_info.get('name_line'):
                header_patterns.append(header_info['name_line'])
            
            contact_patterns.extend(header_info.get('contact_info', []))
        
        return {
            "common_name_patterns": self._find_common_patterns(header_patterns),
            "contact_format_patterns": self._find_common_patterns(contact_patterns),
            "header_structure_consistency": len(set(header_patterns)) / len(header_patterns) if header_patterns else 0
        }
    
    def _analyze_sections(self, all_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze section patterns across all CVs"""
        all_section_headers = []
        
        for data in all_data:
            style_info = data.get('style_info', {})
            section_headers = style_info.get('section_headers', [])
            all_section_headers.extend(section_headers)
        
        # Find most common section headers
        header_counts = Counter(all_section_headers)
        
        return {
            "most_common_sections": header_counts.most_common(20),
            "section_naming_patterns": self._analyze_section_naming_patterns(all_section_headers),
            "total_unique_sections": len(header_counts)
        }
    
    def _analyze_layout(self, all_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze layout patterns across all CVs"""
        all_indentation = []
        all_bullet_styles = []
        
        for data in all_data:
            style_info = data.get('style_info', {})
            layout_info = style_info.get('layout_indicators', {})
            
            all_indentation.extend(layout_info.get('indentation_patterns', []))
            all_bullet_styles.extend(layout_info.get('bullet_styles', []))
        
        return {
            "common_indentation": statistics.mode(all_indentation) if all_indentation else 0,
            "indentation_distribution": Counter(all_indentation),
            "bullet_style_preferences": Counter(all_bullet_styles),
            "layout_consistency": self._calculate_consistency_score(all_indentation)
        }
    
    def _analyze_content(self, all_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content patterns across all CVs"""
        all_sections = []
        all_date_formats = []
        
        for data in all_data:
            style_info = data.get('style_info', {})
            content_structure = style_info.get('content_structure', {})
            
            all_sections.extend(content_structure.get('sections', []))
            all_date_formats.extend(content_structure.get('date_formats', []))
        
        return {
            "average_section_length": statistics.mean([s['length'] for s in all_sections]) if all_sections else 0,
            "common_date_formats": Counter(all_date_formats),
            "content_structure_patterns": self._analyze_content_structure_patterns(all_sections)
        }
    
    def _analyze_formatting(self, all_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze formatting patterns across all CVs"""
        all_separators = []
        all_special_chars = defaultdict(int)
        
        for data in all_data:
            style_info = data.get('style_info', {})
            formatting_patterns = style_info.get('formatting_patterns', {})
            
            all_separators.extend(formatting_patterns.get('separator_lines', []))
            
            special_chars = formatting_patterns.get('special_characters', {})
            for char, count in special_chars.items():
                all_special_chars[char] += count
        
        return {
            "separator_usage": Counter(all_separators),
            "special_character_frequency": dict(all_special_chars),
            "formatting_consistency": self._calculate_formatting_consistency(all_data)
        }
    
    def _find_common_patterns(self, items: List[str]) -> List[Tuple[str, int]]:
        """Find common patterns in a list of items"""
        return Counter(items).most_common(10)
    
    def _analyze_section_naming_patterns(self, section_headers: List[str]) -> Dict[str, Any]:
        """Analyze patterns in section naming"""
        patterns = {
            "all_caps": sum(1 for header in section_headers if header.isupper()),
            "title_case": sum(1 for header in section_headers if header.istitle()),
            "with_colons": sum(1 for header in section_headers if ':' in header),
            "with_asterisks": sum(1 for header in section_headers if '*' in header)
        }
        
        return patterns
    
    def _calculate_consistency_score(self, values: List[int]) -> float:
        """Calculate consistency score for a list of values"""
        if not values:
            return 0.0
        
        unique_values = len(set(values))
        total_values = len(values)
        
        # Lower ratio means more consistent
        return 1.0 - (unique_values / total_values)
    
    def _analyze_content_structure_patterns(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content structure patterns"""
        if not sections:
            return {}
        
        return {
            "average_lines_per_section": statistics.mean([s['lines'] for s in sections]),
            "sections_with_bullets": sum(1 for s in sections if s['has_bullets']),
            "total_sections": len(sections)
        }
    
    def _calculate_formatting_consistency(self, all_data: List[Dict[str, Any]]) -> float:
        """Calculate overall formatting consistency score"""
        # This is a simplified consistency calculation
        # Could be enhanced with more sophisticated analysis
        return 0.8  # Placeholder
    
    def _generate_recommendations(self, style_profile: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on style analysis"""
        recommendations = []
        
        # Header recommendations
        header_analysis = style_profile.get('header_analysis', {})
        if header_analysis.get('header_structure_consistency', 0) > 0.7:
            recommendations.append("High consistency in header structure - good for standardization")
        
        # Section recommendations
        section_analysis = style_profile.get('section_analysis', {})
        if section_analysis.get('total_unique_sections', 0) > 10:
            recommendations.append("Consider standardizing section naming for consistency")
        
        # Layout recommendations
        layout_analysis = style_profile.get('layout_analysis', {})
        if layout_analysis.get('layout_consistency', 0) > 0.8:
            recommendations.append("Strong layout consistency - excellent for professional presentation")
        
        return recommendations
    
    def save_analysis(self, analysis_results: Dict[str, Any], output_file: str = "cv_style_analysis.json"):
        """Save analysis results to file"""
        with open(output_file, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        logger.info(f"Analysis results saved to {output_file}")

def main():
    """Main function to run CV style analysis"""
    analyzer = CVStyleAnalyzer()
    
    logger.info("Starting CV style analysis for Mawney Partners...")
    results = analyzer.analyze_all_cvs()
    
    # Save results
    analyzer.save_analysis(results)
    
    # Print summary
    print("\n" + "="*60)
    print("MAWNEY PARTNERS CV STYLE ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total CVs analyzed: {results['total_cvs_analyzed']}")
    
    style_profile = results['style_profile']
    
    print("\n📋 SECTION ANALYSIS:")
    section_analysis = style_profile.get('section_analysis', {})
    most_common = section_analysis.get('most_common_sections', [])
    for section, count in most_common[:10]:
        print(f"  • {section}: {count} occurrences")
    
    print("\n📄 HEADER ANALYSIS:")
    header_analysis = style_profile.get('header_analysis', {})
    print(f"  • Header consistency: {header_analysis.get('header_structure_consistency', 0):.2f}")
    
    print("\n🎨 LAYOUT ANALYSIS:")
    layout_analysis = style_profile.get('layout_analysis', {})
    print(f"  • Layout consistency: {layout_analysis.get('layout_consistency', 0):.2f}")
    
    print("\n💡 RECOMMENDATIONS:")
    for rec in results.get('recommendations', []):
        print(f"  • {rec}")
    
    print("\n" + "="*60)
    print("Analysis complete! Check cv_style_analysis.json for detailed results.")
    print("="*60)

if __name__ == "__main__":
    main()


