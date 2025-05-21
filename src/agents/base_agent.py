"""
Base Agent class for the Agent Swarm system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseAgent(ABC):
    """Base class for all agents in the swarm."""
    
    def __init__(self, name: str):
        """Initialize the base agent.
        
        Args:
            name: The name of the agent
        """
        self.name = name
        self.tool_calls: Dict[str, Any] = {}
    
    @abstractmethod
    async def process(self, message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message and return a response.
        
        Args:
            message: The user message to process
            user_id: The ID of the user sending the message
            context: Optional context information
            
        Returns:
            Dict containing the response and any additional information
        """
        pass
    
    def record_tool_call(self, tool_name: str, tool_result: Any) -> None:
        """Record a tool call for tracking purposes.
        
        Args:
            tool_name: The name of the tool called
            tool_result: The result returned by the tool
        """
        self.tool_calls[tool_name] = tool_result
    
    def get_tool_calls(self) -> Dict[str, Any]:
        """Get all recorded tool calls.
        
        Returns:
            Dict of tool calls and their results
        """
        return self.tool_calls
    
    def clear_tool_calls(self) -> None:
        """Clear all recorded tool calls."""
        self.tool_calls = {}
