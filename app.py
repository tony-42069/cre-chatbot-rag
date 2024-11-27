import streamlit as st
import tempfile
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
st.set_page_config(page_title="Concept Definition Chatbot", layout="wide")
st.title("Concept Definition Chatbot")

# Sidebar for PDF upload
with st.sidebar:
    st.header("Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None and not st.session_state.processed_file:
        with st.spinner("Processing PDF..."):
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Process PDF
                processor = PDFProcessor()
                chunks = processor.process_pdf(tmp_path)
                
                # Initialize RAG engine
                st.session_state.rag_engine.initialize_vector_store(chunks)
                st.session_state.processed_file = True
                
                # Clean up
                os.unlink(tmp_path)
            except ValueError as e:
                st.error(f"Configuration Error: {str(e)}")
                st.stop()
            except ConnectionError as e:
                st.error(f"Connection Error: {str(e)}")
                st.stop()
            except Exception as e:
                st.error(f"Unexpected Error: {str(e)}")
                st.stop()
        st.success("PDF processed successfully!")

# Main chat interface
if st.session_state.processed_file:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("View Sources"):
                    for source in message["sources"]:
                        st.markdown(f"**Page {source['page']}:**\n{source['text']}")

    # Chat input
    if prompt := st.chat_input("Ask a question about the concepts in your PDF"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.rag_engine.answer_question(prompt)
                    
                    # Display response
                    st.markdown(response["answer"])
                    
                    # Display sources in expander
                    with st.expander("View Sources"):
                        for source in response["sources"]:
                            st.markdown(f"**Page {source['page']}:**\n{source['text']}")
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response["sources"]
                    })
                except ValueError as e:
                    st.error(f"Configuration Error: {str(e)}")
                    st.stop()
                except ConnectionError as e:
                    st.error(f"Connection Error: {str(e)}")
                    st.stop()
                except Exception as e:
                    st.error(f"Unexpected Error: {str(e)}")
                    st.stop()
else:
    st.info("Please upload a PDF file to start chatting.")
