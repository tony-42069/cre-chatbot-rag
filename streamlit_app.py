import streamlit as st
import os
from dotenv import load_dotenv
from pdf_processor import PDFProcessor
from rag_engine import RAGEngine
from app.config import AZURE_OPENAI_DEPLOYMENT_NAME

# Load environment variables
load_dotenv()

# Initialize components
pdf_processor = PDFProcessor()
rag_engine = RAGEngine(deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME)

def main():
    st.set_page_config(
        page_title="CRE Knowledge Assistant",
        page_icon="🤖",
        layout="wide"
    )

    st.title("CRE Knowledge Assistant 🏢")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
    
    if uploaded_file:
        try:
            # Process the PDF
            pdf_processor.process(uploaded_file)
            st.success("PDF processed successfully! You can now ask questions about it.")
            
            # Show chat interface
            user_question = st.text_input("Ask a question about the document:")
            if user_question:
                response = rag_engine.get_response(user_question)
                st.write("Answer:", response)
                
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")

if __name__ == "__main__":
    main()
