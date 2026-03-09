"""
Mental Health Support Agent
Provides empathetic support for emotional distress
"""
import re
import logging
from typing import Optional, Tuple, Dict, Any
from response_cache import ResponseCache

logger = logging.getLogger(__name__)


class MentalHealthAgent:
    """
    Detects emotional distress and provides supportive responses
    Integrates with Response Cache for fast path optimization
    """
    
    def __init__(self, response_cache: ResponseCache):
        """
        Initialize mental health support agent
        
        Args:
            response_cache: Response cache for caching supportive responses
        """
        self.response_cache = response_cache
        self.is_active = False
        
        # Emotional distress keywords
        self.distress_keywords = [
            r'\b(hopeless|helpless)\b',
            r'\b(anxious|anxiety|worried|worry)\b',
            r'\b(depressed|depression|sad|sadness)\b',
            r'\b(overwhelmed|too much|can\'t cope)\b',
            r'\b(stressed|stress|pressure)\b',
            r'\b(can\'t keep up|falling behind)\b',
            r'\b(exhausted|burned out|burnout)\b',
            r'\b(lonely|alone|isolated)\b',
            r'\b(scared|afraid|frightened|fear)\b',
        ]
        
        # Guided breathing exercise template
        self.breathing_exercise = (
            "Let's try a simple breathing exercise together. "
            "Take a slow, deep breath in through your nose for 4 counts... "
            "Hold it for 4 counts... "
            "Now breathe out slowly through your mouth for 4 counts... "
            "Let's do this a few more times. "
            "Focus on the rhythm of your breathing and how your body feels."
        )
    
    def detect_distress(self, text: str) -> bool:
        """
        Detect emotional distress keywords in text
        
        Args:
            text: User input text
            
        Returns:
            True if distress keywords detected
        """
        if not text or not text.strip():
            return False
        
        text_lower = text.lower().strip()
        
        for pattern in self.distress_keywords:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    def activate(self, text: str) -> bool:
        """
        Activate agent if distress detected
        
        Args:
            text: User input text
            
        Returns:
            True if agent was activated
        """
        if self.detect_distress(text):
            if not self.is_active:
                self.is_active = True
                logger.info("[Mental Health Agent] activated")
            return True
        return False
    
    def is_agent_active(self) -> bool:
        """
        Check if agent is currently active
        
        Returns:
            True if agent is active
        """
        return self.is_active
    
    def deactivate(self):
        """Deactivate agent (typically at session end)"""
        self.is_active = False
        logger.info("[Mental Health Agent] deactivated")
    
    def get_breathing_exercise(self) -> str:
        """
        Get guided breathing exercise template
        
        Returns:
            Breathing exercise instructions
        """
        return self.breathing_exercise
    
    def check_cache(self, text: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Check cache for similar emotional support queries
        
        Args:
            text: User input text
            context: Optional context dictionary for cache key
            
        Returns:
            Cached response if found, None otherwise
        """
        cached_response = self.response_cache.get(text, context)
        if cached_response:
            logger.info("[Mental Health Agent] cache hit for emotional support query")
            return cached_response
        return None
    
    def cache_response(self, text: str, response: str, context: Optional[Dict[str, Any]] = None):
        """
        Cache supportive response for future use
        
        Args:
            text: User input text
            response: Generated response
            context: Optional context dictionary for cache key
        """
        self.response_cache.put(text, response, context)
        logger.info("[Mental Health Agent] cached supportive response")
    
    def generate_supportive_prompt(self, text: str, user_history: Optional[str] = None) -> str:
        """
        Generate LLM prompt for supportive response
        
        Args:
            text: User input text
            user_history: Optional user history context
            
        Returns:
            Formatted prompt for LLM
        """
        prompt_parts = [
            "You are a compassionate AI health companion providing emotional support.",
            "Respond with empathy, warmth, and encouragement.",
            "DO NOT diagnose mental health conditions.",
            "DO NOT recommend specific medications or treatments.",
            "Focus on active listening, validation, and gentle guidance.",
            ""
        ]
        
        if user_history:
            prompt_parts.append(f"User history: {user_history}")
            prompt_parts.append("")
        
        prompt_parts.append(f"User: {text}")
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)
    
    def log_response_generated(self):
        """Log that supportive response was generated"""
        logger.info("[Mental Health Agent] supportive response generated")
    
    def should_offer_breathing_exercise(self, text: str) -> bool:
        """
        Determine if breathing exercise should be offered
        
        Args:
            text: User input text
            
        Returns:
            True if user accepts support or asks for help
        """
        text_lower = text.lower().strip()
        
        acceptance_patterns = [
            r'\b(yes|yeah|sure|okay|ok|please|help)\b',
            r'\b(i would|i\'d like|that would help)\b',
            r'\b(what can i do|how can i)\b',
        ]
        
        for pattern in acceptance_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
