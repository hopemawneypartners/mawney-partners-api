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
        """Extract text from PDF files with improved text cleaning"""
        try:
            extracted_text = ""
            page_count = 0
            
            # Try pdfplumber first (better for complex PDFs)
            try:
                with pdfplumber.open(io.BytesIO(file_data)) as pdf:
                    page_count = len(pdf.pages)
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            # Clean the extracted text
                            cleaned_text = self._clean_extracted_text(text)
                            extracted_text += cleaned_text + "\n"
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
            
            extracted_text = extracted_text.strip()
            
            # Log the extracted content for debugging
            logger.info(f"PDF extraction for {filename}:")
            logger.info(f"Page count: {page_count}")
            logger.info(f"Text length: {len(extracted_text)} characters")
            logger.info(f"First 500 characters: {extracted_text[:500]}")
            
            # Analyze document content
            analysis = self._analyze_document_content(extracted_text, filename)
            
            return {
                'type': 'pdf',
                'filename': filename,
                'mime_type': 'application/pdf',
                'extracted_text': extracted_text,
                'document_properties': {
                    'page_count': page_count,
                    'word_count': len(extracted_text.split()) if extracted_text else 0,
                    'char_count': len(extracted_text)
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
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted PDF text with aggressive word separation"""
        import re
        
        # CRITICAL: Preserve line breaks for CV structure!
        # Only replace multiple spaces/tabs on the same line
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
        
        # Fix common PDF extraction issues
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')
        text = text.replace('ﬀ', 'ff')
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
        
        # Fix more complex concatenations
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
