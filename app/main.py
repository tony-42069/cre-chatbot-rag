"""
Main Streamlit application for the CRE Chatbot.
"""
import logging
import streamlit as st
from io import BytesIO
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import validate_config, AZURE_OPENAI_DEPLOYMENT_NAME
from app.logging import setup_logging
from src.pdf_processor import PDFProcessor
from src.rag_engine import RAGEngine

# Setup logging
loggers = setup_logging()
logger = logging.getLogger('app')

# Page configuration
st.set_page_config(
    page_title="CRE Knowledge Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e3f2fd;
    }
    .chat-message.assistant {
        background-color: #f3e5f5;
    }
    .chat-message .message {
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None
if 'pdf_processor' not in st.session_state:
    st.session_state.pdf_processor = PDFProcessor()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_pdfs' not in st.session_state:
    st.session_state.uploaded_pdfs = set()

def initialize_rag_engine(deployment_name: str):
    """Initialize the RAG engine with error handling."""
    try:
        st.session_state.rag_engine = RAGEngine(deployment_name)
        logger.info("RAG Engine initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing the application: {str(e)}")
        st.error(f"Error initializing the application: {str(e)}")

def process_pdf(pdf_file):
    """Process uploaded PDF file."""
    try:
        # Check if PDF was already processed
        if pdf_file.name in st.session_state.uploaded_pdfs:
            st.warning(f"'{pdf_file.name}' has already been processed!")
            return

        with st.spinner(f"Processing {pdf_file.name}..."):
            # Read PDF content
            pdf_content = pdf_file.read()
            
            # Process PDF and get chunks
            chunks = st.session_state.pdf_processor.process_pdf(
                BytesIO(pdf_content)
            )
            
            # Add chunks to vector store
            texts = [chunk[0] for chunk in chunks]
            metadata = [{"source": pdf_file.name, **chunk[1]} for chunk in chunks]
            st.session_state.rag_engine.add_documents(texts, metadata)
            
            # Mark PDF as processed
            st.session_state.uploaded_pdfs.add(pdf_file.name)
            
        st.success(f"Successfully processed '{pdf_file.name}'!")
        logger.info(f"PDF '{pdf_file.name}' processed and added to vector store")
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        st.error(f"Error processing PDF: {str(e)}")

def display_chat_message(role: str, content: str):
    """Display a chat message with proper styling."""
    with st.container():
        st.markdown(f"""
            <div class="chat-message {role}">
                <div class="role"><strong>{'You' if role == 'user' else 'Assistant'}:</strong></div>
                <div class="message">{content}</div>
            </div>
        """, unsafe_allow_html=True)

def main():
    """Main application function."""
    # Header
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("🏢 CRE Knowledge Assistant")
        st.markdown("*Your AI guide for commercial real estate concepts*")
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Knowledge Base")
        st.markdown("Upload your CRE documents to enhance the assistant's knowledge.")
        
        # Model configuration (collapsible)
        with st.expander("⚙️ Model Configuration"):
            deployment_name = st.text_input(
                "Model Deployment Name",
                value=AZURE_OPENAI_DEPLOYMENT_NAME,
                help="Enter your Azure OpenAI model deployment name"
            )
        
        # Initialize RAG engine if not already done
        if not st.session_state.rag_engine:
            initialize_rag_engine(deployment_name)
        
        # PDF upload section
        st.subheader("📄 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type="pdf",
            accept_multiple_files=True,
            help="Upload one or more PDF files to add to the knowledge base"
        )
        
        if uploaded_files:
            for pdf_file in uploaded_files:
                process_pdf(pdf_file)
        
        # Show processed documents
        if st.session_state.uploaded_pdfs:
            st.subheader("📚 Processed Documents")
            for pdf_name in st.session_state.uploaded_pdfs:
                st.markdown(f"✓ {pdf_name}")
    
    # Main chat interface
    if st.session_state.rag_engine:
        # Display chat history
        for message in st.session_state.chat_history:
            display_chat_message(
                role=message["role"],
                content=message["content"]
            )
        
        # Chat input
        user_question = st.text_input(
            "Ask a question about commercial real estate:",
            placeholder="e.g., What is LTV? How is DSCR calculated?",
            key="user_question"
        )
        
        if user_question:
            try:
                # Add user message to chat
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_question
                })
                
                with st.spinner("Generating answer..."):
                    response = st.session_state.rag_engine.query(user_question)
                
                # Add assistant response to chat
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["answer"]
                })
                
                # Display latest messages immediately
                display_chat_message("user", user_question)
                display_chat_message("assistant", response["answer"])
                
            except Exception as e:
                logger.error(f"Error generating answer: {str(e)}")
                st.error(f"Error generating answer: {str(e)}")
    
    else:
        st.info("👆 Please upload PDF documents in the sidebar to start asking questions!")

if __name__ == "__main__":
    main()
