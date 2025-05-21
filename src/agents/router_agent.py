"""
Router Agent for the Agent Swarm system.

This agent is responsible for analyzing incoming messages and routing them
to the appropriate specialized agent based on the content.
"""
from typing import Dict, Any, List, Optional, Type
import re
from .base_agent import BaseAgent


class RouterAgent(BaseAgent):
    """
    Router Agent that analyzes incoming messages and routes them to specialized agents.
    
    This agent serves as the entry point for all user messages and manages the workflow
    between other agents in the swarm.
    """
    
    def __init__(self, name: str = "Router"):
        """Initialize the Router Agent.
        
        Args:
            name: The name of the agent
        """
        super().__init__(name)
        self.registered_agents: Dict[str, BaseAgent] = {}
        
    def register_agent(self, agent_type: str, agent: BaseAgent) -> None:
        """Register a specialized agent with the router.
        
        Args:
            agent_type: The type/category of the agent
            agent: The agent instance to register
        """
        self.registered_agents[agent_type] = agent
        
    async def process(self, message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message by analyzing it and routing to the appropriate agent.
        
        Args:
            message: The user message to process
            user_id: The ID of the user sending the message
            context: Optional context information
            
        Returns:
            Dict containing the response and workflow information
        """
        # Analyze the message to determine which agent should handle it
        agent_type = self._analyze_message(message)
        
        # Get the appropriate agent
        if agent_type not in self.registered_agents:
            return {
                "response": "I'm unable to process this request as the required agent is not available.",
                "agent_workflow": [{"agent_name": self.name, "tool_calls": self.get_tool_calls()}]
            }
        
        agent = self.registered_agents[agent_type]
        
        # Process the message with the selected agent
        agent_response = await agent.process(message, user_id, context)
        
        # Record the workflow
        workflow = [
            {"agent_name": self.name, "tool_calls": self.get_tool_calls()},
            {"agent_name": agent.name, "tool_calls": agent.get_tool_calls()}
        ]
        
        # If we have a personality agent, apply it
        if "personality" in self.registered_agents and agent_type != "personality":
            personality_agent = self.registered_agents["personality"]
            
            # The personality agent needs the original response
            personality_context = context or {}
            personality_context["source_agent_response"] = agent_response.get("response", "")
            
            personality_response = await personality_agent.process(
                message, 
                user_id, 
                personality_context
            )
            
            # Add personality agent to workflow
            workflow.append({
                "agent_name": personality_agent.name, 
                "tool_calls": personality_agent.get_tool_calls()
            })
            
            # Return the personality-enhanced response
            return {
                "response": personality_response.get("response", ""),
                "source_agent_response": agent_response.get("response", ""),
                "agent_workflow": workflow
            }
        
        # If no personality agent or if this is already the personality agent's response
        return {
            "response": agent_response.get("response", ""),
            "agent_workflow": workflow
        }
    
    def _analyze_message(self, message: str) -> str:
        """Analyze the message content to determine which agent should handle it.
        
        Args:
            message: The user message to analyze
            
        Returns:
            The type of agent that should handle the message
        """
        # Record this tool call
        self.record_tool_call("message_analysis", {"message": message})
        
        # Convert message to lowercase for easier pattern matching
        message_lower = message.lower()
        
        # Check for customer support patterns
        support_patterns = [
            r"(can'?t|unable to) (sign|log) in",
            r"(can'?t|unable to) (make|do|perform) (transfer|payment)",
            r"(problem|issue|error|trouble) with (my|the) account",
            r"(help|support|assistance) (with|for|regarding)",
            r"not working",
            r"doesn'?t work"
        ]
        
        for pattern in support_patterns:
            if re.search(pattern, message_lower):
                return "support"
        
        # Check for general knowledge or web search patterns
        general_knowledge_patterns = [
            r"(what|when|where|who|how|why) (is|are|was|were|do|does|did)",
            r"tell me about",
            r"(news|information) (about|on|regarding)",
            r"(latest|recent) (news|information|updates)"
        ]
        
        for pattern in general_knowledge_patterns:
            if re.search(pattern, message_lower):
                return "knowledge"
        
        # Check for InfinitePay specific knowledge patterns
        infinitepay_patterns = [
            r"(infinitepay|infinite pay)",
            r"(fee|cost|price|rate|charge)",
            r"(maquininha|card machine|card reader)",
            r"(tap to pay|contactless)",
            r"(pix|boleto|payment|transfer)",
            r"(conta digital|digital account)",
            r"(emprestimo|loan)",
            r"(cartao|card)"
        ]
        
        for pattern in infinitepay_patterns:
            if re.search(pattern, message_lower):
                return "knowledge"
        
        # Default to knowledge agent if no specific pattern is matched
        return "knowledge"
