from typing import List, Dict
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
            List[Dict]: List of dictionaries containing text chunks and metadata
        """
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        
        # Split text into chunks
        chunks = self.text_splitter.split_documents(pages)
        
        # Format chunks with metadata
        processed_chunks = []
        for chunk in chunks:
            processed_chunks.append({
                'text': chunk.page_content,
                'metadata': {
                    'page': chunk.metadata.get('page', 0) + 1,
                    'source': pdf_path
                }
            })
        
        return processed_chunks
