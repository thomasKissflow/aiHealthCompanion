"""
Template Response Engine
Pre-formatted responses for fast path (no LLM needed)
"""
import random
import logging
from typing import Dict, List
from enum import Enum

logger = logging.getLogger(__name__)


class UrgencyLevel(Enum):
    """Medical urgency classification"""
    EMERGENCY = "EMERGENCY"
    PROFESSIONAL = "PROFESSIONAL"
    MONITOR = "MONITOR"
    NONE = "NONE"


class TemplateResponseEngine:
    """
    Manages template-based responses for fast path
    Provides varied responses without LLM calls
    """
    
    def __init__(self):
        """Initialize template responses"""
        self.greeting_index = 0
        
        # Greeting templates with variations
        self.greetings = [
            "Hi there, I'm glad you reached out. How are you feeling today?",
            "Hello! What's on your mind?",
            "Hey! How can I help you today?",
        ]
        
        # Farewell templates with variations
        self.farewells = [
            "Take care! Feel free to reach out anytime you need support.",
            "Goodbye! Remember, I'm here whenever you need to talk about your health.",
            "Thanks for chatting with me. Wishing you good health and wellness!",
            "You're very welcome! Take care of yourself, and don't hesitate to come back if you need anything.",
            "I'm glad I could help. Stay well, and reach out anytime!",
        ]
        
        # Acknowledgment templates
        self.acknowledgments = [
            "I understand",
            "Got it",
            "Okay",
            "Thanks for sharing that",
        ]
        
        # Immediate feedback phrases (while processing)
        self.immediate_feedback = [
            "Let me check that for you",
            "One moment please",
            "Looking that up now",
        ]
        
        # Risk classification templates
        self.risk_templates = {
            UrgencyLevel.EMERGENCY: (
                "Chest pain combined with difficulty breathing can sometimes indicate a serious medical issue. "
                "I cannot provide medical advice, but those symptoms may require immediate medical attention. "
                "If someone is experiencing this right now, it's important to contact emergency services or "
                "seek medical care immediately."
            ),
            UrgencyLevel.PROFESSIONAL: (
                "I recommend scheduling an appointment with your doctor within the next few days."
            ),
            UrgencyLevel.MONITOR: (
                "Keep an eye on these symptoms. If they worsen, please consult a healthcare professional."
            ),
        }
    
    def get_greeting(self) -> str:
        """
        Get varied greeting (rotates through options)
        
        Returns:
            Greeting string
        """
        greeting = self.greetings[self.greeting_index]
        self.greeting_index = (self.greeting_index + 1) % len(self.greetings)
        logger.info("[LLM Agent] skipping model call")
        return greeting
    
    def get_farewell(self) -> str:
        """
        Get varied farewell response
        
        Returns:
            Farewell string
        """
        logger.info("[LLM Agent] skipping model call")
        return random.choice(self.farewells)
    
    def get_acknowledgment(self) -> str:
        """
        Get random acknowledgment
        
        Returns:
            Acknowledgment string
        """
        return random.choice(self.acknowledgments)
    
    def get_immediate_feedback(self) -> str:
        """
        Get random immediate feedback phrase
        
        Returns:
            Immediate feedback string
        """
        return random.choice(self.immediate_feedback)
    
    def get_risk_response(self, level: UrgencyLevel) -> str:
        """
        Get template response for risk level
        
        Args:
            level: Urgency level
            
        Returns:
            Risk response template
        """
        return self.risk_templates.get(level, "")
    
    def get_fallback_response(self) -> str:
        """
        Get fallback response for LLM timeout or error
        
        Returns:
            Fallback response string
        """
        return "I'm having trouble processing that right now. Could you rephrase your question?"
    
    def substitute_variables(self, template: str, variables: Dict[str, str]) -> str:
        """
        Substitute variables in template
        
        Args:
            template: Template string with {variable} placeholders
            variables: Dictionary of variable values
            
        Returns:
            Template with substituted values
        """
        try:
            return template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing variable in template: {e}")
            return template
