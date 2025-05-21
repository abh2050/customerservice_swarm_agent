"""
Unit tests for the Personality Agent.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.personality_agent import PersonalityAgent


@pytest.mark.asyncio
async def test_personality_agent_initialization():
    """Test that the personality agent initializes correctly."""
    agent = PersonalityAgent()
    assert agent.name == "Personality"
    assert agent.personality_type == "friendly"
    
    # Test with different personality type
    agent = PersonalityAgent(personality_type="professional")
    assert agent.personality_type == "professional"


@pytest.mark.asyncio
async def test_personality_agent_process_with_source():
    """Test that the personality agent processes responses correctly when source is provided."""
    agent = PersonalityAgent()
    
    # Process with a source response
    context = {"source_agent_response": "This is a test response from another agent."}
    result = await agent.process("Original message", "user123", context)
    
    # Verify the agent processed the response
    assert "response" in result
    assert result["agent_type"] == "personality"
    assert len(result["response"]) > len(context["source_agent_response"])


@pytest.mark.asyncio
async def test_personality_agent_process_without_source():
    """Test that the personality agent handles missing source responses."""
    agent = PersonalityAgent()
    
    # Process without a source response
    result = await agent.process("Original message", "user123", {})
    
    # Verify the agent returned a default message
    assert "response" in result
    assert "not sure how to respond" in result["response"].lower()
    assert result["agent_type"] == "personality"


@pytest.mark.asyncio
async def test_personality_agent_transform_response():
    """Test the response transformation logic."""
    agent = PersonalityAgent()
    
    # Test with a simple response
    original = "This is a test response."
    transformed = agent._transform_response(original)
    
    # Verify the transformation added personality elements
    assert len(transformed) > len(original)
    
    # Test with a multi-paragraph response
    original = "This is paragraph one.\n\nThis is paragraph two."
    transformed = agent._transform_response(original)
    
    # Verify the transformation handled paragraphs correctly
    assert "\n\n" in transformed
    assert len(transformed.split("\n\n")) == 2


@pytest.mark.asyncio
async def test_personality_agent_different_personalities():
    """Test different personality types."""
    # Test friendly personality
    friendly_agent = PersonalityAgent(personality_type="friendly")
    friendly_result = friendly_agent._transform_response("This is a test.")
    
    # Test professional personality
    professional_agent = PersonalityAgent(personality_type="professional")
    professional_result = professional_agent._transform_response("This is a test.")
    
    # Test casual personality
    casual_agent = PersonalityAgent(personality_type="casual")
    casual_result = casual_agent._transform_response("This is a test.")
    
    # Verify each personality produces different results
    assert friendly_result != professional_result
    assert friendly_result != casual_result
    assert professional_result != casual_result


def test_set_personality():
    """Test setting the personality type."""
    agent = PersonalityAgent()
    
    # Test setting a valid personality
    agent.set_personality("professional")
    assert agent.personality_type == "professional"
    
    # Test setting an invalid personality
    agent.set_personality("invalid_type")
    assert agent.personality_type == "professional"  # Should not change
