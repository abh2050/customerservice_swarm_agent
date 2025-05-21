"""
FastAPI application for the Agent Swarm system.

This module sets up the HTTP API endpoint for processing user messages
through the Agent Swarm.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging
import asyncio
from dotenv import load_dotenv

# Import agents
from src.agents.router_agent import RouterAgent
from src.agents.knowledge_agent import KnowledgeAgent
from src.agents.customer_support_agent import CustomerSupportAgent
from src.agents.personality_agent import PersonalityAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agent Swarm API",
    description="API for processing messages through an Agent Swarm system",
    version="1.0.0"
)

# Request and response models
class MessageRequest(BaseModel):
    message: str
    user_id: str

class MessageResponse(BaseModel):
    response: str
    source_agent_response: str = ""
    agent_workflow: list = []

# Initialize agents
router_agent = RouterAgent()
knowledge_agent = KnowledgeAgent(api_key=os.environ.get("OPENAI_API_KEY"))
support_agent = CustomerSupportAgent()
personality_agent = PersonalityAgent(personality_type="friendly")

# Register agents with the router
router_agent.register_agent("knowledge", knowledge_agent)
router_agent.register_agent("support", support_agent)
router_agent.register_agent("personality", personality_agent)

@app.get("/")
async def root():
    """Root endpoint that returns API information."""
    return {
        "name": "Agent Swarm API",
        "version": "1.0.0",
        "description": "API for processing messages through an Agent Swarm system"
    }

@app.post("/api/message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    """
    Process a message through the Agent Swarm.
    
    Args:
        request: MessageRequest containing the user message and user ID
        
    Returns:
        MessageResponse containing the agent's response and workflow information
    """
    try:
        logger.info(f"Received message from user {request.user_id}")
        
        # Process the message through the router agent
        result = await router_agent.process(request.message, request.user_id)
        
        logger.info(f"Processed message from user {request.user_id}")
        
        # Return the response
        return MessageResponse(
            response=result.get("response", ""),
            source_agent_response=result.get("source_agent_response", ""),
            agent_workflow=result.get("agent_workflow", [])
        )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
