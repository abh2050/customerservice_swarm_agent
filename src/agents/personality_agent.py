"""
Personality Layer for the Agent Swarm system.

This agent is responsible for transforming responses from other agents
to make them more human-like and engaging.
"""
from typing import Dict, Any, List, Optional
import re
import random

from .base_agent import BaseAgent


class PersonalityAgent(BaseAgent):
    """
    Personality Agent that transforms responses to be more human-like.
    
    This agent applies a personality layer to responses from other agents
    to make them more engaging and conversational.
    """
    
    def __init__(self, name: str = "Personality", personality_type: str = "friendly"):
        """Initialize the Personality Agent.
        
        Args:
            name: The name of the agent
            personality_type: The type of personality to apply (friendly, professional, casual)
        """
        super().__init__(name)
        self.personality_type = personality_type
        
        # Define personality traits and language patterns
        self.personalities = {
            "friendly": {
                "greetings": ["Hi there!", "Hello!", "Hey!", "Greetings!"],
                "closings": ["Hope that helps!", "Let me know if you need anything else!", 
                             "I'm here if you have more questions!", "Happy to assist further!"],
                "acknowledgments": ["I understand", "I see", "Got it", "I hear you"],
                "transitions": ["So", "Well", "Now", "Alright"],
                "fillers": ["actually", "you know", "basically", "essentially"],
                "emojis": ["😊", "👍", "✨", "🙌"],
                "emoji_frequency": 0.3,  # Probability of adding an emoji
                "exclamation_frequency": 0.4,  # Probability of using exclamation marks
            },
            "professional": {
                "greetings": ["Good day", "Greetings", "Hello", "Welcome"],
                "closings": ["Please let me know if you require further assistance.", 
                             "I'm available if you have additional questions.", 
                             "Don't hesitate to reach out for more information.",
                             "Thank you for your inquiry."],
                "acknowledgments": ["I understand", "Noted", "I see", "Understood"],
                "transitions": ["Therefore", "Additionally", "Furthermore", "Moreover"],
                "fillers": ["specifically", "particularly", "notably", "indeed"],
                "emojis": [],
                "emoji_frequency": 0,
                "exclamation_frequency": 0.1,
            },
            "casual": {
                "greetings": ["Hey!", "What's up?", "Hi!", "Howdy!"],
                "closings": ["Catch you later!", "Hope that works for you!", 
                             "Let me know if you need anything!", "Take care!"],
                "acknowledgments": ["Sure thing", "Got it", "I hear ya", "Totally"],
                "transitions": ["So", "Anyway", "Alright", "OK"],
                "fillers": ["like", "kinda", "pretty much", "sort of"],
                "emojis": ["😊", "👍", "✌️", "🙂", "😉", "🤔", "💯"],
                "emoji_frequency": 0.5,
                "exclamation_frequency": 0.6,
            }
        }
    
    async def process(self, message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a message by applying a personality layer to the response.
        
        Args:
            message: The user message (not used directly)
            user_id: The ID of the user (not used directly)
            context: Context containing the source agent response
            
        Returns:
            Dict containing the transformed response
        """
        # Get the source agent response from context
        if not context or "source_agent_response" not in context:
            # If no source response is provided, return a default message
            return {
                "response": "I'm not sure how to respond to that without more information.",
                "agent_type": "personality"
            }
        
        source_response = context["source_agent_response"]
        
        # Apply personality transformation
        transformed_response = self._transform_response(source_response)
        
        # Record the transformation
        self.record_tool_call("personality_transform", {
            "personality_type": self.personality_type,
            "original_length": len(source_response),
            "transformed_length": len(transformed_response)
        })
        
        return {
            "response": transformed_response,
            "agent_type": "personality"
        }
    
    def _transform_response(self, response: str) -> str:
        """Transform a response by applying personality traits.
        
        Args:
            response: The original response to transform
            
        Returns:
            Transformed response string
        """
        # Get personality traits
        personality = self.personalities.get(self.personality_type, self.personalities["friendly"])
        
        # Split response into paragraphs
        paragraphs = response.split('\n\n')
        transformed_paragraphs = []
        
        # Add a greeting to the first paragraph
        if paragraphs:
            greeting = random.choice(personality["greetings"])
            paragraphs[0] = f"{greeting} {paragraphs[0]}"
        
        # Transform each paragraph
        for i, paragraph in enumerate(paragraphs):
            # Skip empty paragraphs
            if not paragraph.strip():
                transformed_paragraphs.append(paragraph)
                continue
            
            # Add acknowledgment to the first paragraph if it's not a list item
            if i == 0 and not paragraph.strip().startswith(('•', '-', '*', '1.')):
                acknowledgment = random.choice(personality["acknowledgments"])
                paragraph = f"{acknowledgment}, {paragraph[0].lower() + paragraph[1:]}"
            
            # Add transitions to middle paragraphs
            elif i > 0 and i < len(paragraphs) - 1 and not paragraph.strip().startswith(('•', '-', '*', '1.')):
                if random.random() < 0.5:  # 50% chance to add a transition
                    transition = random.choice(personality["transitions"])
                    paragraph = f"{transition}, {paragraph[0].lower() + paragraph[1:]}"
            
            # Add fillers occasionally
            if random.random() < 0.3 and not paragraph.strip().startswith(('•', '-', '*', '1.')):
                filler = random.choice(personality["fillers"])
                words = paragraph.split()
                insert_position = min(3, len(words) - 1)
                words.insert(insert_position, filler)
                paragraph = ' '.join(words)
            
            # Convert periods to exclamations occasionally
            if random.random() < personality["exclamation_frequency"]:
                paragraph = re.sub(r'\.(?=\s|$)', '!', paragraph)
            
            transformed_paragraphs.append(paragraph)
        
        # Add a closing to the last paragraph if it's not a list
        if transformed_paragraphs and not transformed_paragraphs[-1].strip().startswith(('•', '-', '*', '1.')):
            closing = random.choice(personality["closings"])
            transformed_paragraphs[-1] = f"{transformed_paragraphs[-1]} {closing}"
        
        # Join paragraphs back together
        transformed_response = '\n\n'.join(transformed_paragraphs)
        
        # Add emojis occasionally
        if personality["emojis"] and random.random() < personality["emoji_frequency"]:
            emoji = random.choice(personality["emojis"])
            transformed_response = f"{transformed_response} {emoji}"
        
        return transformed_response
    
    def set_personality(self, personality_type: str) -> None:
        """Set the personality type.
        
        Args:
            personality_type: The type of personality to apply
        """
        if personality_type in self.personalities:
            self.personality_type = personality_type
            self.record_tool_call("set_personality", {"personality_type": personality_type})
        else:
            self.record_tool_call("set_personality_error", {
                "error": f"Unknown personality type: {personality_type}",
                "available_types": list(self.personalities.keys())
            })
