from typing import List, Dict
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
        try:
            # Try using PyPDFLoader from langchain
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            
            # Split the text into chunks
            chunks = []
            for page in pages:
                page_chunks = self.text_splitter.split_text(page.page_content)
                for chunk in page_chunks:
                    chunks.append({
                        'text': chunk,
                        'metadata': {'page': page.metadata['page']}
                    })
            return chunks
            
        except Exception as e:
            print(f"Error with PyPDFLoader: {str(e)}")
            print("Trying alternative PDF processing method...")
            
            # Fallback to direct pypdf usage
            try:
                with open(pdf_path, 'rb') as file:
                    pdf = pypdf.PdfReader(file)
                    chunks = []
                    
                    for page_num in range(len(pdf.pages)):
                        text = pdf.pages[page_num].extract_text()
                        page_chunks = self.text_splitter.split_text(text)
                        
                        for chunk in page_chunks:
                            chunks.append({
                                'text': chunk,
                                'metadata': {'page': page_num + 1}
                            })
                    return chunks
                    
            except Exception as e2:
                raise Exception(f"Failed to process PDF with both methods. Error: {str(e2)}")
