from typing import List, Dict
import os
import pypdf
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
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
                
            # Split the text into chunks
            chunks = []
            for page in pages:
                if not page.page_content.strip():
                    print(f"Warning: Empty content on page {page.metadata.get('page', 'unknown')}")
                    continue
                    
                page_chunks = self.text_splitter.split_text(page.page_content)
                print(f"Created {len(page_chunks)} chunks from page {page.metadata.get('page', 'unknown')}")
                
                for chunk in page_chunks:
                    chunks.append({
                        'text': chunk,
                        'metadata': {'page': page.metadata['page']}
                    })
            
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
                    chunks = []
                    
                    for page_num in range(len(pdf.pages)):
                        text = pdf.pages[page_num].extract_text()
                        if not text.strip():
                            print(f"Warning: Empty content on page {page_num + 1}")
                            continue
                            
                        page_chunks = self.text_splitter.split_text(text)
                        print(f"Created {len(page_chunks)} chunks from page {page_num + 1}")
                        
                        for chunk in page_chunks:
                            chunks.append({
                                'text': chunk,
                                'metadata': {'page': page_num + 1}
                            })
                    
                    if not chunks:
                        raise ValueError("No text chunks created from PDF")
                        
                    print(f"Created total of {len(chunks)} chunks from direct pypdf method")
                    print(f"First chunk preview: {chunks[0]['text'][:200]}...")
                    return chunks
                    
            except Exception as e2:
                error_msg = f"Failed to process PDF with both methods.\nPyPDFLoader error: {str(e)}\npypdf error: {str(e2)}"
                print(error_msg)
                raise Exception(error_msg)
