"""
PDF processing module for extracting and chunking text from PDF documents.
"""
import logging
from typing import List, Tuple
import PyPDF2
from io import BytesIO

from app.config import MAX_CHUNK_SIZE, OVERLAP_SIZE

logger = logging.getLogger('pdf')

class PDFProcessor:
    """Handles PDF document processing and text chunking."""
    
    @staticmethod
    def extract_text(pdf_file: BytesIO) -> str:
        """Extract text content from a PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            logger.info(f"Successfully extracted text from PDF ({len(text)} characters)")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    @staticmethod
    def create_chunks(text: str, chunk_size: int = MAX_CHUNK_SIZE, 
                     overlap: int = OVERLAP_SIZE) -> List[Tuple[str, dict]]:
        """Split text into overlapping chunks with metadata."""
        try:
            chunks = []
            start = 0
            
            while start < len(text):
                # Find the end of the chunk
                end = start + chunk_size
                
                # If we're not at the end of the text, try to find a good break point
                if end < len(text):
                    # Try to find the last period or newline in the chunk
                    last_period = text.rfind('.', start, end)
                    last_newline = text.rfind('\n', start, end)
                    break_point = max(last_period, last_newline)
                    
                    if break_point > start:
                        end = break_point + 1
                
                # Create chunk with metadata
                chunk_text = text[start:end].strip()
                if chunk_text:  # Only add non-empty chunks
                    metadata = {
                        "start_char": start,
                        "end_char": end,
                        "chunk_size": len(chunk_text)
                    }
                    chunks.append((chunk_text, metadata))
                
                # Move the start position, accounting for overlap
                start = end - overlap if end < len(text) else len(text)
            
            logger.info(f"Created {len(chunks)} chunks from text")
            return chunks
            
        except Exception as e:
            logger.error(f"Error creating chunks: {str(e)}")
            raise
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text."""
        try:
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            # Remove special characters that might cause issues
            text = text.replace('\x00', '')
            
            # Normalize newlines
            text = text.replace('\r\n', '\n')
            
            logger.info("Text cleaned successfully")
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            raise
    
    def process_pdf(self, pdf_file: BytesIO) -> List[Tuple[str, dict]]:
        """Process PDF file and return chunks with metadata."""
        try:
            # Extract text from PDF
            raw_text = self.extract_text(pdf_file)
            
            # Clean the extracted text
            cleaned_text = self.clean_text(raw_text)
            
            # Create chunks
            chunks = self.create_chunks(cleaned_text)
            
            logger.info(f"PDF processed successfully: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
