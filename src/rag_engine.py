"""
RAG (Retrieval Augmented Generation) engine for the CRE Chatbot.
"""
import logging
import os
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings
from openai import AzureOpenAI
from app.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,  # Added this line
    TEMPERATURE,
    MAX_TOKENS,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
)

logger = logging.getLogger('rag')

class RAGEngine:
    """Handles document retrieval and question answering using Azure OpenAI."""
    
    def __init__(self, deployment_name: str):
        """Initialize the RAG engine with Azure OpenAI client."""
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2023-12-01-preview",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        self.deployment_name = deployment_name
        self.embedding_deployment_name = AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
        
        # Initialize ChromaDB with simple in-memory settings
        self.chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
        self.collection = None
        self.initialize_vector_store("cre_docs")
        logger.info("RAG Engine initialized with Azure OpenAI")
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for the given texts using Azure OpenAI."""
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.embedding_deployment_name
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    def initialize_vector_store(self, collection_name: str):
        """Initialize or get the vector store collection."""
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Vector store initialized with collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def add_documents(self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None):
        """Add documents to the vector store."""
        try:
            if not self.collection:
                raise ValueError("Vector store collection not initialized")
                
            embeddings = self.create_embeddings(texts)
            # Use timestamp + index as ID to ensure uniqueness
            import time
            timestamp = int(time.time())
            ids = [f"{timestamp}_{i}" for i in range(len(texts))]
            
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                ids=ids,
                metadatas=metadata if metadata else [{}] * len(texts)
            )
            logger.info(f"Added {len(texts)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def query(self, question: str, k: int = 3) -> Dict[str, Any]:
        """Query the vector store and generate an answer."""
        try:
            # Create embedding for the question
            question_embedding = self.create_embeddings([question])[0]
            
            # Query vector store
            results = self.collection.query(
                query_embeddings=[question_embedding],
                n_results=k
            )
            
            # Prepare context from retrieved documents
            context = "\n".join(results['documents'][0])
            
            # Generate answer using Azure OpenAI
            messages = [
                {"role": "system", "content": "You are a helpful assistant that answers questions about commercial real estate concepts. Use the provided context to answer questions accurately and concisely."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "context": context,
                "source_documents": results['documents'][0]
            }
            
        except Exception as e:
            logger.error(f"Error querying RAG engine: {str(e)}")
            raise
    
    def clear(self):
        """Clear the vector store collection."""
        if self.collection:
            self.collection.delete()
            logger.info("Vector store collection cleared")
