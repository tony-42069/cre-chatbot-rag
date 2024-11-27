import streamlit as st
import requests
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import validate_config
from app.logging import setup_logging

def main():
    # Setup logging
    setup_logging()
    
    st.set_page_config(
        page_title="CRE Knowledge Assistant",
        page_icon="🤖",
        layout="wide"
    )

    st.title("CRE Knowledge Assistant")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
    
    if uploaded_file:
        # Convert file to bytes
        file_bytes = uploaded_file.getvalue()
        
        # Send to API endpoint
        response = requests.post(
            "api/process_pdf",
            files={"file": (uploaded_file.name, file_bytes, "application/pdf")}
        )
        
        if response.status_code == 200:
            st.success("PDF processed successfully!")
        else:
            st.error("Error processing PDF")
    
    # Query input
    query = st.text_input("Ask a question about your documents:")
    
    if query:
        # Send query to API endpoint
        response = requests.post(
            "api/query",
            json={"query": query}
        )
        
        if response.status_code == 200:
            result = response.json()
            st.write("Answer:", result["answer"])
        else:
            st.error("Error processing query")

if __name__ == "__main__":
    main()
