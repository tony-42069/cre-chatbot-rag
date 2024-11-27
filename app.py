import streamlit as st
import os
from pdf_processor import PDFProcessor
from rag_engine import RAGEngine

# Initialize session state
if 'rag_engine' not in st.session_state:
    try:
        st.session_state.rag_engine = RAGEngine()
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        st.stop()
    except ConnectionError as e:
        st.error(f"Connection Error: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        st.stop()

if 'processed_file' not in st.session_state:
    st.session_state.processed_file = False

# Page config
st.set_page_config(
    page_title="CRE Knowledge Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        margin-bottom: 2rem;
        text-align: center;
    }
    .chat-container {
        background-color: #F3F4F6;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    .sidebar-content {
        padding: 1.5rem;
        background-color: #F8FAFC;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-header">Commercial Real Estate Knowledge Assistant</h1>', unsafe_allow_html=True)

# Initialize RAG engine with pre-loaded PDF if not already done
if not st.session_state.processed_file:
    with st.spinner("Initializing knowledge base..."):
        try:
            # Process the pre-loaded PDF
            pdf_path = os.path.join("Dataset", "Commercial Lending 101.pdf")
            processor = PDFProcessor()
            chunks = processor.process_pdf(pdf_path)
            
            # Initialize RAG engine
            st.session_state.rag_engine.initialize_vector_store(chunks)
            st.session_state.processed_file = True
        except Exception as e:
            st.error(f"Error initializing knowledge base: {str(e)}")
            st.stop()

# Sidebar with information
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/tony-42069/cre-chatbot-rag/main/Dataset/commercial-lending-101.png", 
             use_column_width=True)
    st.markdown("""
    ### About
    This AI assistant is trained on commercial real estate knowledge and can help you understand:
    - Commercial lending concepts
    - Real estate terminology
    - Market analysis
    - Investment strategies
    
    ### How to Use
    Simply type your question in the chat box below and press Enter. The assistant will provide detailed answers based on the commercial real estate knowledge base.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Chat interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about commercial real estate..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.rag_engine.get_response(prompt)
                st.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)
