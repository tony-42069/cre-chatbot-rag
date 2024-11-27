"""
Tests for the RAG engine module.
"""
import pytest
from unittest.mock import Mock, patch
from src.rag_engine import RAGEngine

@pytest.fixture
def mock_azure_client():
    """Create a mock Azure OpenAI client."""
    with patch('openai.AzureOpenAI') as mock_client:
        yield mock_client

@pytest.fixture
def mock_chroma_client():
    """Create a mock Chroma client."""
    with patch('chromadb.Client') as mock_client:
        yield mock_client

@pytest.fixture
def rag_engine(mock_azure_client, mock_chroma_client):
    """Create a RAG engine instance with mocked dependencies."""
    return RAGEngine("test-deployment")

def test_create_embeddings(rag_engine, mock_azure_client):
    """Test embedding creation."""
    # Setup mock response
    mock_response = Mock()
    mock_response.data = [
        Mock(embedding=[0.1, 0.2, 0.3]),
        Mock(embedding=[0.4, 0.5, 0.6])
    ]
    rag_engine.client.embeddings.create.return_value = mock_response
    
    # Test
    texts = ["Text 1", "Text 2"]
    embeddings = rag_engine.create_embeddings(texts)
    
    # Verify
    assert len(embeddings) == 2
    assert all(isinstance(emb, list) for emb in embeddings)
    assert len(embeddings[0]) == 3  # Embedding dimension

def test_initialize_vector_store(rag_engine):
    """Test vector store initialization."""
    rag_engine.initialize_vector_store("test_collection")
    
    # Verify the collection was created
    assert rag_engine.collection is not None

def test_add_documents(rag_engine):
    """Test adding documents to vector store."""
    # Setup
    rag_engine.initialize_vector_store("test_collection")
    texts = ["Document 1", "Document 2"]
    metadata = [{"source": "test1"}, {"source": "test2"}]
    
    # Create mock embeddings
    with patch.object(rag_engine, 'create_embeddings') as mock_create_embeddings:
        mock_create_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
        
        # Test
        rag_engine.add_documents(texts, metadata)
        
        # Verify
        mock_create_embeddings.assert_called_once_with(texts)
        assert rag_engine.collection.add.called

def test_query(rag_engine):
    """Test querying the RAG engine."""
    # Setup
    rag_engine.initialize_vector_store("test_collection")
    
    # Mock embeddings creation
    with patch.object(rag_engine, 'create_embeddings') as mock_create_embeddings:
        mock_create_embeddings.return_value = [[0.1, 0.2]]
        
        # Mock vector store query
        mock_results = {
            'documents': [["Relevant document 1", "Relevant document 2"]],
            'distances': [[0.1, 0.2]]
        }
        rag_engine.collection.query.return_value = mock_results
        
        # Mock chat completion
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test answer"))]
        rag_engine.client.chat.completions.create.return_value = mock_response
        
        # Test
        result = rag_engine.query("Test question")
        
        # Verify
        assert isinstance(result, dict)
        assert "answer" in result
        assert "context" in result
        assert "source_documents" in result
        assert result["answer"] == "Test answer"

def test_error_handling(rag_engine):
    """Test error handling in RAG engine."""
    # Test error in embeddings creation
    rag_engine.client.embeddings.create.side_effect = Exception("API Error")
    
    with pytest.raises(Exception):
        rag_engine.create_embeddings(["Test"])
    
    # Test error in vector store initialization
    rag_engine.chroma_client.get_or_create_collection.side_effect = Exception("DB Error")
    
    with pytest.raises(Exception):
        rag_engine.initialize_vector_store("test")
