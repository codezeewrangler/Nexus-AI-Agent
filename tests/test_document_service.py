# tests/test_document_service.py

import pytest
from io import BytesIO
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_file_validation_valid_pdf():
    """Test validation passes for valid PDF"""
    from app.services.document_service import DocumentService
    
    service = DocumentService()
    # Should not raise any exception
    service.validate_file("test.pdf", 1000)


def test_file_validation_valid_docx():
    """Test validation passes for valid DOCX"""
    from app.services.document_service import DocumentService
    
    service = DocumentService()
    # Should not raise any exception
    service.validate_file("document.docx", 5000)


def test_file_validation_valid_txt():
    """Test validation passes for valid TXT"""
    from app.services.document_service import DocumentService
    
    service = DocumentService()
    # Should not raise any exception
    service.validate_file("notes.txt", 2000)


def test_file_validation_invalid_type():
    """Test validation fails for invalid file type"""
    from app.services.document_service import DocumentService
    from app.core.exceptions import FileValidationError
    
    service = DocumentService()
    with pytest.raises(FileValidationError):
        service.validate_file("malware.exe", 1000)


def test_file_validation_too_large():
    """Test validation fails for oversized file"""
    from app.services.document_service import DocumentService
    from app.core.exceptions import FileValidationError
    
    service = DocumentService()
    with pytest.raises(FileValidationError):
        service.validate_file("huge.pdf", 100 * 1024 * 1024)  # 100MB


def test_txt_parsing():
    """Test TXT file parsing"""
    from app.services.document_service import DocumentService
    
    service = DocumentService()
    file = BytesIO(b"This is test content for parsing.")
    
    result = service.parse_txt(file)
    
    assert 'content' in result
    assert result['content'] == "This is test content for parsing."


def test_txt_parsing_unicode():
    """Test TXT file parsing with unicode content"""
    from app.services.document_service import DocumentService
    
    service = DocumentService()
    file = BytesIO("Hello 世界 🌍".encode('utf-8'))
    
    result = service.parse_txt(file)
    
    assert 'content' in result
    assert "世界" in result['content']
    assert "🌍" in result['content']


def test_parse_document_routing_txt():
    """Test that parse_document routes to correct parser for TXT"""
    from app.services.document_service import DocumentService
    
    service = DocumentService()
    file = BytesIO(b"Sample text file content.")
    
    result = service.parse_document("sample.txt", file)
    
    assert 'content' in result
    assert result['content'] == "Sample text file content."


def test_parse_document_invalid_extension():
    """Test parse_document fails for unsupported file type"""
    from app.services.document_service import DocumentService
    from app.core.exceptions import FileValidationError
    
    service = DocumentService()
    file = BytesIO(b"some content")
    
    with pytest.raises(FileValidationError):
        service.parse_document("file.xyz", file)
