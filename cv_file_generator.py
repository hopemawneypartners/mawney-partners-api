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
        else:
            logger.info(f"Output directory already exists: {self.output_dir}")
        
        # Debug: List contents of directory
        try:
            files = os.listdir(self.output_dir)
            logger.info(f"Directory contents: {files}")
        except Exception as e:
            logger.error(f"Error listing directory contents: {e}")
    
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
            logger.info(f"HTML content length: {len(html_content)} characters")
            
            # Verify file was written
            if os.path.exists(filepath):
                actual_size = os.path.getsize(filepath)
                logger.info(f"File verified - actual size: {actual_size} bytes")
            else:
                logger.error(f"File was not created: {filepath}")
            
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
            # Helper to sanitize and create file path
            import re
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cv_formatted_{timestamp}.pdf"
            filename = re.sub(r'[^\w\-_.]', '_', filename).replace(' ', '_').replace('(', '').replace(')', '')
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            filepath = os.path.join(self.output_dir, filename)

            # Try PDF generation methods in order, prioritize pure Python solutions for Render
            pdf_generated = False
            last_error = None
            
            # 1) Try xhtml2pdf FIRST (pure Python, no system dependencies, most reliable on Render)
            try:
                from xhtml2pdf import pisa
                with open(filepath, 'wb') as pdf_file:
                    pisa_status = pisa.CreatePDF(src=html_content, dest=pdf_file)
                if pisa_status.err:
                    raise RuntimeError(f"xhtml2pdf failed: {pisa_status.err}")
                if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                    raise RuntimeError("xhtml2pdf created file but it's empty or missing")
                logger.info(f"✅ Generated PDF via xhtml2pdf: {filepath} ({os.path.getsize(filepath)} bytes)")
                pdf_generated = True
            except ImportError:
                logger.info("xhtml2pdf not available, trying WeasyPrint...")
                last_error = "xhtml2pdf not installed"
            except Exception as e_xhtml2pdf:
                logger.warning(f"xhtml2pdf failed: {type(e_xhtml2pdf).__name__}: {e_xhtml2pdf}")
                last_error = f"xhtml2pdf failed: {str(e_xhtml2pdf)}"
            
            # 2) Try WeasyPrint (may need system dependencies on Render)
            if not pdf_generated:
                try:
                    from weasyprint import HTML
                    HTML(string=html_content).write_pdf(filepath)
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                        logger.info(f"✅ Generated PDF via WeasyPrint: {filepath} ({os.path.getsize(filepath)} bytes)")
                        pdf_generated = True
                    else:
                        raise RuntimeError("WeasyPrint created file but it's empty or missing")
                except ImportError:
                    logger.info("WeasyPrint not available, trying pdfkit...")
                    if not last_error:
                        last_error = "WeasyPrint not installed"
                except Exception as e_weasy:
                    logger.warning(f"WeasyPrint failed: {type(e_weasy).__name__}: {e_weasy}")
                    last_error = f"WeasyPrint failed: {str(e_weasy)}"
            
            # 3) Try pdfkit / wkhtmltopdf (requires system binary, least likely to work on Render)
            if not pdf_generated:
                try:
                    import pdfkit
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
                    pdfkit.from_string(html_content, filepath, options=options)
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                        logger.info(f"✅ Generated PDF via pdfkit: {filepath} ({os.path.getsize(filepath)} bytes)")
                        pdf_generated = True
                except ImportError:
                    logger.info("pdfkit not available")
                    if not last_error:
                        last_error = "pdfkit not installed"
                except Exception as e_pdfkit:
                    logger.warning(f"pdfkit failed: {type(e_pdfkit).__name__}: {e_pdfkit}")
                    if not last_error:
                        last_error = f"pdfkit failed: {str(e_pdfkit)}"
            
            # If all methods failed, raise an error
            if not pdf_generated:
                error_msg = f"All PDF generation methods failed. Last error: {last_error}"
                logger.error(f"❌ {error_msg}")
                raise RuntimeError(error_msg)

            # At this point, a PDF should exist
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
            
        except Exception as e:
            logger.error(f"❌ All PDF generation methods failed: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "format": "pdf",
                "error": f"PDF generation failed: {str(e)}",
                "error_type": type(e).__name__
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

