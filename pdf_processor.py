from typing import List, Dict
import os
import pypdf
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    def __init__(self):
        # Adjust text splitter settings for more lenient chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Smaller chunks
            chunk_overlap=50,  # Less overlap
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]  # More granular separators
        )
    
    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Process a PDF file and return chunks of text with metadata.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            List[Dict]: List of text chunks with metadata
        """
        print(f"Processing PDF at: {os.path.abspath(pdf_path)}")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")
            
        print(f"PDF file exists, size: {os.path.getsize(pdf_path)} bytes")
        
        try:
            print("Attempting to use PyPDFLoader...")
            # Try using PyPDFLoader from langchain
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            print(f"Successfully loaded {len(pages)} pages with PyPDFLoader")
            
            if not pages:
                raise ValueError("No pages extracted from PDF")
            
            # Debug: Print raw content from first few pages
            for i, page in enumerate(pages[:2]):
                print(f"\nPage {i+1} preview (first 200 chars):")
                print(page.page_content[:200])
                
            # Split the text into chunks
            chunks = []
            for page in pages:
                if not page.page_content.strip():
                    print(f"Warning: Empty content on page {page.metadata.get('page', 'unknown')}")
                    continue
                
                # Debug: Print content length
                content = page.page_content.strip()
                print(f"Page {page.metadata.get('page', 'unknown')} content length: {len(content)} chars")
                
                try:
                    page_chunks = self.text_splitter.split_text(content)
                    print(f"Created {len(page_chunks)} chunks from page {page.metadata.get('page', 'unknown')}")
                    
                    for chunk in page_chunks:
                        if chunk.strip():  # Only add non-empty chunks
                            chunks.append({
                                'text': chunk,
                                'metadata': {'page': page.metadata['page']}
                            })
                except Exception as chunk_error:
                    print(f"Error splitting page {page.metadata.get('page', 'unknown')}: {str(chunk_error)}")
            
            if not chunks:
                raise ValueError("No text chunks created from PDF")
                
            print(f"Created total of {len(chunks)} chunks from PyPDFLoader method")
            print(f"First chunk preview: {chunks[0]['text'][:200]}...")
            return chunks
            
        except Exception as e:
            print(f"Error with PyPDFLoader: {str(e)}")
            print("Trying alternative PDF processing method...")
            
            # Fallback to direct pypdf usage
            try:
                print("Attempting to use pypdf directly...")
                with open(pdf_path, 'rb') as file:
                    pdf = pypdf.PdfReader(file)
                    print(f"Successfully opened PDF with {len(pdf.pages)} pages")
                    
                    # Debug: Print raw content from first few pages
                    for i in range(min(2, len(pdf.pages))):
                        print(f"\nPage {i+1} preview (first 200 chars):")
                        print(pdf.pages[i].extract_text()[:200])
                    
                    chunks = []
                    for page_num in range(len(pdf.pages)):
                        text = pdf.pages[page_num].extract_text()
                        if not text.strip():
                            print(f"Warning: Empty content on page {page_num + 1}")
                            continue
                        
                        # Debug: Print content length
                        content = text.strip()
                        print(f"Page {page_num + 1} content length: {len(content)} chars")
                        
                        try:
                            page_chunks = self.text_splitter.split_text(content)
                            print(f"Created {len(page_chunks)} chunks from page {page_num + 1}")
                            
                            for chunk in page_chunks:
                                if chunk.strip():  # Only add non-empty chunks
                                    chunks.append({
                                        'text': chunk,
                                        'metadata': {'page': page_num + 1}
                                    })
                        except Exception as chunk_error:
                            print(f"Error splitting page {page_num + 1}: {str(chunk_error)}")
                    
                    if not chunks:
                        raise ValueError("No text chunks created from PDF")
                        
                    print(f"Created total of {len(chunks)} chunks from direct pypdf method")
                    print(f"First chunk preview: {chunks[0]['text'][:200]}...")
                    return chunks
                    
            except Exception as e2:
                error_msg = f"Failed to process PDF with both methods.\nPyPDFLoader error: {str(e)}\npypdf error: {str(e2)}"
                print(error_msg)
                raise Exception(error_msg)
