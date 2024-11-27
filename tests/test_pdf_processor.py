"""
Tests for the PDF processor module.
"""
import pytest
from io import BytesIO
from src.pdf_processor import PDFProcessor

def test_clean_text():
    """Test text cleaning functionality."""
    processor = PDFProcessor()
    
    # Test removing extra whitespace
    text = "This   has    extra   spaces"
    assert processor.clean_text(text) == "This has extra spaces"
    
    # Test normalizing newlines
    text = "Line1\r\nLine2\r\nLine3"
    assert processor.clean_text(text) == "Line1 Line2 Line3"
    
    # Test removing null characters
    text = "Text with\x00null\x00chars"
    assert processor.clean_text(text) == "Text with null chars"

def test_create_chunks():
    """Test text chunking functionality."""
    processor = PDFProcessor()
    
    # Test basic chunking
    text = "This is a test. This is another test. And a final test."
    chunks = processor.create_chunks(text, chunk_size=20, overlap=5)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, tuple) for chunk in chunks)
    assert all(len(chunk) == 2 for chunk in chunks)  # (text, metadata)
    assert all(isinstance(chunk[1], dict) for chunk in chunks)  # metadata is dict

def test_chunk_metadata():
    """Test chunk metadata creation."""
    processor = PDFProcessor()
    
    text = "Short test text."
    chunks = processor.create_chunks(text, chunk_size=20, overlap=5)
    
    assert len(chunks) == 1
    chunk_text, metadata = chunks[0]
    
    assert "start_char" in metadata
    assert "end_char" in metadata
    assert "chunk_size" in metadata
    assert metadata["chunk_size"] == len(chunk_text)

def test_empty_text():
    """Test handling of empty text."""
    processor = PDFProcessor()
    
    chunks = processor.create_chunks("")
    assert len(chunks) == 0

def test_chunk_overlap():
    """Test chunk overlap functionality."""
    processor = PDFProcessor()
    
    text = "This is a long text that should be split into multiple chunks with overlap."
    chunks = processor.create_chunks(text, chunk_size=20, overlap=5)
    
    # Check that chunks overlap
    if len(chunks) > 1:
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i][0]
            next_chunk = chunks[i + 1][0]
            
            # There should be some overlap between consecutive chunks
            assert any(word in next_chunk for word in current_chunk.split()[-3:])
