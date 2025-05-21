"""
Unit tests for the Knowledge Agent.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.knowledge_agent import KnowledgeAgent


@pytest.fixture
def mock_vectorstore():
    """Create a mock vectorstore."""
    mock = MagicMock()
    mock.as_retriever.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_qa_chain():
    """Create a mock QA chain."""
    mock = MagicMock()
    mock.invoke.return_value = {"result": "This is a test response about InfinitePay."}
    return mock


@pytest.mark.asyncio
async def test_knowledge_agent_initialization():
    """Test that the knowledge agent initializes correctly."""
    agent = KnowledgeAgent(api_key="test_key")
    assert agent.name == "Knowledge"
    assert agent.api_key == "test_key"
    assert agent.vectorstore is None
    assert agent.qa_chain is None


@pytest.mark.asyncio
@patch('src.agents.knowledge_agent.KnowledgeAgent._initialize_rag_pipeline')
@patch('src.agents.knowledge_agent.KnowledgeAgent._is_general_knowledge_question')
@patch('src.agents.knowledge_agent.KnowledgeAgent._retrieve_and_generate')
async def test_knowledge_agent_process_infinitepay_query(
    mock_retrieve, mock_is_general, mock_initialize, mock_vectorstore, mock_qa_chain
):
    """Test that the knowledge agent processes InfinitePay queries correctly."""
    # Configure mocks
    mock_is_general.return_value = False
    mock_retrieve.return_value = "Response about InfinitePay"
    
    # Create agent
    agent = KnowledgeAgent(api_key="test_key")
    agent.vectorstore = mock_vectorstore
    agent.qa_chain = mock_qa_chain
    
    # Process a query
    result = await agent.process("What are the fees for Maquininha Smart?", "user123")
    
    # Verify the agent processed the query correctly
    mock_initialize.assert_not_called()  # Should not initialize since vectorstore is set
    mock_is_general.assert_called_once()
    mock_retrieve.assert_called_once()
    assert result["response"] == "Response about InfinitePay"
    assert result["agent_type"] == "knowledge"


@pytest.mark.asyncio
@patch('src.agents.knowledge_agent.KnowledgeAgent._initialize_rag_pipeline')
@patch('src.agents.knowledge_agent.KnowledgeAgent._is_general_knowledge_question')
@patch('src.agents.knowledge_agent.KnowledgeAgent._handle_general_knowledge')
async def test_knowledge_agent_process_general_query(
    mock_general, mock_is_general, mock_initialize, mock_vectorstore, mock_qa_chain
):
    """Test that the knowledge agent processes general knowledge queries correctly."""
    # Configure mocks
    mock_is_general.return_value = True
    mock_general.return_value = "Response about general knowledge"
    
    # Create agent
    agent = KnowledgeAgent(api_key="test_key")
    agent.vectorstore = mock_vectorstore
    agent.qa_chain = mock_qa_chain
    
    # Process a query
    result = await agent.process("What is the weather in São Paulo?", "user123")
    
    # Verify the agent processed the query correctly
    mock_initialize.assert_not_called()  # Should not initialize since vectorstore is set
    mock_is_general.assert_called_once()
    mock_general.assert_called_once()
    assert result["response"] == "Response about general knowledge"
    assert result["agent_type"] == "knowledge"


@pytest.mark.asyncio
@patch('src.agents.knowledge_agent.KnowledgeAgent._initialize_rag_pipeline')
async def test_knowledge_agent_initialize_if_needed(mock_initialize, mock_vectorstore, mock_qa_chain):
    """Test that the knowledge agent initializes the RAG pipeline if needed."""
    # Create agent with no vectorstore
    agent = KnowledgeAgent(api_key="test_key")
    
    # Configure mocks for the rest of the process
    mock_initialize.return_value = None
    agent._is_general_knowledge_question = MagicMock(return_value=False)
    agent._retrieve_and_generate = AsyncMock(return_value="Test response")
    
    # Process a query
    await agent.process("What are the fees for Maquininha Smart?", "user123")
    
    # Verify the agent initialized the RAG pipeline
    mock_initialize.assert_called_once()


def test_is_general_knowledge_question():
    """Test the general knowledge question detection."""
    agent = KnowledgeAgent(api_key="test_key")
    
    # InfinitePay-related queries should return False
    assert not agent._is_general_knowledge_question("What are the fees for Maquininha?")
    assert not agent._is_general_knowledge_question("Tell me about InfinitePay's card reader")
    assert not agent._is_general_knowledge_question("How does Pix work with InfinitePay?")
    
    # General knowledge queries should return True
    assert agent._is_general_knowledge_question("What's the latest news about technology?")
    assert agent._is_general_knowledge_question("Tell me about the weather in Brazil")
    assert agent._is_general_knowledge_question("What's happening in sports today?")
