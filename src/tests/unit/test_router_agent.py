"""
Unit tests for the Router Agent.
"""
import pytest
from unittest.mock import AsyncMock, patch
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.router_agent import RouterAgent
from src.agents.base_agent import BaseAgent


class MockAgent(BaseAgent):
    """Mock agent for testing."""

    async def process(self, message, user_id, context=None):
        return {"response": f"Response from {self.name}"}


@pytest.fixture
def router_agent():
    """Create a router agent with mock specialized agents."""
    router = RouterAgent()
    
    # Create and register mock agents
    knowledge_agent = MockAgent("Knowledge")
    support_agent = MockAgent("Support")
    personality_agent = MockAgent("Personality")
    
    router.register_agent("knowledge", knowledge_agent)
    router.register_agent("support", support_agent)
    router.register_agent("personality", personality_agent)
    
    return router


@pytest.mark.asyncio
async def test_router_agent_initialization():
    """Test that the router agent initializes correctly."""
    router = RouterAgent()
    assert router.name == "Router"
    assert router.registered_agents == {}


@pytest.mark.asyncio
async def test_router_agent_registration():
    """Test that agents can be registered with the router."""
    router = RouterAgent()
    mock_agent = MockAgent("Test")
    
    router.register_agent("test", mock_agent)
    assert "test" in router.registered_agents
    assert router.registered_agents["test"] == mock_agent


@pytest.mark.asyncio
async def test_router_agent_knowledge_routing():
    """Test that the router correctly routes knowledge queries."""
    router = RouterAgent()
    knowledge_agent = MockAgent("Knowledge")
    knowledge_agent.process = AsyncMock(return_value={"response": f"Response from {knowledge_agent.name}"})
    router.register_agent("knowledge", knowledge_agent)
    
    # Test with a knowledge query
    result = await router.process("What are the fees for the Maquininha Smart?", "user123")
    
    # Verify the knowledge agent was called
    knowledge_agent.process.assert_called_once()
    assert "Response from Knowledge" in result["response"]


@pytest.mark.asyncio
async def test_router_agent_support_routing():
    """Test that the router correctly routes support queries."""
    router = RouterAgent()
    support_agent = MockAgent("Support")
    support_agent.process = AsyncMock(return_value={"response": f"Response from {support_agent.name}"})
    router.register_agent("support", support_agent)
    
    # Test with a support query
    result = await router.process("I can't sign in to my account", "user123")
    
    # Verify the support agent was called
    support_agent.process.assert_called_once()
    assert "Response from Support" in result["response"]


@pytest.mark.asyncio
async def test_router_agent_personality_application():
    """Test that the personality agent is applied to responses."""
    router = RouterAgent()
    knowledge_agent = MockAgent("Knowledge")
    personality_agent = MockAgent("Personality")
    knowledge_agent.process = AsyncMock(return_value={"response": f"Response from {knowledge_agent.name}"})
    personality_agent.process = AsyncMock(return_value={"response": f"Response from {personality_agent.name}"})
    
    router.register_agent("knowledge", knowledge_agent)
    router.register_agent("personality", personality_agent)
    
    # Test with a knowledge query
    result = await router.process("What are the fees for the Maquininha Smart?", "user123")
    
    # Verify both agents were called
    knowledge_agent.process.assert_called_once()
    personality_agent.process.assert_called_once()
    
    # Verify the workflow includes both agents
    agent_names = [step["agent_name"] for step in result["agent_workflow"]]
    assert "Router" in agent_names
    assert "Knowledge" in agent_names
    assert "Personality" in agent_names


@pytest.mark.asyncio
async def test_router_agent_missing_agent():
    """Test that the router handles missing agents gracefully."""
    router = RouterAgent()
    
    # Test with a query when no agents are registered
    result = await router.process("What are the fees for the Maquininha Smart?", "user123")
    
    # Verify the response indicates the agent is not available
    assert "unable to process" in result["response"].lower()
    
    # Verify the workflow only includes the router
    agent_names = [step["agent_name"] for step in result["agent_workflow"]]
    assert len(agent_names) == 1
    assert "Router" in agent_names
