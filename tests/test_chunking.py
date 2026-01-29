# tests/test_chunking.py

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockSettings:
    chunk_size = 100
    chunk_overlap = 20


# Mock the get_settings function
def mock_get_settings():
    return MockSettings()


def test_basic_chunking():
    """Test basic text chunking functionality"""
    from app.utils.chunking import TextChunker
    
    chunker = TextChunker()
    chunker.chunk_size = 100
    chunker.overlap = 20
    
    text = "This is sentence one. This is sentence two. This is sentence three. This is sentence four."
    
    chunks = chunker.create_chunks(text)
    
    assert len(chunks) > 0
    assert all('content' in chunk for chunk in chunks)
    assert all('metadata' in chunk for chunk in chunks)


def test_metadata_preservation():
    """Test that metadata is preserved in chunks"""
    from app.utils.chunking import TextChunker
    
    chunker = TextChunker()
    text = "Test text content."
    metadata = {'page_number': 5}
    
    chunks = chunker.create_chunks(text, metadata)
    
    assert chunks[0]['metadata']['page_number'] == 5


def test_empty_text():
    """Test chunking with empty text"""
    from app.utils.chunking import TextChunker
    
    chunker = TextChunker()
    text = ""
    
    chunks = chunker.create_chunks(text)
    
    assert len(chunks) == 0


def test_chunk_document_with_pages():
    """Test chunking document with pages (PDF-like structure)"""
    from app.utils.chunking import TextChunker
    
    chunker = TextChunker()
    chunker.chunk_size = 1000
    
    document_data = {
        'total_pages': 2,
        'pages': [
            {'page_number': 1, 'content': 'Content from page one.'},
            {'page_number': 2, 'content': 'Content from page two.'}
        ]
    }
    
    chunks = chunker.chunk_document(document_data)
    
    assert len(chunks) >= 2
    assert all('chunk_id' in chunk for chunk in chunks)


def test_chunk_document_without_pages():
    """Test chunking document without pages (TXT-like structure)"""
    from app.utils.chunking import TextChunker
    
    chunker = TextChunker()
    chunker.chunk_size = 1000
    
    document_data = {
        'content': 'This is plain text content without page structure.'
    }
    
    chunks = chunker.chunk_document(document_data)
    
    assert len(chunks) >= 1
    assert all('chunk_id' in chunk for chunk in chunks)
