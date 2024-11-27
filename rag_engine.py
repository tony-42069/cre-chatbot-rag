import os
from typing import List, Dict
from dotenv import load_dotenv
import chromadb
from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import AzureChatOpenAI
from langchain.chains import RetrievalQA
import time

# Load environment variables
load_dotenv()

class RAGEngine:
    def __init__(self):
        # Verify Azure OpenAI settings are set
        required_vars = [
            'AZURE_OPENAI_ENDPOINT',
            'AZURE_OPENAI_KEY',
            'AZURE_OPENAI_DEPLOYMENT_NAME',
            'AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required Azure OpenAI settings: {', '.join(missing_vars)}")
        
        # Initialize with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.embeddings = AzureOpenAIEmbeddings(
                    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                    azure_deployment=os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME'),
                    api_key=os.getenv('AZURE_OPENAI_KEY')
                )
                self.vector_store = None
                self.qa_chain = None
                # Test connection
                self.embeddings.embed_query("test")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise ConnectionError(f"Failed to connect to Azure OpenAI API after {max_retries} attempts. Error: {str(e)}")
                time.sleep(2)  # Wait before retrying
        
    def initialize_vector_store(self, chunks: List[Dict]):
        """
        Initialize the vector store with document chunks.
        
        Args:
            chunks (List[Dict]): List of dictionaries containing text and metadata
        """
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Create vector store
        self.vector_store = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )
        
        # Initialize QA chain
        llm = AzureChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", azure_deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'), azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'), api_key=os.getenv('AZURE_OPENAI_KEY'))
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 3}
            )
        )
    
    def answer_question(self, question: str) -> Dict:
        """
        Answer a question using the RAG system.
        
        Args:
            question (str): User's question
            
        Returns:
            Dict: Answer and source information
        """
        if not self.qa_chain:
            raise ValueError("Vector store not initialized. Please process documents first.")
        
        # Create a prompt that emphasizes definition extraction
        prompt = f"""
        Question: {question}
        Please provide a clear and concise answer based on the provided context. 
        If the question asks for a definition or explanation of a concept, 
        make sure to provide that specifically. Include relevant examples or 
        additional context only if they help clarify the concept.
        """
        
        # Get answer from QA chain
        result = self.qa_chain({"query": prompt})
        
        # Get source documents
        source_docs = self.vector_store.similarity_search(question, k=2)
        sources = [
            {
                'page': doc.metadata['page'],
                'text': doc.page_content[:200] + "..."  # Preview of source text
            }
            for doc in source_docs
        ]
        
        return {
            'answer': result['result'],
            'sources': sources
        }
