"""
CV File Generator for Mawney Partners
Generates downloadable CV files in various formats (HTML, PDF, DOCX)
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

class CVFileGenerator:
    """Generates downloadable CV files in various formats"""
    
    def __init__(self, output_dir: str = "generated_cvs"):
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def generate_html_file(self, html_content: str, filename: str = None) -> Dict[str, Any]:
        """
        Generate HTML file from CV content
        
        Args:
            html_content: HTML CV content
            filename: Optional custom filename
            
        Returns:
            Dictionary with file info and download URL
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cv_formatted_{timestamp}.html"
            
            # Sanitize filename - remove spaces and special characters
            import re
            filename = re.sub(r'[^\w\-_.]', '_', filename)
            filename = filename.replace(' ', '_').replace('(', '').replace(')', '')
            
            # Ensure .html extension
            if not filename.endswith('.html'):
                filename += '.html'
            
            # Full file path
            filepath = os.path.join(self.output_dir, filename)
            
            # Write HTML file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated HTML CV file: {filepath}")
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "file_size": file_size,
                "format": "html",
                "download_url": f"/api/download-cv/{filename}",
                "message": "CV file generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error generating HTML file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_pdf_file(self, html_content: str, filename: str = None) -> Dict[str, Any]:
        """
        Generate PDF file from HTML CV content
        
        Args:
            html_content: HTML CV content
            filename: Optional custom filename
            
        Returns:
            Dictionary with file info and download URL
        """
        try:
            # Try to use pdfkit/wkhtmltopdf if available
            try:
                import pdfkit
                
                # Generate filename if not provided
                if not filename:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"cv_formatted_{timestamp}.pdf"
                
                # Sanitize filename - remove spaces and special characters
                import re
                filename = re.sub(r'[^\w\-_.]', '_', filename)
                filename = filename.replace(' ', '_').replace('(', '').replace(')', '')
                
                # Ensure .pdf extension
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
                
                # Full file path
                filepath = os.path.join(self.output_dir, filename)
                
                # Configure pdfkit options
                options = {
                    'page-size': 'A4',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                    'encoding': "UTF-8",
                    'no-outline': None,
                    'enable-local-file-access': None
                }
                
                # Generate PDF
                pdfkit.from_string(html_content, filepath, options=options)
                
                logger.info(f"Generated PDF CV file: {filepath}")
                
                # Get file size
                file_size = os.path.getsize(filepath)
                
                return {
                    "success": True,
                    "filename": filename,
                    "filepath": filepath,
                    "file_size": file_size,
                    "format": "pdf",
                    "download_url": f"/api/download-cv/{filename}",
                    "message": "CV PDF generated successfully"
                }
                
            except ImportError:
                # Fallback: Generate HTML file instead
                logger.warning("pdfkit not available, generating HTML file instead")
                return self.generate_html_file(html_content, filename.replace('.pdf', '.html') if filename else None)
            
        except Exception as e:
            logger.error(f"Error generating PDF file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_file_as_base64(self, filepath: str) -> Optional[str]:
        """
        Read file and return as base64 encoded string
        
        Args:
            filepath: Path to file
            
        Returns:
            Base64 encoded file content
        """
        try:
            with open(filepath, 'rb') as f:
                file_content = f.read()
                return base64.b64encode(file_content).decode('utf-8')
        except Exception as e:
            logger.error(f"Error reading file as base64: {e}")
            return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old generated CV files
        
        Args:
            max_age_hours: Maximum age of files to keep (default 24 hours)
        """
        try:
            current_time = datetime.now()
            deleted_count = 0
            
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                
                # Skip directories and non-CV files
                if os.path.isdir(filepath):
                    continue
                
                # Check file age
                file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                age_hours = (current_time - file_modified).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    os.remove(filepath)
                    deleted_count += 1
                    logger.info(f"Deleted old CV file: {filename}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old CV files")
                
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")

# Global instance
cv_file_generator = CVFileGenerator()

