# app/services/document_service.py

from typing import Dict, BinaryIO
import logging

logger = logging.getLogger("nexus")


class DocumentService:
    def __init__(self):
        from app.core.config import get_settings
        self.settings = get_settings()
        self.allowed_extensions = {'.pdf', '.docx', '.txt'}
    
    def validate_file(self, filename: str, file_size: int) -> None:
        """Validate file type and size"""
        from app.core.exceptions import FileValidationError
        
        ext = '.' + filename.lower().split('.')[-1] if '.' in filename else ''
        if ext not in self.allowed_extensions:
            raise FileValidationError(
                f"Invalid file type: {ext}. "
                f"Allowed: {self.allowed_extensions}"
            )
        
        max_bytes = self.settings.max_file_size_mb * 1024 * 1024
        if file_size > max_bytes:
            raise FileValidationError(
                f"File too large: {file_size} bytes. "
                f"Max: {max_bytes} bytes"
            )
    
    def parse_pdf(self, file: BinaryIO) -> Dict:
        """Extract text and metadata from PDF"""
        from app.core.exceptions import DocumentParsingError
        
        try:
            from pypdf import PdfReader
            reader = PdfReader(file)
            pages = []
            
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    pages.append({
                        'page_number': page_num,
                        'content': text
                    })
            
            return {
                'total_pages': len(reader.pages),
                'pages': pages
            }
        except Exception as e:
            logger.error(f"PDF parsing failed: {str(e)}")
            raise DocumentParsingError(f"PDF parsing failed: {str(e)}")
    
    def parse_docx(self, file: BinaryIO) -> Dict:
        """Extract text from DOCX"""
        from app.core.exceptions import DocumentParsingError
        
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(file)
            paragraphs = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
            
            return {
                'total_paragraphs': len(paragraphs),
                'content': '\n\n'.join(paragraphs)
            }
        except Exception as e:
            logger.error(f"DOCX parsing failed: {str(e)}")
            raise DocumentParsingError(f"DOCX parsing failed: {str(e)}")
    
    def parse_txt(self, file: BinaryIO) -> Dict:
        """Extract text from TXT"""
        from app.core.exceptions import DocumentParsingError
        
        try:
            content = file.read().decode('utf-8')
            return {'content': content}
        except Exception as e:
            logger.error(f"TXT parsing failed: {str(e)}")
            raise DocumentParsingError(f"TXT parsing failed: {str(e)}")
    
    def parse_document(self, filename: str, file: BinaryIO) -> Dict:
        """Route to appropriate parser based on file type"""
        from app.core.exceptions import FileValidationError
        
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        parsers = {
            'pdf': self.parse_pdf,
            'docx': self.parse_docx,
            'txt': self.parse_txt
        }
        
        parser = parsers.get(ext)
        if not parser:
            raise FileValidationError(f"No parser for {ext}")
        
        return parser(file)
