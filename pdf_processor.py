from typing import List, Dict
import os
import subprocess
import tempfile
import pypdf
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    def extract_text_with_pdftotext(self, pdf_path: str) -> str:
        """Use pdftotext (from poppler-utils) to extract text."""
        try:
            result = subprocess.run(
                ['pdftotext', pdf_path, '-'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except Exception as e:
            print(f"pdftotext extraction failed: {str(e)}")
            return ""

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
            
        file_size = os.path.getsize(pdf_path)
        print(f"PDF file exists, size: {file_size} bytes")
        
        if file_size < 1000:  # Less than 1KB
            raise ValueError(f"PDF file seems too small ({file_size} bytes). Might be corrupted or a pointer file.")
        
        # Try all three methods
        methods = [
            ("PyPDFLoader", self._try_pypdf_loader),
            ("pypdf", self._try_pypdf_direct),
            ("pdftotext", self._try_pdftotext)
        ]
        
        last_error = None
        for method_name, method in methods:
            try:
                print(f"\nTrying {method_name} method...")
                chunks = method(pdf_path)
                if chunks:
                    print(f"Successfully extracted {len(chunks)} chunks using {method_name}")
                    return chunks
            except Exception as e:
                print(f"Error with {method_name}: {str(e)}")
                last_error = e
        
        raise Exception(f"All PDF processing methods failed. Last error: {str(last_error)}")
    
    def _try_pypdf_loader(self, pdf_path: str) -> List[Dict]:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        print(f"Loaded {len(pages)} pages")
        
        chunks = []
        for page in pages:
            content = page.page_content.strip()
            if content:
                page_chunks = self.text_splitter.split_text(content)
                for chunk in page_chunks:
                    if chunk.strip():
                        chunks.append({
                            'text': chunk,
                            'metadata': {'page': page.metadata['page']}
                        })
        return chunks
    
    def _try_pypdf_direct(self, pdf_path: str) -> List[Dict]:
        with open(pdf_path, 'rb') as file:
            pdf = pypdf.PdfReader(file)
            print(f"Opened PDF with {len(pdf.pages)} pages")
            
            chunks = []
            for page_num in range(len(pdf.pages)):
                content = pdf.pages[page_num].extract_text().strip()
                if content:
                    page_chunks = self.text_splitter.split_text(content)
                    for chunk in page_chunks:
                        if chunk.strip():
                            chunks.append({
                                'text': chunk,
                                'metadata': {'page': page_num + 1}
                            })
            return chunks
    
    def _try_pdftotext(self, pdf_path: str) -> List[Dict]:
        text = self.extract_text_with_pdftotext(pdf_path)
        if not text.strip():
            return []
            
        chunks = []
        page_chunks = self.text_splitter.split_text(text)
        for i, chunk in enumerate(page_chunks):
            if chunk.strip():
                chunks.append({
                    'text': chunk,
                    'metadata': {'page': 1}  # Page info not available with this method
                })
        return chunks
