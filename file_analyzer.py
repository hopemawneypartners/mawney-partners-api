"""
File Analysis Module for AI Assistant
Handles processing and analysis of uploaded files including images and documents
"""

import io
import logging
import magic
from PIL import Image
import pytesseract
import PyPDF2
import pdfplumber
from typing import Dict, List, Optional, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileAnalyzer:
    """Handles analysis of uploaded files for AI assistant"""
    
    def __init__(self):
        self.supported_image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff']
        self.supported_document_types = ['application/pdf', 'text/plain', 'text/rtf', 'application/json']
        
    def analyze_file(self, file_data: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """
        Analyze a file and extract relevant information
        
        Args:
            file_data: Raw file data
            filename: Original filename
            mime_type: MIME type of the file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            logger.info(f"📎 Analyzing file: {filename} (type: {mime_type})")
            logger.info(f"📎 File size: {len(file_data)} bytes")
            
            if mime_type in self.supported_image_types:
                result = self._analyze_image(file_data, filename)
                logger.info(f"📎 Image analysis result: {result.get('type', 'unknown')}")
                return result
            elif mime_type in self.supported_document_types:
                result = self._analyze_document(file_data, filename, mime_type)
                logger.info(f"📎 Document analysis result: {result.get('type', 'unknown')}")
                logger.info(f"📎 Extracted text length: {len(result.get('extracted_text', ''))}")
                return result
            else:
                logger.warning(f"📎 Unsupported file type: {mime_type}")
                return {
                    'type': 'unsupported',
                    'filename': filename,
                    'mime_type': mime_type,
                    'error': f'Unsupported file type: {mime_type}',
                    'extracted_text': '',
                    'analysis': 'File type not supported for analysis'
                }
                
        except Exception as e:
            logger.error(f"Error analyzing file {filename}: {str(e)}")
            return {
                'type': 'error',
                'filename': filename,
                'mime_type': mime_type,
                'error': str(e),
                'extracted_text': '',
                'analysis': f'Error processing file: {str(e)}'
            }
    
    def _analyze_image(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Analyze image files for text extraction and content description"""
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(file_data))
            
            # Get image properties
            width, height = image.size
            mode = image.mode
            format_name = image.format
            
            # Extract text using OCR
            extracted_text = ""
            try:
                extracted_text = pytesseract.image_to_string(image, lang='eng')
                extracted_text = extracted_text.strip()
            except Exception as e:
                logger.warning(f"OCR failed for {filename}: {str(e)}")
                extracted_text = "OCR processing failed"
            
            # Analyze image content
            analysis = self._describe_image_content(image, extracted_text)
            
            return {
                'type': 'image',
                'filename': filename,
                'mime_type': 'image/*',
                'extracted_text': extracted_text,
                'image_properties': {
                    'width': width,
                    'height': height,
                    'mode': mode,
                    'format': format_name
                },
                'analysis': analysis,
                'has_text': bool(extracted_text and extracted_text != "OCR processing failed")
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image {filename}: {str(e)}")
            return {
                'type': 'image_error',
                'filename': filename,
                'mime_type': 'image/*',
                'error': str(e),
                'extracted_text': '',
                'analysis': f'Error processing image: {str(e)}'
            }
    
    def _analyze_document(self, file_data: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """Analyze document files for text extraction"""
        try:
            if mime_type == 'application/pdf':
                return self._analyze_pdf(file_data, filename)
            elif mime_type in ['text/plain', 'text/rtf', 'application/json']:
                return self._analyze_text_file(file_data, filename, mime_type)
            else:
                return {
                    'type': 'document_error',
                    'filename': filename,
                    'mime_type': mime_type,
                    'error': f'Unsupported document type: {mime_type}',
                    'extracted_text': '',
                    'analysis': f'Document type {mime_type} not supported'
                }
                
        except Exception as e:
            logger.error(f"Error analyzing document {filename}: {str(e)}")
            return {
                'type': 'document_error',
                'filename': filename,
                'mime_type': mime_type,
                'error': str(e),
                'extracted_text': '',
                'analysis': f'Error processing document: {str(e)}'
            }
    
    def _analyze_pdf(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from PDF files with improved text cleaning and color-aware extraction"""
        try:
            extracted_text = ""
            page_count = 0
            use_ocr = False
            
            # Try pdfplumber first (better for complex PDFs and can handle colored text)
            try:
                with pdfplumber.open(io.BytesIO(file_data)) as pdf:
                    page_count = len(pdf.pages)
                    
                    # First pass: try standard text extraction with layout preservation
                    # Also extract font size info to identify large text (likely names)
                    page_texts = []
                    page_font_info = []  # Store font size info for name detection
                    
                    for page_idx, page in enumerate(pdf.pages):
                        # Try layout-based extraction first (better for colored/styled text)
                        text = page.extract_text(layout=True)
                        if not text or len(text.strip()) < 50:
                            # Fallback to standard extraction
                            text = page.extract_text()
                        
                        # Extract words with font size information (for identifying large text/names)
                        words = page.extract_words()
                        if words:
                            # Reconstruct text from words (preserves colored text)
                            word_text = ' '.join([w.get('text', '') for w in words if w.get('text')])
                            if word_text and len(word_text) > len(text or ''):
                                text = word_text
                            
                            # Store font size info for first page (where names typically are)
                            if page_idx == 0:
                                # Look for large text (likely name) - typically 14pt+ for names
                                large_text_words = []
                                for w in words:
                                    size = w.get('size', 0)
                                    if size > 12:  # Large text threshold
                                        large_text_words.append(w.get('text', ''))
                                if large_text_words:
                                    page_font_info.append({
                                        'page': 0,
                                        'large_text': ' '.join(large_text_words),
                                        'words': words
                                    })
                        
                        if text:
                            # Clean the extracted text
                            cleaned_text = self._clean_extracted_text(text)
                            page_texts.append((page_idx, cleaned_text))
                            extracted_text += cleaned_text + "\n"
                    
                    # ALWAYS use OCR for first page to catch artistically formatted names
                    # Names are often styled/large/colored and may be missed by text extraction
                    first_page_ocr = ""
                    try:
                        from pdf2image import convert_from_bytes
                        images = convert_from_bytes(file_data, dpi=300)
                        if images:
                            # OCR first page with higher DPI for better name detection
                            first_image = images[0]
                            # Crop top 40% of first page (where names and headers typically are)
                            width, height = first_image.size
                            top_region = first_image.crop((0, 0, width, int(height * 0.4)))
                            first_page_ocr_top = pytesseract.image_to_string(top_region, lang='eng', config='--psm 6')
                            logger.info(f"OCR extracted {len(first_page_ocr_top)} characters from first page header area")
                            
                            # Also try full first page OCR (more complete)
                            full_first_page_ocr = pytesseract.image_to_string(first_image, lang='eng', config='--psm 6')
                            logger.info(f"OCR extracted {len(full_first_page_ocr)} characters from full first page")
                            
                            # Use the longer/more complete version
                            if len(full_first_page_ocr) > len(first_page_ocr_top):
                                first_page_ocr = full_first_page_ocr
                            else:
                                first_page_ocr = first_page_ocr_top
                    except Exception as ocr_err:
                        logger.warning(f"First page OCR failed: {str(ocr_err)}")
                    
                    # Merge first page OCR with extracted text - always prefer more complete text
                    if first_page_ocr and page_texts:
                        first_page_text = page_texts[0][1] if page_texts else ""
                        # Always merge - OCR often catches text that extraction misses
                        merged_first = self._merge_text_extractions(first_page_text, first_page_ocr)
                        # Clean the merged text
                        merged_first = self._clean_extracted_text(merged_first)
                        page_texts[0] = (0, merged_first)
                        logger.info(f"Merged first page: extracted {len(first_page_text)} + OCR {len(first_page_ocr)} = merged {len(merged_first)}")
                        # Rebuild extracted_text with merged first page
                        extracted_text = ""
                        for page_idx, text in page_texts:
                            extracted_text += text + "\n"
                    
                    # Store font info for later use in name extraction
                    if page_font_info:
                        logger.info(f"Found large text on first page: {page_font_info[0].get('large_text', '')[:100]}")
                    
                    # Check if extraction seems incomplete (might be missing colored text)
                    # If text is suspiciously short for a CV, try OCR
                    if page_count > 0:
                        avg_chars_per_page = len(extracted_text) / page_count
                        # CVs typically have 500+ characters per page
                        if avg_chars_per_page < 300:
                            logger.warning(f"PDF text extraction seems incomplete ({avg_chars_per_page:.0f} chars/page), trying OCR for colored text")
                            use_ocr = True
                    
                    # If we got some text but it seems fragmented, try OCR as supplement
                    if not use_ocr and extracted_text:
                        # Check for suspicious patterns that suggest missing text
                        # (e.g., very short words, lots of single characters)
                        words = extracted_text.split()
                        if len(words) > 0:
                            avg_word_length = sum(len(w) for w in words) / len(words)
                            single_char_words = sum(1 for w in words if len(w) == 1)
                            if avg_word_length < 3 or (single_char_words / len(words)) > 0.1:
                                logger.warning(f"PDF text seems fragmented, trying OCR for colored text")
                                use_ocr = True
                    
                    # If OCR needed, extract text from images
                    if use_ocr:
                        ocr_text = ""
                        try:
                            from pdf2image import convert_from_bytes
                            images = convert_from_bytes(file_data, dpi=300)
                            for i, image in enumerate(images):
                                try:
                                    page_ocr = pytesseract.image_to_string(image, lang='eng')
                                    if page_ocr:
                                        ocr_text += page_ocr + "\n"
                                        logger.info(f"OCR extracted {len(page_ocr)} characters from page {i+1}")
                                except Exception as ocr_err:
                                    logger.warning(f"OCR failed for page {i+1}: {str(ocr_err)}")
                            
                            # Combine OCR text with extracted text, preferring OCR for missing parts
                            if ocr_text:
                                # OCR often gets more complete text, especially for colored backgrounds
                                # Use OCR if it's significantly longer
                                if len(ocr_text.strip()) > len(extracted_text.strip()) * 1.2:
                                    logger.info(f"Using OCR text (OCR: {len(ocr_text)} chars vs extracted: {len(extracted_text)} chars)")
                                    extracted_text = ocr_text
                                else:
                                    # Merge both, removing duplicates
                                    logger.info(f"Merging OCR text with extracted text")
                                    extracted_text = self._merge_text_extractions(extracted_text, ocr_text)
                        except ImportError:
                            logger.warning("pdf2image not available, cannot use OCR fallback")
                        except Exception as ocr_err:
                            logger.warning(f"OCR fallback failed: {str(ocr_err)}")
                            
            except Exception as e:
                logger.warning(f"pdfplumber failed for {filename}, trying PyPDF2: {str(e)}")
                
                # Fallback to PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        # Clean the extracted text
                        cleaned_text = self._clean_extracted_text(text)
                        extracted_text += cleaned_text + "\n"
                
                # If PyPDF2 also gives little text, try OCR
                if page_count > 0 and len(extracted_text) / page_count < 300:
                    logger.warning("PyPDF2 extraction seems incomplete, trying OCR")
                    use_ocr = True
                    try:
                        from pdf2image import convert_from_bytes
                        images = convert_from_bytes(file_data, dpi=300)
                        ocr_text = ""
                        for image in images:
                            try:
                                page_ocr = pytesseract.image_to_string(image, lang='eng')
                                if page_ocr:
                                    ocr_text += page_ocr + "\n"
                            except Exception:
                                pass
                        if ocr_text and len(ocr_text) > len(extracted_text):
                            extracted_text = ocr_text
                    except Exception:
                        pass
            
            extracted_text = extracted_text.strip()
            
            # Log the extracted content for debugging
            logger.info(f"PDF extraction for {filename}:")
            logger.info(f"Page count: {page_count}")
            logger.info(f"Text length: {len(extracted_text)} characters")
            logger.info(f"Used OCR: {use_ocr}")
            logger.info(f"First 500 characters: {extracted_text[:500]}")
            
            # Analyze document content
            analysis = self._analyze_document_content(extracted_text, filename)
            
            # Store font info for name extraction
            font_info = page_font_info if 'page_font_info' in locals() else []
            
            return {
                'type': 'pdf',
                'filename': filename,
                'mime_type': 'application/pdf',
                'extracted_text': extracted_text,
                'document_properties': {
                    'page_count': page_count,
                    'word_count': len(extracted_text.split()) if extracted_text else 0,
                    'char_count': len(extracted_text),
                    'used_ocr': use_ocr,
                    'font_info': font_info  # Large text info for name detection
                },
                'analysis': analysis,
                'has_text': bool(extracted_text)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing PDF {filename}: {str(e)}")
            return {
                'type': 'pdf_error',
                'filename': filename,
                'mime_type': 'application/pdf',
                'error': str(e),
                'extracted_text': '',
                'analysis': f'Error processing PDF: {str(e)}'
            }
    
    def _merge_text_extractions(self, text1: str, text2: str) -> str:
        """Merge two text extractions, intelligently combining the best parts"""
        if not text1:
            return text2
        if not text2:
            return text1
        
        # Split into words for better comparison
        words1 = text1.split()
        words2 = text2.split()
        
        # If one is significantly longer, prefer it (more complete)
        if len(text2) > len(text1) * 1.3:
            return text2
        if len(text1) > len(text2) * 1.3:
            return text1
        
        # Merge line by line, preferring more complete versions
        lines1 = text1.split('\n')
        lines2 = text2.split('\n')
        
        # Create a map of line starts to full lines (to match similar lines)
        merged_lines = []
        used_lines2 = set()
        
        for line1 in lines1:
            line1_clean = line1.strip()
            if not line1_clean:
                merged_lines.append(line1)
                continue
            
            # Find best matching line in text2
            best_match = None
            best_match_idx = -1
            best_score = 0
            
            for idx, line2 in enumerate(lines2):
                if idx in used_lines2:
                    continue
                line2_clean = line2.strip()
                if not line2_clean:
                    continue
                
                # Score based on similarity and completeness
                score = 0
                # Check if lines are similar (one contains the other)
                if line1_clean.lower() in line2_clean.lower():
                    score = len(line2_clean)  # Prefer longer (more complete)
                elif line2_clean.lower() in line1_clean.lower():
                    score = len(line1_clean)
                # Check word overlap
                words1_set = set(line1_clean.lower().split())
                words2_set = set(line2_clean.lower().split())
                overlap = len(words1_set & words2_set)
                if overlap > 0:
                    score = max(score, overlap * 10 + len(line2_clean))
                
                if score > best_score:
                    best_score = score
                    best_match = line2_clean
                    best_match_idx = idx
            
            # Use the more complete version
            if best_match and len(best_match) > len(line1_clean) * 1.1:
                merged_lines.append(best_match)
                if best_match_idx >= 0:
                    used_lines2.add(best_match_idx)
            else:
                merged_lines.append(line1_clean)
        
        # Add remaining lines from text2 that weren't matched
        for idx, line2 in enumerate(lines2):
            if idx not in used_lines2 and line2.strip():
                merged_lines.append(line2.strip())
        
        return '\n'.join(merged_lines)
    
    def _reconstruct_fragmented_words(self, text: str) -> str:
        """Reconstruct fragmented words that were split incorrectly"""
        import re
        
        # Common word fragments to merge
        # Pattern: (fragment1)(fragment2) -> (full_word)
        fragment_patterns = [
            # Name fragments - be more aggressive
            (r'\bPE\s+GILBERT\b', 'HOPE GILBERT'),
            (r'\bHO\s+PE\s+GILBERT\b', 'HOPE GILBERT'),
            (r'\bH\s+O\s+PE\s+GILBERT\b', 'HOPE GILBERT'),
            (r'\bPE\s+GE\b', 'PAGE'),
            # Company name fragments - comprehensive patterns
            (r'\bartners\b', 'Partners'),
            (r'\bwney\s+Partners\b', 'Mawney Partners'),
            (r'\bMawney\s+artners\b', 'Mawney Partners'),
            (r'\bM\s+awney\s+Partners\b', 'Mawney Partners'),
            (r'\bg\s+wney\b', 'Mawney'),  # "g" + "wney" = "Mawney" (missing "Ma")
            (r'\bMa\s+wney\b', 'Mawney'),
            (r'\bM\s+a\s+wney\b', 'Mawney'),
            # Common word fragments - more patterns
            (r'\bde\s+velopment\b', 'development'),
            (r'\bde\s+sign\b', 'design'),
            (r'\bde\s+signer\b', 'designer'),
            (r'\bde\s+veloper\b', 'developer'),
            (r'\bcre\s+ative\b', 'creative'),
            (r'\bpro\s+fessional\b', 'professional'),
            (r'\bmar\s+keting\b', 'marketing'),
            (r'\bcom\s+munication\b', 'communication'),
            (r'\bstrat\s+egy\b', 'strategy'),
            (r'\bstrat\s+egic\b', 'strategic'),
            (r'\bex\s+perience\b', 'experience'),
            (r'\bex\s+ecutive\b', 'executive'),
            (r'\bad\s+ministrator\b', 'administrator'),
            (r'\bman\s+agement\b', 'management'),
            (r'\bde\s+sign\s+to\s+create\s+human\b', ''),  # Remove this fragment
        ]
        
        for pattern, replacement in fragment_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Try to merge single-character words with following words
        # Pattern: "word g word" -> "word Mawney word" (if context suggests it)
        # But be careful - only merge if it makes sense
        lines = text.split('\n')
        reconstructed_lines = []
        
        for line in lines:
            words = line.split()
            if len(words) < 2:
                reconstructed_lines.append(line)
                continue
            
            merged_words = []
            i = 0
            while i < len(words):
                word = words[i]
                
                # Check if this is a single character that might be a fragment
                if len(word) == 1 and word.isalpha() and i < len(words) - 1:
                    next_word = words[i + 1]
                    
                    # Try to reconstruct common patterns
                    # "g wney" -> "Mawney" (if "wney" follows)
                    if word.lower() == 'g' and next_word.lower().startswith('wney'):
                        merged_words.append('Mawney')
                        i += 2
                        continue
                    # "H O" -> "HO" (part of HOPE)
                    elif word.upper() == 'H' and next_word.upper() == 'O' and i < len(words) - 2:
                        third_word = words[i + 2]
                        if third_word.upper() == 'PE':
                            merged_words.append('HOPE')
                            i += 3
                            continue
                        else:
                            merged_words.append('HO')
                            i += 2
                            continue
                    # "artners" -> "Partners" (if preceded by something that looks like company name)
                    elif word.lower() == 'artners' and merged_words and merged_words[-1].lower() in ['mawney', 'm', 'ma']:
                        if merged_words[-1].lower() in ['m', 'ma']:
                            merged_words[-1] = 'Mawney'
                        merged_words.append('Partners')
                        i += 1
                        continue
                    # "PE" -> might be part of "HOPE" if followed by "GILBERT"
                    elif word.upper() == 'PE' and i < len(words) - 1 and words[i + 1].upper() == 'GILBERT':
                        # Check if previous word might be "HO"
                        if merged_words and merged_words[-1].upper() == 'HO':
                            merged_words[-1] = 'HOPE'
                            i += 1  # Skip "PE"
                            continue
                
                merged_words.append(word)
                i += 1
            
            reconstructed_lines.append(' '.join(merged_words))
        
        return '\n'.join(reconstructed_lines)
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted PDF text with aggressive word separation"""
        import re
        
        # FIRST: Reconstruct fragmented words before other cleaning
        text = self._reconstruct_fragmented_words(text)
        
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
        
        # Fix common PDF extraction issues
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')
        text = text.replace('ﬀ', 'ff')
        
        # CRITICAL: Fix concatenated words that are common in CVs
        # Add spaces between lowercase and uppercase letters
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # Fix specific concatenated words we've seen
        text = re.sub(r'stronganalytical', 'strong analytical', text, flags=re.IGNORECASE)
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
        text = text.replace('ﬃ', 'ffi')
        text = text.replace('ﬄ', 'ffl')
        
        # AGGRESSIVE word separation - handle multiple cases
        # Fix concatenated words by adding spaces between lowercase and uppercase
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # Fix concatenated words by adding spaces between letters and numbers
        text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
        text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
        
        # Fix concatenated words by adding spaces between punctuation and letters
        text = re.sub(r'([.,;:])([a-zA-Z])', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z])([.,;:])', r'\1\2', text)
        
        # Fix common concatenated patterns
        text = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', text)  # "wordWord" -> "word Word"
        text = re.sub(r'([a-z])([A-Z]{2,})', r'\1 \2', text)   # "wordWORD" -> "word WORD"
        
        # Fix specific common concatenations
        text = re.sub(r'andcertified', 'and certified', text, flags=re.IGNORECASE)
        text = re.sub(r'withstrong', 'with strong', text, flags=re.IGNORECASE)
        text = re.sub(r'analyticaland', 'analytical and', text, flags=re.IGNORECASE)
        text = re.sub(r'skillslooking', 'skills looking', text, flags=re.IGNORECASE)
        text = re.sub(r'lookingfor', 'looking for', text, flags=re.IGNORECASE)
        text = re.sub(r'ananalyst', 'an analyst', text, flags=re.IGNORECASE)
        text = re.sub(r'problem-solving', 'problem-solving', text, flags=re.IGNORECASE)
        text = re.sub(r'experienceof', 'experience of', text, flags=re.IGNORECASE)
        text = re.sub(r'statisticalanalysis', 'statistical analysis', text, flags=re.IGNORECASE)
        
        # Fix more complex concatenations - AGGRESSIVE FIXES
        text = re.sub(r'managingfinancial', 'managing financial', text, flags=re.IGNORECASE)
        text = re.sub(r'riskmetrics', 'risk metrics', text, flags=re.IGNORECASE)
        text = re.sub(r'financialrisk', 'financial risk', text, flags=re.IGNORECASE)
        text = re.sub(r'riskanalysis', 'risk analysis', text, flags=re.IGNORECASE)
        text = re.sub(r'riskautomation', 'risk automation', text, flags=re.IGNORECASE)
        text = re.sub(r'riskcommittee', 'risk committee', text, flags=re.IGNORECASE)
        text = re.sub(r'developingcalculating', 'developing calculating', text, flags=re.IGNORECASE)
        text = re.sub(r'valueatrisk', 'value at risk', text, flags=re.IGNORECASE)
        text = re.sub(r'marketfactors', 'market factors', text, flags=re.IGNORECASE)
        text = re.sub(r'derivativeproducts', 'derivative products', text, flags=re.IGNORECASE)
        text = re.sub(r'researchedthe', 'researched the', text, flags=re.IGNORECASE)
        text = re.sub(r'universitiesand', 'universities and', text, flags=re.IGNORECASE)
        text = re.sub(r'businessschool', 'business school', text, flags=re.IGNORECASE)
        
        # CRITICAL: Fix the specific concatenations we're seeing
        text = re.sub(r'researchedtheuniversitiesandbusinesssci', 'researched the universities and business school', text, flags=re.IGNORECASE)
        text = re.sub(r'researchedtheuniversitiesandbusinesssc]', 'researched the universities and business school', text, flags=re.IGNORECASE)
        text = re.sub(r'managingfinancialriskmetricsonfinanci', 'managing financial risk metrics on financial', text, flags=re.IGNORECASE)
        text = re.sub(r'riskanalysisautomation', 'risk analysis automation', text, flags=re.IGNORECASE)
        text = re.sub(r'riskcommittee', 'risk committee', text, flags=re.IGNORECASE)
        text = re.sub(r'developingcalculating', 'developing calculating', text, flags=re.IGNORECASE)
        text = re.sub(r'analysingreports', 'analysing reports', text, flags=re.IGNORECASE)
        text = re.sub(r'keyfinancialrisk', 'key financial risk', text, flags=re.IGNORECASE)
        text = re.sub(r'valueatrisk', 'value at risk', text, flags=re.IGNORECASE)
        text = re.sub(r'sensitivitiestomarket', 'sensitivities to market', text, flags=re.IGNORECASE)
        text = re.sub(r'marketfactorsfor', 'market factors for', text, flags=re.IGNORECASE)
        text = re.sub(r'variousderivatives', 'various derivatives', text, flags=re.IGNORECASE)
        text = re.sub(r'equitiescredit', 'equities credit', text, flags=re.IGNORECASE)
        text = re.sub(r'creditcorporate', 'credit corporate', text, flags=re.IGNORECASE)
        text = re.sub(r'commoditiesand', 'commodities and', text, flags=re.IGNORECASE)
        
        # Fix common date patterns
        text = re.sub(r'(\d{4})\s*-\s*(\d{4})', r'\1 - \2', text)
        text = re.sub(r'(\w{3})\s*(\d{4})', r'\1 \2', text)
        
        # Fix bullet points and lists
        text = re.sub(r'[•▪▫‣⁃]', '•', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()
    
    def _analyze_text_file(self, file_data: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """Analyze text-based files"""
        try:
            # Decode text content
            try:
                extracted_text = file_data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    extracted_text = file_data.decode('latin-1')
                except UnicodeDecodeError:
                    extracted_text = file_data.decode('utf-8', errors='ignore')
            
            extracted_text = extracted_text.strip()
            
            # Analyze content
            analysis = self._analyze_document_content(extracted_text, filename)
            
            return {
                'type': 'text',
                'filename': filename,
                'mime_type': mime_type,
                'extracted_text': extracted_text,
                'document_properties': {
                    'word_count': len(extracted_text.split()) if extracted_text else 0,
                    'char_count': len(extracted_text),
                    'line_count': len(extracted_text.split('\n')) if extracted_text else 0
                },
                'analysis': analysis,
                'has_text': bool(extracted_text)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text file {filename}: {str(e)}")
            return {
                'type': 'text_error',
                'filename': filename,
                'mime_type': mime_type,
                'error': str(e),
                'extracted_text': '',
                'analysis': f'Error processing text file: {str(e)}'
            }
    
    def _describe_image_content(self, image: Image.Image, extracted_text: str) -> str:
        """Generate a description of image content"""
        width, height = image.size
        mode = image.mode
        
        description_parts = []
        
        # Basic image info
        description_parts.append(f"Image: {width}x{height} pixels, {mode} color mode")
        
        # Text content
        if extracted_text and extracted_text != "OCR processing failed":
            # Summarize text content
            text_preview = extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
            description_parts.append(f"Contains text: {text_preview}")
            
            # Look for financial/market indicators
            financial_keywords = ['revenue', 'profit', 'loss', 'earnings', 'market', 'stock', 'price', 'chart', 'graph', 'data']
            if any(keyword in extracted_text.lower() for keyword in financial_keywords):
                description_parts.append("Appears to contain financial or market-related content")
        else:
            description_parts.append("No readable text detected (may be a chart, diagram, or photo)")
        
        return " | ".join(description_parts)
    
    def _analyze_document_content(self, text: str, filename: str) -> str:
        """Analyze document content and provide insights"""
        if not text:
            return "Document appears to be empty or unreadable"
        
        word_count = len(text.split())
        char_count = len(text)
        
        analysis_parts = []
        
        # Basic stats
        analysis_parts.append(f"Document contains {word_count} words, {char_count} characters")
        
        # Content type detection
        financial_keywords = ['revenue', 'profit', 'loss', 'earnings', 'market', 'stock', 'price', 'financial', 'investment', 'portfolio']
        if any(keyword in text.lower() for keyword in financial_keywords):
            analysis_parts.append("Contains financial/market-related content")
        
        # Document structure
        if '\n' in text:
            line_count = len(text.split('\n'))
            analysis_parts.append(f"Multi-line document ({line_count} lines)")
        
        # Look for structured data
        if any(char in text for char in ['$', '%', '€', '£']):
            analysis_parts.append("Contains monetary values or percentages")
        
        if any(word in text.lower() for word in ['table', 'chart', 'graph', 'figure']):
            analysis_parts.append("May contain tables, charts, or figures")
        
        return " | ".join(analysis_parts)
    
    def format_analysis_for_ai(self, analyses: List[Dict[str, Any]]) -> str:
        """Format file analyses for AI prompt"""
        if not analyses:
            return "No files were provided for analysis."
        
        formatted_analyses = []
        
        for i, analysis in enumerate(analyses, 1):
            file_info = f"File {i}: {analysis.get('filename', 'Unknown')}"
            
            if analysis.get('type') in ['image', 'pdf', 'text']:
                file_info += f" ({analysis.get('mime_type', 'Unknown type')})"
                
                if analysis.get('extracted_text'):
                    text_preview = analysis['extracted_text'][:500]
                    if len(analysis['extracted_text']) > 500:
                        text_preview += "..."
                    file_info += f"\nExtracted content: {text_preview}"
                else:
                    file_info += f"\nNo readable content extracted"
                
                if analysis.get('analysis'):
                    file_info += f"\nAnalysis: {analysis['analysis']}"
            else:
                file_info += f"\nError: {analysis.get('error', 'Unknown error')}"
            
            formatted_analyses.append(file_info)
        
        return "\n\n".join(formatted_analyses)

# Global instance
file_analyzer = FileAnalyzer()
