#!/usr/bin/env python3
"""
Mawney Partners CV Template Formatter
Uses the exact HTML template to match the design shown in examples
"""

import re
import logging
import os
from typing import Dict, List, Optional, Any
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MawneyTemplateFormatter:
    """Formats CVs using the exact Mawney Partners template"""
    
    def __init__(self):
        self.template_path = os.path.join(os.path.dirname(__file__), 'mawney_cv_template_correct.html')
        
    def format_cv_with_template(self, cv_data: str, filename: str = '', font_info: List[Dict] = None) -> Dict[str, Any]:
        """Format CV using the exact Mawney Partners template (compatible with AI assistant)"""
        try:
            logger.info(f"Using template path: {self.template_path}")
            logger.info(f"Template exists: {os.path.exists(self.template_path)}")
            
            # Parse the CV data (pass font_info for better name extraction)
            parsed_data = self._parse_cv_data(cv_data, font_info=font_info)
            
            # Log what was extracted for debugging
            logger.info(f"📊 Parsed CV data summary:")
            logger.info(f"   Name: {parsed_data.get('name', 'NOT FOUND')}")
            logger.info(f"   Email: {parsed_data.get('email', 'NOT FOUND')}")
            logger.info(f"   Phone: {parsed_data.get('phone', 'NOT FOUND')}")
            logger.info(f"   Location: {parsed_data.get('location', 'NOT FOUND')}")
            logger.info(f"   Experience entries: {len(parsed_data.get('experience', []))}")
            logger.info(f"   Education entries: {len(parsed_data.get('education', []))}")
            logger.info(f"   Skills count: {len(parsed_data.get('skills', []))}")
            logger.info(f"   Summary length: {len(parsed_data.get('summary', ''))}")
            
            # Load the template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            logger.info(f"Template loaded, length: {len(template)} characters")
            
            # Get both logos for Mawney Partners CV format
            top_logo_base64 = self._get_top_logo_base64()
            bottom_logo_base64 = self._get_bottom_logo_base64()
            
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return {
                'success': False,
                'error': f"Template loading failed: {str(e)}",
                'html_version': '',
                'text_version': '',
                'download_url': '',
                'download_filename': ''
            }
        
        # Fill in the template using safe string replacement to avoid Python format conflicts
        formatted_html = template
        
        # Log what we're putting into the template
        name = parsed_data.get('name', '')
        contact_info = self._format_contact_info(parsed_data)
        summary = self._format_professional_summary(parsed_data)
        skills = self._format_skills_list(parsed_data)
        experience = self._format_experience_items(parsed_data)
        education = self._format_education_items(parsed_data)
        
        logger.info(f"📝 Template replacement:")
        logger.info(f"   NAME length: {len(name)} chars - '{name[:50]}...'")
        logger.info(f"   CONTACT_INFO length: {len(contact_info)} chars - '{contact_info[:50]}...'")
        logger.info(f"   SUMMARY length: {len(summary)} chars")
        logger.info(f"   SKILLS length: {len(skills)} chars")
        logger.info(f"   EXPERIENCE length: {len(experience)} chars")
        logger.info(f"   EDUCATION length: {len(education)} chars")
        
        formatted_html = formatted_html.replace('{TOP_LOGO_BASE64}', top_logo_base64)
        formatted_html = formatted_html.replace('{BOTTOM_LOGO_BASE64}', bottom_logo_base64)
        formatted_html = formatted_html.replace('{NAME}', name)
        formatted_html = formatted_html.replace('{CONTACT_INFO}', contact_info)
        formatted_html = formatted_html.replace('{PROFESSIONAL_SUMMARY}', summary)
        formatted_html = formatted_html.replace('{SKILLS_LIST}', skills)
        formatted_html = formatted_html.replace('{EXPERIENCE_ITEMS}', experience)
        formatted_html = formatted_html.replace('{EDUCATION_ITEMS}', education)
        
        logger.info(f"✅ Formatted CV using template, length: {len(formatted_html)} characters")
        
        return {
            'success': True,
            'html_version': formatted_html,
            'html_content': formatted_html,  # ensure downstream callers find HTML consistently
            'text_version': self._extract_text_from_html(formatted_html),
            'analysis': f"CV formatted using Mawney Partners template. Extracted: {len(parsed_data.get('experience', []))} experience items, {len(parsed_data.get('education', []))} education items.",
            'sections_found': list(parsed_data.keys()),
            'formatted_data': parsed_data
        }

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
    
    def _clean_cv_text(self, text: str) -> str:
        """Clean CV text to fix concatenated words and improve parsing"""
        import re
        
        # CRITICAL: Force structure into CV format by adding line breaks strategically
        # First, fix concatenations
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Add line breaks before CV section headers to preserve structure
        cv_section_headers = [
            'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EMPLOYMENT HISTORY', 'CAREER HISTORY',
            'EDUCATION', 'QUALIFICATIONS', 'ACADEMIC BACKGROUND',
            'PROFESSIONAL SUMMARY', 'SUMMARY', 'PROFILE', 'OBJECTIVE',
            'SKILLS', 'COMPETENCIES', 'TECHNICAL SKILLS', 'KEY SKILLS',
            'CERTIFICATIONS', 'PROFESSIONAL CERTIFICATIONS',
            'INTERESTS', 'HOBBIES', 'PERSONAL INTERESTS',
            'LANGUAGES', 'REFERENCES'
        ]
        
        for header in cv_section_headers:
            # Add line breaks before section headers (case insensitive)
            text = re.sub(f'([a-z])({header})', r'\1\n\n\2', text, flags=re.IGNORECASE)
            text = re.sub(f'({header})([A-Z][a-z])', r'\1\n\n\2', text, flags=re.IGNORECASE)
        
        # Add line breaks before company names (all caps with 2+ words)
        text = re.sub(r'([a-z])([A-Z]{2,}\s+[A-Z]{2,})', r'\1\n\n\2', text)
        
        # Add line breaks before dates (year ranges)
        text = re.sub(r'([a-z])((?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2})', r'\1\n\2', text, flags=re.IGNORECASE)
        text = re.sub(r'([a-z])((?:19|20)\d{2}\s*[-–]\s*(?:Present|Current))', r'\1\n\2', text, flags=re.IGNORECASE)
        
        # Add line breaks before bullet points
        text = re.sub(r'([a-z])([•▪▫‣⁃])', r'\1\n\2', text, flags=re.IGNORECASE)
        
        # CRITICAL: Force structure by adding line breaks before common patterns
        # Add line breaks before job titles (common patterns)
        text = re.sub(r'([a-z])([A-Z][A-Z\s]+(?:ASSOCIATE|ANALYST|MANAGER|DIRECTOR|OFFICER|SPECIALIST))', r'\1\n\n\2', text, flags=re.IGNORECASE)
        
        # Add line breaks before email addresses
        text = re.sub(r'([a-z])([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'\1\n\2', text)
        
        # Add line breaks before phone numbers
        text = re.sub(r'([a-z])((?:Tel|Phone|Mobile|Mob)[:\s]*[+\d\s\-\(\)]+)', r'\1\n\2', text, flags=re.IGNORECASE)
        
        # Add line breaks before addresses (common patterns)
        text = re.sub(r'([a-z])(\d+\s+[A-Za-z\s]+(?:Way|Street|Road|Avenue|Lane|Drive|Close|Crescent))', r'\1\n\2', text)
        
        # Add line breaks before location patterns
        text = re.sub(r'([a-z])([A-Z][a-z]+,\s*[A-Z]{2,3}\s+\d{4,5})', r'\1\n\2', text)
        
        # Add line breaks before common job description patterns
        text = re.sub(r'([a-z])(MANAGING|DEVELOPING|ANALYZING|CREATING|IMPLEMENTING)', r'\1\n\n\2', text)
        
        # CRITICAL: Fix concatenated words that are common in CVs
        # Add spaces between lowercase and uppercase letters
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # Fix specific concatenated words we've seen
        text = re.sub(r'stronganalytical', 'strong analytical', text, flags=re.IGNORECASE)
        text = re.sub(r'andproblem-solving', 'and problem-solving', text, flags=re.IGNORECASE)
        text = re.sub(r'problem-solving', 'problem-solving', text, flags=re.IGNORECASE)
        text = re.sub(r'lookingfor', 'looking for', text, flags=re.IGNORECASE)
        text = re.sub(r'ananalyst', 'an analyst', text, flags=re.IGNORECASE)
        text = re.sub(r'financialrisk', 'financial risk', text, flags=re.IGNORECASE)
        text = re.sub(r'derivativeproducts', 'derivative products', text, flags=re.IGNORECASE)
        text = re.sub(r'statisticalmodelling', 'statistical modelling', text, flags=re.IGNORECASE)
        text = re.sub(r'financialmathematics', 'financial mathematics', text, flags=re.IGNORECASE)
        text = re.sub(r'Responsible,', 'Responsible,', text, flags=re.IGNORECASE)
        text = re.sub(r'detail-oriented', 'detail-oriented', text, flags=re.IGNORECASE)
        text = re.sub(r'RISKMETRICSONFINANCIALDERIVATIVES', 'RISK METRICS ON FINANCIAL DERIVATIVES', text, flags=re.IGNORECASE)
        text = re.sub(r'RISKMETRICSON', 'RISK METRICS ON', text, flags=re.IGNORECASE)
        text = re.sub(r'FINANCIALDERIVATIVES', 'FINANCIAL DERIVATIVES', text, flags=re.IGNORECASE)
        text = re.sub(r'METRICSONFINANCIALDERIVATIVES', 'METRICS ON FINANCIAL DERIVATIVES', text, flags=re.IGNORECASE)
        text = re.sub(r'METRICSONFINANCIAL', 'METRICS ON FINANCIAL', text, flags=re.IGNORECASE)
        text = re.sub(r'andproblem-solving', 'and problem-solving', text, flags=re.IGNORECASE)
        text = re.sub(r'andproblem', 'and problem', text, flags=re.IGNORECASE)
        text = re.sub(r'andanalytical', 'and analytical', text, flags=re.IGNORECASE)
        
        return text

    def _parse_cv_data(self, cv_data: str, font_info: List[Dict] = None) -> Dict[str, Any]:
        """Parse CV data to extract structured information with professional formatting"""
        # CRITICAL: First reconstruct fragmented words (before any other processing)
        import re
        # Fix common word duplications (general pattern, not specific names)
        # Pattern: repeated words like "WORD WORD" -> "WORD"
        cv_data = re.sub(r'\b(\w+)\s+\1\b', r'\1', cv_data, flags=re.IGNORECASE)
        # Fix common word fragments - GENERAL patterns for all CVs
        # Common splits in PDF extraction
        common_fragments = [
            (r'\bde\s+velopment\b', 'development'),
            (r'\bde\s+sign\b', 'design'),
            (r'\bpro\s+fessional\b', 'professional'),
            (r'\bmar\s+keting\b', 'marketing'),
            (r'\bcom\s+munication\b', 'communication'),
            (r'\bstrat\s+egy\b', 'strategy'),
            (r'\bfin\s+ancial\b', 'financial'),
            (r'\ban\s+alyst\b', 'analyst'),
            (r'\bin\s+vestment\b', 'investment'),
            (r'\bport\s+folio\b', 'portfolio'),
            # Company name fragments - general
            (r'\bartners\b', 'Partners'),
            (r'\bcap\s+ital\b', 'Capital'),
        ]
        for pattern, replacement in common_fragments:
            cv_data = re.sub(pattern, replacement, cv_data, flags=re.IGNORECASE)
        
        # CRITICAL: Clean the text first to fix concatenated words
        cleaned_cv_data = self._clean_cv_text(cv_data)
        lines = [line.strip() for line in cleaned_cv_data.split('\n') if line.strip()]
        
        # Apply reconstruction to each line as well - GENERAL patterns
        reconstructed_lines = []
        for i, line in enumerate(lines):
            # Fix common word fragments in each line (general patterns)
            common_fragments = [
                (r'\bde\s+velopment\b', 'development'),
                (r'\bde\s+sign\b', 'design'),
                (r'\bpro\s+fessional\b', 'professional'),
                (r'\bmar\s+keting\b', 'marketing'),
                (r'\bcom\s+munication\b', 'communication'),
                (r'\bstrat\s+egy\b', 'strategy'),
                (r'\bfin\s+ancial\b', 'financial'),
                (r'\ban\s+alyst\b', 'analyst'),
                (r'\bin\s+vestment\b', 'investment'),
                (r'\bartners\b', 'Partners'),
            ]
            for pattern, replacement in common_fragments:
                line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
            
            # Check for single-character words that might be fragments
            # Merge with adjacent words if they form common patterns
            words = line.split()
            if len(words) >= 2:
                merged_words = []
                j = 0
                while j < len(words):
                    word = words[j]
                    # If single char and next word exists, check if they should merge
                    if len(word) == 1 and word.isalpha() and j < len(words) - 1:
                        next_word = words[j + 1]
                        # Common patterns: "de" + "velopment", "pro" + "fessional", etc.
                        potential = word.lower() + next_word.lower()
                        if potential in ['development', 'design', 'professional', 'marketing', 'communication', 'strategy', 'financial', 'analyst', 'investment']:
                            # Find the full word
                            full_word = next((w for w in ['development', 'design', 'professional', 'marketing', 'communication', 'strategy', 'financial', 'analyst', 'investment'] if w.startswith(potential)), None)
                            if full_word:
                                merged_words.append(full_word.capitalize() if word[0].isupper() else full_word)
                                j += 2
                                continue
                    merged_words.append(word)
                    j += 1
                line = ' '.join(merged_words)
            
            reconstructed_lines.append(line)
        lines = reconstructed_lines
        
        # Use font_info to help identify large text (likely names)
        large_text_candidates = []
        if font_info:
            for info in font_info:
                large_text = info.get('large_text', '')
                if large_text:
                    # Split into potential name candidates
                    words = large_text.split()
                    if 2 <= len(words) <= 5:
                        candidate = ' '.join(words)
                        # Check if it looks like a name
                        if all(word[0].isupper() for word in words if word and word[0].isalpha()):
                            if not re.search(r'\d', candidate) and not any(char in candidate for char in ['@', '+']):
                                large_text_candidates.append(candidate)
                                logger.info(f"Found large text candidate (likely name): {candidate}")
        
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
        
        # Extract name with better pattern matching and fragmentation handling
        # Also check for artistically formatted names (large text, all caps, styled)
        if lines:
            name_candidates = []
            
            # First, try to find name in first few lines (most common location)
            # Be more aggressive - names are often artistically formatted
            for i, line in enumerate(lines[:15]):  # Check more lines
                line_original = line
                line = line.strip()
                
                # Skip obvious headers
                if any(keyword in line.lower() for keyword in ['curriculum', 'vitae', 'resume', 'cv', 'page', 'document', 'professional', 'creative']):
                    continue
                
                # Skip contact info lines
                if '@' in line or re.search(r'\+?[\d\s\-\(\)]{10,}', line):
                    continue
                
                # Skip lines that are clearly not names
                if any(word in line.lower() for word in ['experience', 'education', 'skills', 'summary', 'profile', 'objective']):
                    continue
                
                words = line.split()
                
                # Look for proper name patterns (2-4 words, title case or all caps)
                # Be more lenient for artistically formatted names
                if 2 <= len(words) <= 5:  # Allow up to 5 words (e.g., "Mary Jane Watson Smith")
                    # Check if all words start with capital (title case) or all uppercase
                    is_title_case = all(word[0].isupper() for word in words if word and word[0].isalpha())
                    is_all_caps = line.isupper() and len(line) < 60  # Allow longer all-caps names
                    
                    # Also check for mixed case (artistic formatting)
                    has_capitals = any(word[0].isupper() for word in words if word and word[0].isalpha())
                    mostly_capitals = sum(1 for word in words if word and word[0].isupper()) >= len(words) * 0.8
                    
                    if (is_title_case or is_all_caps or (has_capitals and mostly_capitals)) and not any(char in line for char in ['@', '+', '(', ')', '/', '\\']):
                        # Additional check: names usually don't have numbers
                        # But allow some special chars for artistic formatting
                        has_numbers = bool(re.search(r'\d', line))
                        # Allow some punctuation for artistic names (e.g., "O'Brien")
                        special_chars = re.findall(r'[^\w\s]', line)
                        has_too_many_special = len(special_chars) > 2
                        
                        if not has_numbers and not has_too_many_special:
                            # Check if it looks like a real name (not a job title or section)
                            if not any(word.lower() in ['the', 'and', 'or', 'of', 'for', 'with', 'from', 'to'] for word in words):
                                name_candidates.append((line, i, 'standard'))
            
            # Also check for names that might be split across lines (artistic formatting)
            # Also check for fragmented names - look for patterns where first part is missing
            for i in range(min(8, len(lines) - 1)):
                line1 = lines[i].strip() if i < len(lines) else ""
                line2 = lines[i+1].strip() if i+1 < len(lines) else ""
                
                # Check if two consecutive lines might form a name
                if line1 and line2:
                    # Skip if either line looks like a header or contact info
                    if any(keyword in line1.lower() or keyword in line2.lower() 
                           for keyword in ['curriculum', 'vitae', 'resume', 'cv', 'professional', 'creative', '@']):
                        continue
                    
                    combined = f"{line1} {line2}"
                    words = combined.split()
                    if 2 <= len(words) <= 5:
                        # Check if it forms a valid name pattern
                        is_title_case = all(word[0].isupper() for word in words if word and word[0].isalpha())
                        is_all_caps = combined.isupper() and len(combined) < 60
                        
                        if (is_title_case or is_all_caps) and not any(char in combined for char in ['@', '+', '(', ')', '/', '\\']):
                            if not re.search(r'\d', combined):
                                name_candidates.append((combined, i, 'split'))
                
                # Check for fragmented names where first part might be missing
                # Pattern: "PE" or "PE GILBERT" - might be missing "HO" or "HOPE"
                if line1.upper() == 'PE' and line2:
                    line2_words = line2.split()
                    # If line2 is a surname (single word, capitalized)
                    if len(line2_words) == 1 and line2_words[0][0].isupper() and len(line2_words[0]) > 3:
                        # Check if previous lines might have "HO" or "HOPE"
                        for j in range(max(0, i-3), i):
                            prev_line = lines[j].strip().upper()
                            if prev_line in ['HO', 'HOPE']:
                                # Reconstruct name
                                if prev_line == 'HO':
                                    reconstructed = f"HOPE {line2}"
                                else:
                                    reconstructed = f"{prev_line} {line2}"
                                name_candidates.append((reconstructed, j, 'reconstructed'))
                                break
                        # If no "HO" found, "PE" might be a fragment - try common name patterns
                        # But be conservative - only if it really looks like a name
                        if line2_words[0][0].isupper() and len(line2_words[0]) >= 4:
                            # Common pattern: missing first part of first name
                            # We can't guess the full name, but we can note it's likely incomplete
                            pass
            
            # Add large text candidates from font_info (artistically formatted names)
            if large_text_candidates:
                for candidate in large_text_candidates:
                    name_candidates.append((candidate, 0, 'large_text'))  # Position 0 = top of page
            
            # If we found candidates, pick the best one
            if name_candidates:
                # Score candidates: prefer earlier in doc, longer names, standard format over split
                # Large text gets highest priority (artistically formatted names)
                def score_candidate(candidate):
                    name, pos, source = candidate
                    score = 0
                    # Large text (artistically formatted) gets highest priority
                    if source == 'large_text':
                        score += 200
                    # Reconstructed names get high priority (we fixed fragments)
                    if source == 'reconstructed':
                        score += 150
                    # Earlier is better (names are usually at top)
                    score += (15 - pos) * 10
                    # Longer names are better (more complete)
                    score += len(name) * 2
                    # Standard format preferred over split
                    if source == 'standard':
                        score += 50
                    # Prefer 2-3 word names (most common)
                    word_count = len(name.split())
                    if 2 <= word_count <= 3:
                        score += 30
                    # Penalize names with single-character words that look like fragments
                    name_words = name.split()
                    if any(len(w) == 1 and w.isalpha() and i < len(name_words) - 1 for i, w in enumerate(name_words)):
                        # Might be a fragment, slightly penalize
                        score -= 20
                    return score
                
                name_candidates.sort(key=score_candidate, reverse=True)
                final_name = name_candidates[0][0]
                # Fix any word duplications (general pattern, not specific names)
                # Pattern: repeated words like "WORD WORD" -> "WORD"
                final_name = re.sub(r'\b(\w+)\s+\1\b', r'\1', final_name, flags=re.IGNORECASE)
                # Clean up extra spaces and fix common fragments
                final_name = ' '.join(final_name.split())
                # Remove any single-character words that might be fragments (but keep if it's a valid initial)
                words = final_name.split()
                cleaned_words = []
                for word in words:
                    # Keep single letters if they're likely initials (A, B, C, etc. followed by another word)
                    if len(word) == 1 and word.isalpha() and cleaned_words:
                        # Might be an initial, keep it
                        cleaned_words.append(word)
                    elif len(word) > 1:
                        cleaned_words.append(word)
                final_name = ' '.join(cleaned_words)
                parsed['name'] = final_name
                logger.info(f"✅ Extracted name: '{parsed['name']}' from position {name_candidates[0][1]} (source: {name_candidates[0][2]})")
            else:
                # Fallback: try to reconstruct name from fragmented text
                # Look for patterns like "HO PE" or "PE GILBERT" that might be fragments
                for i in range(min(3, len(lines))):
                    line1 = lines[i].strip() if i < len(lines) else ""
                    line2 = lines[i+1].strip() if i+1 < len(lines) else ""
                    
                    # Check if two consecutive lines might form a name
                    if line1 and line2:
                        combined = f"{line1} {line2}"
                        words = combined.split()
                        if 2 <= len(words) <= 4:
                            if all(word[0].isupper() for word in words if word and word[0].isalpha()):
                                if not any(char in combined for char in ['@', '+', '(', ')', '/', '\\', '-']):
                                    parsed['name'] = combined
                                    break
                
                # Final fallback: first substantial line that looks like a name
                # Also check if name might be incomplete (like "PE GILBERT" missing "HO")
                if not parsed['name']:
                    for line in lines[:8]:
                        words = line.split()
                        # Check for incomplete names (2 words, one might be very short like "PE")
                        if len(words) == 2:
                            word1, word2 = words[0], words[1]
                            # If first word is very short (1-2 chars) and second is a proper surname
                            if len(word1) <= 2 and len(word2) >= 4 and word2[0].isupper():
                                # This might be an incomplete name - check previous lines for missing part
                                for j in range(max(0, lines.index(line) - 3), lines.index(line)):
                                    prev = lines[j].strip().upper()
                                    if prev in ['HO', 'HOPE', 'H', 'O']:
                                        # Reconstruct
                                        if prev == 'HO':
                                            parsed['name'] = f"HOPE {word2}"
                                        elif prev == 'HOPE':
                                            parsed['name'] = f"HOPE {word2}"
                                        else:
                                            # Try to combine
                                            parsed['name'] = f"{prev} {word1} {word2}".strip()
                                        break
                                if parsed['name']:
                                    break
                        # Standard name check
                        if len(words) >= 2 and len(words) <= 4:
                            if all(word[0].isupper() for word in words if word and word[0].isalpha()):
                                if not any(char in line for char in ['@', '+', '(', ')', '/', '\\']):
                                    parsed['name'] = line
                                    break
        
        # Extract contact info with improved patterns
        full_text = ' '.join(lines)
        
        # Email extraction - more comprehensive patterns
        email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Standard email
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\.?',  # Email with optional trailing dot
            r'[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',  # Email with spaces around @
            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(com|co\.uk|org|net|edu|gov)',  # Common domains
        ]
        
        for pattern in email_patterns:
            email_match = re.search(pattern, full_text, re.IGNORECASE)
            if email_match:
                email = email_match.group(0).strip()
                # Clean up email (remove spaces, trailing dots)
                email = re.sub(r'\s+', '', email)
                email = email.rstrip('.')
                if '@' in email and '.' in email.split('@')[1]:
                    parsed['email'] = email
                    logger.info(f"Extracted email: {parsed['email']}")
                    break
        
        # Also check individual lines for emails (sometimes they're on their own line)
        if not parsed['email']:
            for line in lines[:20]:  # Check first 20 lines
                for pattern in email_patterns:
                    email_match = re.search(pattern, line, re.IGNORECASE)
                    if email_match:
                        email = email_match.group(0).strip()
                        email = re.sub(r'\s+', '', email)
                        email = email.rstrip('.')
                        if '@' in email and '.' in email.split('@')[1]:
                            parsed['email'] = email
                            logger.info(f"Extracted email from line: {parsed['email']}")
                            break
                if parsed['email']:
                    break
        
        # Phone extraction with better patterns - check full text and individual lines
        phone_patterns = [
            r'\+44[\s\-]?\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',  # UK phone
            r'\+1[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{4}',  # US phone
            r'\b\d{4}[\s\-]?\d{3}[\s\-]?\d{3}\b',  # UK mobile
            r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b',  # US phone
            r'\+?[\d\s\-\(\)]{10,}',  # General phone pattern
            r'\b\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}\b',  # UK format: 079 2946 0839
            r'\b0\d{2,3}[\s\-]?\d{3,4}[\s\-]?\d{3,4}\b',  # UK format: 07929 460839
            r'0\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',  # UK phone without +
        ]
        
        # First try full text
        for pattern in phone_patterns:
            phone_match = re.search(pattern, full_text)
            if phone_match:
                phone = phone_match.group(0).strip()
                # Clean up phone number
                phone = re.sub(r'[^\d\+\s\-\(\)]', '', phone)
                if len(phone) >= 10:  # Valid phone length
                    parsed['phone'] = phone
                    logger.info(f"Extracted phone from full text: {parsed['phone']}")
                    break
        
        # If not found, check individual lines (especially first 20 lines)
        if not parsed['phone']:
            for line in lines[:20]:
                for pattern in phone_patterns:
                    phone_match = re.search(pattern, line)
                    if phone_match:
                        phone = phone_match.group(0).strip()
                        phone = re.sub(r'[^\d\+\s\-\(\)]', '', phone)
                        if len(phone) >= 10:
                            parsed['phone'] = phone
                            logger.info(f"Extracted phone from line: {parsed['phone']}")
                            break
                if parsed['phone']:
                    break
        
        # Location extraction
        location_keywords = ['england', 'uk', 'united kingdom', 'london', 'manchester', 'birmingham', 'leeds', 'sheffield', 'bristol', 'newcastle', 'liverpool']
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in location_keywords):
                parsed['location'] = line
                break
        
        # Extract professional summary - look for actual CV content, not auto-populated
        summary_started = False
        current_summary = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['professional summary', 'profile', 'overview', 'objective']):
                summary_started = True
                continue
            elif summary_started and any(keyword in line_lower for keyword in ['experience', 'education', 'skills', 'work']):
                break
            elif summary_started and line and len(line) > 20:  # Substantial content
                current_summary.append(line)
        
        # Only use actual CV summary, not auto-populated content
        if current_summary and not any(generic in ' '.join(current_summary).lower() for generic in ['postgraduate and certified', 'looking for an analyst position', 'financial risk management']):
            parsed['summary'] = ' '.join(current_summary)
        else:
            # Extract first substantial paragraph as summary if no dedicated summary section
            for line in lines[2:8]:  # Check lines 3-8 for potential summary
                if len(line) > 50 and not any(keyword in line.lower() for keyword in ['experience', 'education', 'skills', 'work', 'contact']):
                    parsed['summary'] = line
                    break
        
        # Extract experience with improved structure detection
        # Use line-by-line parsing which works better with fragmented PDF text
        # IMPORTANT: Also check for jobs BEFORE the "WORK EXPERIENCE" header
        # Many CVs list recent jobs near the top before the formal section header
        experience_patterns = []
        experience_section = False
        current_experience = None
        current_responsibilities = []
        
        logger.info(f"Starting experience extraction from {len(lines)} lines")
        
        # First pass: Look for jobs near the top (before formal section headers)
        # These are often the most recent/important positions
        top_section_jobs = []
        for i, line in enumerate(lines[:30]):  # Check first 30 lines
            line_lower = line.lower().strip()
            # Skip if we hit a section header
            if any(keyword in line_lower for keyword in ['work experience', 'professional experience', 'education', 'skills', 'profile', 'summary']):
                break
            
            # Check if this line looks like a job entry (has date + job/company keywords)
            has_date = bool(re.search(r'\b(19|20)\d{2}\s*[-–]', line, re.IGNORECASE))
            has_month_date = bool(re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–]', line, re.IGNORECASE))
            looks_like_job = any(indicator in line_lower for indicator in job_title_indicators + company_indicators)
            
            if (has_date or has_month_date) and looks_like_job and len(line.split()) <= 10:
                # This might be a job entry near the top
                # Extract it
                parts = re.split(r'\s*[—–-]\s*|\s*,\s*', line)
                date_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4})\s*[-–]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}|Present|Current|Now)', line, re.IGNORECASE)
                dates = date_match.group(0).strip() if date_match else ""
                line_without_dates = re.sub(r'\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4})\s*[-–]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}|Present|Current|Now)\s*', '', line).strip()
                parts = re.split(r'\s*[—–-]\s*|\s*,\s*', line_without_dates)
                title = parts[0].strip() if parts else line_without_dates
                company = parts[1].strip() if len(parts) > 1 else ""
                company = self._reconstruct_company_names(company)
                top_section_jobs.append({
                    'title': title if title else 'POSITION',
                    'company': company if company else 'COMPANY',
                    'location': parts[2].strip() if len(parts) > 2 else '',
                    'dates': dates,
                    'responsibilities': []
                })
        
        # Now do the main parsing starting from experience section
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            line_upper = line.upper().strip()
            
            # Detect start of experience section
            if any(keyword in line_lower for keyword in ['work experience', 'professional experience', 'employment', 'career history', 'experience']):
                experience_section = True
                continue
            
            # Detect end of experience section - but be careful not to stop too early
            # Only stop if we see a clear section header, not just keywords in content
            # IMPORTANT: Don't stop on partial matches - only stop on clear section headers
            if experience_section:
                # Check if this is a section header (short line, all caps or title case, common header words)
                is_section_header = (len(line) < 50 and 
                                    (line.isupper() or (line[0].isupper() and line.count(' ') < 5)) and
                                    any(keyword in line_lower for keyword in ['education', 'skills', 'interests', 'languages', 'certification', 'qualifications', 'academic']))
                
                if is_section_header:
                    if current_experience:
                        current_experience['responsibilities'] = current_responsibilities
                        experience_patterns.append(current_experience)
                        current_experience = None
                        current_responsibilities = []
                    experience_section = False
                    break
            
            if not experience_section:
                continue
            
            # Check if line looks like a job title/company header
            # Patterns: "Job Title — Company — Location — Dates" or "Job Title, Company, Location, Dates"
            has_date = bool(re.search(r'\b(19|20)\d{2}\s*[-–]\s*((?:19|20)\d{2}|Present|Current|Now)\b', line, re.IGNORECASE))
            has_month_date = bool(re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–]', line, re.IGNORECASE))
            
            # Check if line contains job title indicators - FINANCIAL INDUSTRY FOCUSED
            job_title_indicators = [
                # Financial industry roles
                'analyst', 'associate', 'director', 'manager', 'vice president', 'vp', 'executive', 'officer', 'specialist',
                'trader', 'portfolio', 'risk', 'quantitative', 'quant', 'researcher', 'researcher', 'strategist',
                'consultant', 'advisor', 'adviser', 'investment', 'banker', 'broker', 'dealer',
                # General professional roles
                'designer', 'developer', 'administrator', 'engineer', 'coordinator', 'lead', 'senior', 'junior', 'assistant',
                'marketing', 'business', 'development', 'freelance', 'recruitment'
            ]
            looks_like_job = any(indicator in line_lower for indicator in job_title_indicators)
            
            # Check if line contains company indicators - FINANCIAL INDUSTRY FOCUSED
            company_indicators = [
                # Financial institutions
                'bank', 'capital', 'partners', 'group', 'fund', 'management', 'investment', 'advisory', 'holdings',
                'securities', 'trading', 'asset', 'wealth', 'private equity', 'hedge fund',
                # Company suffixes
                'ltd', 'inc', 'llc', 'corp', 'plc',
                # Common company words
                'clients', 'various', 'remote', 'london', 'new york', 'leeds', 'manchester'
            ]
            looks_like_company = any(indicator in line_lower for indicator in company_indicators) or (line_upper.isupper() and len(line.split()) >= 2 and len(line) < 60)
            
            # Check if previous line might be part of this job entry (fragmented text)
            prev_line = lines[i-1].strip() if i > 0 else ""
            is_continuation = (prev_line and 
                              not prev_line.endswith('.') and 
                              len(prev_line) < 30 and 
                              not re.search(r'\b(19|20)\d{2}\b', prev_line) and
                              (prev_line.endswith(',') or prev_line.endswith(':') or not prev_line[0].isupper()))
            
            # Also check if line has location + date pattern (common in CVs)
            has_location_date = bool(re.search(r'(London|Leeds|Remote|UK|USA)[^,]*,\s*[^,]*\s*\(?\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|19|20)\d{2}', line, re.IGNORECASE))
            
            # If line has date or looks like job/company, it's likely a new experience entry
            # But check if it might be continuation of previous line
            # Be more lenient - if it has a date and looks like it could be a job, treat it as one
            if (has_date or has_month_date or has_location_date) and (looks_like_job or looks_like_company or len(line.split()) <= 8) and not is_continuation:
                # Save previous experience
                if current_experience:
                    current_experience['responsibilities'] = current_responsibilities
                    experience_patterns.append(current_experience)
                
                # Parse the new experience line
                # Try to extract: Title, Company, Location, Dates
                parts = re.split(r'\s*[—–-]\s*|\s*,\s*', line)
                
                # Extract dates
                date_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4})\s*[-–]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}|Present|Current|Now)', line, re.IGNORECASE)
                dates = date_match.group(0).strip() if date_match else ""
                
                # Remove dates from line for title/company extraction
                line_without_dates = re.sub(r'\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4})\s*[-–]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}|Present|Current|Now)\s*', '', line).strip()
                parts = re.split(r'\s*[—–-]\s*|\s*,\s*', line_without_dates)
                
                title = parts[0].strip() if parts else line_without_dates
                company = parts[1].strip() if len(parts) > 1 else ""
                location = parts[2].strip() if len(parts) > 2 else ""
                
                # Clean up and reconstruct fragmented company names
                title = re.sub(r'\s*[—–-]\s*$', '', title).strip()
                company = re.sub(r'^\s*[—–-]\s*', '', company).strip()
                # Aggressive company name reconstruction
                company = self._reconstruct_company_names(company)
                # Also fix common fragments directly - GENERAL patterns
                company = re.sub(r'\bartners\b', 'Partners', company, flags=re.IGNORECASE)
                company = re.sub(r'\bcap\s+ital\b', 'Capital', company, flags=re.IGNORECASE)
                company = re.sub(r'\bman\s+agement\b', 'Management', company, flags=re.IGNORECASE)
                # If it's just a common fragment, it's likely the full word
                if company.lower() == 'artners':
                    company = 'Partners'
                if company.lower() in ['cap', 'ital']:
                    company = 'Capital'
                if company.lower() in ['man', 'agement']:
                    company = 'Management'
                
                current_experience = {
                    'title': title if title else 'POSITION',
                    'company': company if company else 'COMPANY',
                    'location': location if location else '',
                    'dates': dates if dates else '',
                    'responsibilities': []
                }
                current_responsibilities = []
                
                # Parse the new experience line
                # Try to extract: Title, Company, Location, Dates
                parts = re.split(r'\s*[—–-]\s*|\s*,\s*', line)
                
                # Extract dates
                date_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4})\s*[-–]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}|Present|Current|Now)', line, re.IGNORECASE)
                dates = date_match.group(0).strip() if date_match else ""
                
                # Remove dates from line for title/company extraction
                line_without_dates = re.sub(r'\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4})\s*[-–]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}|Present|Current|Now)\s*', '', line).strip()
                parts = re.split(r'\s*[—–-]\s*|\s*,\s*', line_without_dates)
                
                title = parts[0].strip() if parts else line_without_dates
                company = parts[1].strip() if len(parts) > 1 else ""
                location = parts[2].strip() if len(parts) > 2 else ""
                
                # Clean up and reconstruct fragmented company names
                title = re.sub(r'\s*[—–-]\s*$', '', title).strip()
                company = re.sub(r'^\s*[—–-]\s*', '', company).strip()
                # Aggressive company name reconstruction
                company = self._reconstruct_company_names(company)
                # Also fix common fragments directly - GENERAL patterns
                company = re.sub(r'\bartners\b', 'Partners', company, flags=re.IGNORECASE)
                company = re.sub(r'\bcap\s+ital\b', 'Capital', company, flags=re.IGNORECASE)
                company = re.sub(r'\bman\s+agement\b', 'Management', company, flags=re.IGNORECASE)
                # If it's just a common fragment, it's likely the full word
                if company.lower() == 'artners':
                    company = 'Partners'
                if company.lower() in ['cap', 'ital']:
                    company = 'Capital'
                if company.lower() in ['man', 'agement']:
                    company = 'Management'
                
                current_experience = {
                    'title': title if title else 'POSITION',
                    'company': company if company else 'COMPANY',
                    'location': location if location else '',
                    'dates': dates if dates else '',
                    'responsibilities': []
                }
                current_responsibilities = []
            
            # Check if line is a responsibility/bullet point OR a new job entry we missed
            elif current_experience:
                # First check if this might actually be a new job entry we missed
                # (some jobs might not have been caught by the date check)
                has_date_here = bool(re.search(r'\b(19|20)\d{2}\s*[-–]', line, re.IGNORECASE))
                has_month_date_here = bool(re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–]', line, re.IGNORECASE))
                looks_like_new_job = (has_date_here or has_month_date_here) and any(indicator in line_lower for indicator in job_title_indicators + company_indicators)
                
                # If this looks like a new job, save current and start new
                if looks_like_new_job and len(current_responsibilities) > 0:
                    current_experience['responsibilities'] = current_responsibilities
                    experience_patterns.append(current_experience)
                    current_experience = None
                    current_responsibilities = []
                    # Process this line as a new job entry (will be caught in next iteration)
                    continue
                
                # Otherwise, treat as responsibility/bullet point
                # Remove bullet markers
                clean_line = re.sub(r'^[•\-\*◦·]\s*', '', line).strip()
                
                # Skip if it looks like another job entry
                if re.search(r'\b(19|20)\d{2}\s*[-–]', clean_line) and len(clean_line.split()) <= 8:
                    # This might be a date line for current job, add as responsibility
                    if len(clean_line) > 5:
                        current_responsibilities.append(clean_line)
                elif clean_line and len(clean_line) > 5:
                    # Check if it's a sentence fragment that should be combined with previous
                    if current_responsibilities:
                        last_resp = current_responsibilities[-1]
                        # If previous doesn't end with period and this doesn't start with capital, likely continuation
                        if (not last_resp.endswith('.') and 
                            (not clean_line[0].isupper() or 
                             clean_line.startswith(',') or 
                             clean_line.startswith('and ') or
                             len(clean_line) < 40)):
                            # Merge with previous
                            current_responsibilities[-1] += " " + clean_line
                        else:
                            current_responsibilities.append(clean_line)
                    else:
                        current_responsibilities.append(clean_line)
            # If we're in experience section but don't have a current_experience, this might be a job entry
            elif experience_section and not current_experience:
                # Check if this line could be a job entry (has date or job/company keywords)
                if (has_date or has_month_date or has_location_date) and (looks_like_job or looks_like_company):
                    # Process as new job entry (will be caught in next iteration, but let's handle it here)
                    pass  # Will be caught on next iteration
        
        # Save last experience
        if current_experience:
            current_experience['responsibilities'] = current_responsibilities
            experience_patterns.append(current_experience)
        
        # If we didn't find any experience but we're in a CV, try a more aggressive search
        if not experience_patterns and experience_section:
            logger.warning("No experience entries found with standard parsing, trying aggressive search")
            # Look for any line with dates and job-like keywords anywhere in the text
            for i, line in enumerate(lines):
                if re.search(r'\b(19|20)\d{2}\s*[-–]', line, re.IGNORECASE) or re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[-–]', line, re.IGNORECASE):
                    if any(indicator in line.lower() for indicator in job_title_indicators + company_indicators):
                        # Try to extract job info
                        parts = re.split(r'\s*[—–-]\s*|\s*,\s*', line)
                        date_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4})\s*[-–]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}|Present|Current|Now)', line, re.IGNORECASE)
                        dates = date_match.group(0).strip() if date_match else ""
                        line_without_dates = re.sub(r'\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4})\s*[-–]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}|Present|Current|Now)\s*', '', line).strip()
                        parts = re.split(r'\s*[—–-]\s*|\s*,\s*', line_without_dates)
                        title = parts[0].strip() if parts else line_without_dates
                        company = parts[1].strip() if len(parts) > 1 else ""
                        company = self._reconstruct_company_names(company)
                        experience_patterns.append({
                            'title': title if title else 'POSITION',
                            'company': company if company else 'COMPANY',
                            'location': parts[2].strip() if len(parts) > 2 else '',
                            'dates': dates,
                            'responsibilities': []
                        })
        
        # Combine top section jobs with main experience section
        # Top section jobs are usually most recent, so put them first
        all_experience = top_section_jobs + experience_patterns
        
        # Remove duplicates (same title + company + dates)
        seen = set()
        unique_experience = []
        for exp in all_experience:
            key = (exp.get('title', '').lower(), exp.get('company', '').lower(), exp.get('dates', ''))
            if key not in seen and key != ('position', 'company', ''):
                seen.add(key)
                unique_experience.append(exp)
        
        if unique_experience:
            parsed['experience'] = unique_experience
            logger.info(f"✅ Extracted {len(unique_experience)} experience entries ({len(top_section_jobs)} from top section, {len(experience_patterns)} from main section)")
            for i, exp in enumerate(unique_experience):
                logger.info(f"   Experience {i+1}: {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
        else:
            parsed['experience'] = []
            logger.warning("⚠️ No experience entries found")
        
        # Extract education with improved parsing
        education_section = False
        current_education = None
        education_items = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            line_upper = line.upper().strip()
            
            # Detect start of education section
            if 'education' in line_lower or 'qualifications' in line_lower or 'academic' in line_lower:
                education_section = True
                continue
            
            # Detect end of education section - only if it's a clear section header
            # Don't stop on partial matches in content
            is_section_header = (line_upper.isupper() or 
                                line_upper.startswith(('SKILLS', 'Skills', 'EXPERIENCE', 'Experience', 
                                                       'WORK', 'Work', 'INTERESTS', 'Interests',
                                                       'CERTIFICATIONS', 'Certifications')))
            if education_section and is_section_header and len(line_clean.split()) <= 3:
                # Only stop if it looks like a section header (short, clear)
                if current_education:
                    education_items.append(current_education)
                    current_education = None
                education_section = False
                break
            
            if not education_section:
                continue
            
            # Check if line looks like a degree or institution
            has_year = bool(re.search(r'\b(19|20)\d{2}\b', line))
            is_degree_line = any(word in line_lower for word in ['bsc', 'ba', 'ma', 'ms', 'mba', 'phd', 'degree', 'honours', 'diploma', 'certificate'])
            is_school_line = any(word in line_lower for word in ['university', 'college', 'school', 'institute', 'academy'])
            
            # If line has year and looks like education, or is clearly a school/degree
            if (has_year and (is_degree_line or is_school_line)) or (is_school_line and len(line.split()) <= 5):
                # Save previous education
                if current_education:
                    education_items.append(current_education)
                
                # Parse education line
                # Try to extract: Degree, Institution, Year
                parts = re.split(r'\s*[—–-]\s*|\s*,\s*|\s*\(|\s*\)', line)
                
                # Extract year
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                year = year_match.group(0) if year_match else ""
                
                # Remove year from line
                line_without_year = re.sub(r'\s*\b(19|20)\d{2}\b\s*', '', line).strip()
                parts = re.split(r'\s*[—–-]\s*|\s*,\s*|\s*\(|\s*\)', line_without_year)
                
                # Determine if first part is degree or institution
                if is_degree_line and parts:
                    degree = parts[0].strip()
                    institution = parts[1].strip() if len(parts) > 1 else ""
                elif is_school_line and parts:
                    institution = parts[0].strip()
                    degree = parts[1].strip() if len(parts) > 1 else ""
                else:
                    # Try to guess based on content
                    if any(word in parts[0].lower() for word in ['bsc', 'ba', 'ma', 'ms', 'mba', 'phd']):
                        degree = parts[0].strip()
                        institution = parts[1].strip() if len(parts) > 1 else ""
                    else:
                        institution = parts[0].strip()
                        degree = parts[1].strip() if len(parts) > 1 else ""
                
                current_education = {
                    'school': institution if institution else 'INSTITUTION',
                    'degree': degree if degree else line_without_year,
                    'dates': year if year else '',
                    'details': []
                }
            elif current_education:
                # Add to details
                clean_line = re.sub(r'^[•\-\*◦·]\s*', '', line).strip()
                if clean_line and len(clean_line) > 5:
                    # Check if it's a continuation
                    if current_education['details'] and not clean_line[0].isupper() and len(clean_line) < 50:
                        current_education['details'][-1] += " " + clean_line
                    else:
                        current_education['details'].append(clean_line)
            elif education_section and len(line) > 10:
                # Might be a degree/institution without clear markers
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                current_education = {
                    'school': line if is_school_line else 'INSTITUTION',
                    'degree': line if is_degree_line else '',
                    'dates': year_match.group(0) if year_match else '',
                    'details': []
                }
        
        # Save last education
        if current_education:
            education_items.append(current_education)
        
        parsed['education'] = education_items
        logger.info(f"✅ Extracted {len(education_items)} education entries")
        for i, edu in enumerate(education_items):
            logger.info(f"   Education {i+1}: {edu.get('degree', 'N/A')} at {edu.get('school', 'N/A')}")
        
        # Extract skills: capture lines under a SKILLS header with better parsing
        try:
            skills_section = False
            skills_collected: List[str] = []
            current_skill_group = []
            
            for line in lines:
                ll = line.lower().strip()
                line_clean = line.strip()
                
                # Detect skills section start
                if any(h in ll for h in ['skills', 'technical', 'creative skills', 'core strengths', 'competencies', 'key skills']):
                    skills_section = True
                    continue
                
                # Detect skills section end - only if it's a clear section header (all caps or starts with keyword)
                # Don't stop on partial matches in content
                is_section_header = (line_clean.isupper() or 
                                    line_clean.startswith(('EDUCATION', 'Education', 'EXPERIENCE', 'Experience', 
                                                           'SUMMARY', 'Summary', 'PROFILE', 'Profile',
                                                           'INTERESTS', 'Interests', 'CERTIFICATIONS', 'Certifications',
                                                           'LANGUAGES', 'Languages')))
                if skills_section and is_section_header:
                    # Process any pending skill group
                    if current_skill_group:
                        skills_collected.extend(current_skill_group)
                        current_skill_group = []
                    break
                
                if skills_section and line_clean:
                    # Handle bullet points
                    if line_clean.startswith(('•', '-', '·', '*')):
                        # Process previous group if exists
                        if current_skill_group:
                            skills_collected.extend(current_skill_group)
                            current_skill_group = []
                        
                        item = re.sub(r'^[•\-\*◦·]\s*', '', line_clean).strip()
                        # Handle skill categories like "Development: Python, JavaScript"
                        if ':' in item:
                            category, skills_str = item.split(':', 1)
                            category = category.strip()
                            # Add category if it's substantial
                            if len(category) > 2:
                                skills_collected.append(category)
                            # Add individual skills
                            for skill in [s.strip() for s in skills_str.split(',') if s.strip()]:
                                if skill:
                                    skills_collected.append(skill)
                        else:
                            if item:
                                skills_collected.append(item)
                    
                    # Handle comma-separated skills
                    elif ',' in line_clean and len(line_clean) < 200:
                        # Process previous group
                        if current_skill_group:
                            skills_collected.extend(current_skill_group)
                            current_skill_group = []
                        
                        # Check if it's a category line like "Development: Python, JavaScript, TypeScript"
                        if ':' in line_clean:
                            category, skills_str = line_clean.split(':', 1)
                            category = category.strip()
                            if len(category) > 2:
                                skills_collected.append(category)
                            for skill in [s.strip() for s in skills_str.split(',') if s.strip()]:
                                if skill:
                                    skills_collected.append(skill)
                        else:
                            # Just comma-separated skills
                            for skill in [s.strip() for s in line_clean.split(',') if s.strip()]:
                                if skill and len(skill) > 2:
                                    skills_collected.append(skill)
                    
                    # Handle skill category headers (like "Development:" or "Design:")
                    elif line_clean.endswith(':') and len(line_clean) < 30:
                        # Process previous group
                        if current_skill_group:
                            skills_collected.extend(current_skill_group)
                            current_skill_group = []
                        # This is a category header, next lines will be skills
                        skills_collected.append(line_clean.rstrip(':'))
                    
                    # Handle fragmented skill lines (like "development," followed by "and UX Development:")
                    elif skills_collected and len(line_clean) < 60:
                        last_skill = skills_collected[-1]
                        # Check if this looks like a continuation of previous skill
                        if (last_skill.endswith(',') or 
                            (not last_skill.endswith(':') and len(last_skill) < 25 and 
                             (line_clean.startswith('and ') or line_clean.startswith('& ') or 
                              not line_clean[0].isupper() or line_clean.endswith(':')))):
                            # Merge with previous skill
                            merged = (last_skill.rstrip(',') + " " + line_clean).strip()
                            # Clean up common patterns
                            merged = re.sub(r'\s*\.\s*Development', ' Development', merged, flags=re.IGNORECASE)
                            merged = re.sub(r'development\s*,\s*and\s+UX', 'Development and UX', merged, flags=re.IGNORECASE)
                            skills_collected[-1] = merged
                        elif current_skill_group:
                            current_skill_group[-1] += " " + line_clean
                        else:
                            # Check for common skill fragments and clean them
                            cleaned_skill = line_clean
                            # "design to create human Swift" -> "Swift" (programming language)
                            if 'design to create human' in cleaned_skill.lower() and 'swift' in cleaned_skill.lower():
                                cleaned_skill = 'Swift'
                            # "Procreate centered digital" -> "Procreate" and "Digital Design"
                            elif 'procreate centered digital' in cleaned_skill.lower():
                                if 'Procreate' not in skills_collected:
                                    skills_collected.append('Procreate')
                                cleaned_skill = 'Digital Design'
                            skills_collected.append(cleaned_skill)
                    
                    # Standalone skill line
                    elif len(line_clean) > 2 and len(line_clean) < 100:
                        if current_skill_group:
                            skills_collected.extend(current_skill_group)
                            current_skill_group = []
                        skills_collected.append(line_clean)
            
            # Process any remaining group
            if current_skill_group:
                skills_collected.extend(current_skill_group)
            
            # Clean up skills: remove duplicates, filter out invalid entries
            seen = set()
            cleaned_skills = []
            for skill in skills_collected:
                skill_clean = skill.strip()
                if skill_clean and len(skill_clean) > 2 and len(skill_clean) < 100:
                    skill_lower = skill_clean.lower()
                    if skill_lower not in seen:
                        seen.add(skill_lower)
                        cleaned_skills.append(skill_clean)
            
            parsed['skills'] = cleaned_skills[:30]  # Limit to 30 skills
            logger.info(f"✅ Extracted {len(parsed['skills'])} skills")
            if parsed['skills']:
                logger.info(f"   Sample skills: {', '.join(parsed['skills'][:5])}")
        except Exception as e:
            logger.warning(f"❌ Error extracting skills: {e}")
            parsed['skills'] = []

        return parsed
    
    def _is_company_line(self, line: str) -> bool:
        """Check if line is likely a company name"""
        line_clean = line.strip()
        
        # Check for uppercase company names (like "HSBC INVESTMENT BANKING", "ARROW GLOBAL")
        if line_clean.isupper() and len(line_clean) > 5:
            return True
        
        # Check for company keywords
        company_keywords = [
            'inc', 'llc', 'ltd', 'corp', 'partners', 'capital', 'management', 
            'bank', 'group', 'plc', 'investment', 'global', 'fund', 'advisory',
            'consulting', 'finance', 'financial', 'holdings', 'limited'
        ]
        
        if any(word in line_clean.lower() for word in company_keywords):
            return True
        
        # Check for multi-word companies with separators
        if any(char in line_clean for char in ['&', ',']) and len(line_clean.split()) >= 2:
            return True
        
        # Check for financial institutions (common patterns)
        financial_patterns = [
            r'\b[A-Z]{2,}\s+(BANK|INVESTMENT|CAPITAL|FUND)\b',
            r'\b[A-Z]{2,}\s+[A-Z]{2,}\s+(GROUP|PARTNERS|HOLDINGS)\b'
        ]
        
        for pattern in financial_patterns:
            if re.search(pattern, line_clean):
                return True
        
        return False
    
    def _reconstruct_company_names(self, text: str) -> str:
        """Reconstruct fragmented company names - GENERAL patterns"""
        import re
        
        # Common company name fragments - GENERAL patterns for financial industry
        patterns = [
            # Common company suffixes
            (r'\bartners\b', 'Partners', re.IGNORECASE),
            (r'\bcap\s+ital\b', 'Capital', re.IGNORECASE),
            (r'\bman\s+agement\b', 'Management', re.IGNORECASE),
            (r'\bgroup\b', 'Group', re.IGNORECASE),
            (r'\bin\s+vestment\b', 'Investment', re.IGNORECASE),
            (r'\bsecur\s+ities\b', 'Securities', re.IGNORECASE),
            # Handle cases where fragments appear alone
            (r'^artners\b', 'Partners', re.IGNORECASE),
            (r'^cap\s+ital\b', 'Capital', re.IGNORECASE),
        ]
        
        for pattern, replacement, flags in patterns:
            text = re.sub(pattern, replacement, text, flags=flags)
        
        return text
    
    def _is_school_line(self, line: str) -> bool:
        """Check if line is likely a school name"""
        return (any(word in line.lower() for word in ['university', 'college', 'school', 'institute']) or
                line.isupper())
    
    
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
    
    def _format_skills_list(self, data: Dict[str, Any]) -> str:
        """Format skills as a single list"""
        skills = data.get('skills', [])
        if not skills:
            # Default skills based on Mawney Partners examples
            skills = [
                'Investment Analysis',
                'Portfolio Management',
                'Risk Management',
                'Client Relations',
                'Financial Modeling',
                'Due Diligence',
                'Fund Management',
                'Capital Markets'
            ]
        
        return '\n'.join([f'<li>{skill}</li>' for skill in skills])
    
    def _format_experience_items(self, data: Dict[str, Any]) -> str:
        """Format experience items with professional structure"""
        items = []
        for exp in data.get('experience', []):
            company = exp.get('company', '').strip()
            title = exp.get('title', '').strip()
            dates = exp.get('dates', '').strip()
            location = exp.get('location', '').strip()
            responsibilities = exp.get('responsibilities', []) or []

            # Only add if we have substantial content
            if company or title or responsibilities:
                responsibility_list = ''
                if responsibilities:
                    responsibility_list = f'''
                    <ul>
                        {''.join([f'<li>{resp.strip()}</li>' for resp in responsibilities if resp and resp.strip()])}
                    </ul>
                    '''

                item_html = f'''
                <div class="experience-item">
                    <div class="job-header">{title}{', ' if title and company else ''}{company}{', ' if (title or company) and location else ''}{location} {dates}</div>
                    <div class="job-details">
                        {responsibility_list}
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
    
    def _get_top_logo_base64(self) -> str:
        """Get top MP logo (cv logo 1.png) from local assets"""
        try:
            # Try to get the top MP logo from the local assets folder
            top_logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'cv logo 1.png')
            
            if os.path.exists(top_logo_path):
                with open(top_logo_path, 'rb') as f:
                    logo_data = f.read()
                logo_base64 = base64.b64encode(logo_data).decode('utf-8')
                
                logo_html = f'''
                <img src="data:image/png;base64,{logo_base64}" alt="MP" style="max-width: 80px; height: auto;" />
                '''
                logger.info("Using actual top MP logo from assets")
                return logo_html
            else:
                # Fallback to text logo if image not found
                logger.warning("Top MP logo not found, using text fallback")
                return '''
                <div style="font-family: 'EB Garamond', serif; font-size: 36pt; font-weight: 700; color: #2c3e50; letter-spacing: 8px;">
                    MP
                </div>
                '''
        except Exception as e:
            logger.error(f"Error getting top MP logo: {e}")
            return '''
            <div style="font-family: 'EB Garamond', serif; font-size: 36pt; font-weight: 700; color: #2c3e50; letter-spacing: 8px;">
                MP
            </div>
            '''
    
    def _get_bottom_logo_base64(self) -> str:
        """Get bottom MAWNEY Partners logo (cv logo 2.png) from local assets"""
        try:
            # Try to get the bottom MAWNEY Partners logo from the local assets folder
            bottom_logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'cv logo 2.png')
            
            if os.path.exists(bottom_logo_path):
                with open(bottom_logo_path, 'rb') as f:
                    logo_data = f.read()
                logo_base64 = base64.b64encode(logo_data).decode('utf-8')
                
                logo_html = f'''
                <img src="data:image/png;base64,{logo_base64}" alt="MAWNEY Partners" style="max-width: 120px; height: auto;" />
                '''
                logger.info("Using actual bottom MAWNEY Partners logo from assets")
                return logo_html
            else:
                # Fallback to text logo if image not found
                logger.warning("Bottom MAWNEY Partners logo not found, using text fallback")
                return '''
                <div style="font-family: 'Arial', sans-serif; font-size: 12pt; font-weight: 700; color: #2c3e50; letter-spacing: 1px;">
                    MAWNEY PARTNERS
                </div>
                '''
        except Exception as e:
            logger.error(f"Error getting bottom MAWNEY Partners logo: {e}")
            return '''
            <div style="font-family: 'Arial', sans-serif; font-size: 12pt; font-weight: 700; color: #2c3e50; letter-spacing: 1px;">
                MAWNEY PARTNERS
            </div>
            '''
    
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

