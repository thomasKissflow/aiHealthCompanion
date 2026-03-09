"""
Intent Classifier
Fast pattern-based intent classification without LLM
"""
import re
import logging
from enum import Enum
from typing import Tuple

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Intent categories for user queries"""
    GREETING = "greeting"
    FAREWELL = "farewell"
    SYMPTOM_CHECK = "symptom_check"
    MENTAL_HEALTH = "mental_health"
    RISK_SYMPTOM = "risk_symptom"
    KNOWLEDGE_QUERY = "knowledge_query"
    ACKNOWLEDGMENT = "acknowledgment"
    UNKNOWN = "unknown"


class IntentClassifier:
    """
    Pattern-based intent classifier using regex
    Fast classification without LLM (2ms target)
    """
    
    def __init__(self):
        """Initialize intent patterns"""
        self.patterns = {
            Intent.GREETING: [
                r'\b(hello|hi|hey|good morning|good afternoon|good evening|greetings)\b',
                r'^(hi|hello|hey)[\s\.,!?]*$',
            ],
            Intent.FAREWELL: [
                r'\b(bye|goodbye|good bye|see you|farewell|take care|gotta go|have to go)\b',
                r'\b(thanks for your help|thank you for your help|thanks for helping|appreciate your help)\b',
                r'\b(that\'s all|that is all|i\'m done|im done|all set)\b',
                r'^(bye|goodbye|thanks|thank you)[\s\.,!?]*$',
            ],
            Intent.RISK_SYMPTOM: [
                r'\b(chest pain|heart attack|can\'t breathe|difficulty breathing|severe bleeding)\b',
                r'\b(trouble breathing|shortness of breath|crushing chest|chest pressure)\b',
                r'\b(stroke|seizure|unconscious|unresponsive)\b',
            ],
            Intent.MENTAL_HEALTH: [
                r'\b(anxious|anxiety|depressed|depression|overwhelmed|hopeless|stressed)\b',
                r'\b(too much|can\'t keep up|breaking down|panic|worried|scared)\b',
                r'\b(mental health|emotional|feeling down|sad|lonely)\b',
            ],
            Intent.SYMPTOM_CHECK: [
                r'\b(headache|nausea|pain|dizzy|fever|cough|cold|flu|sick)\b',
                r'\b(ache|aching|hurt|hurting|sore|tired|fatigue|weak)\b',
                r'\b(symptom|symptoms|feeling|not well|unwell)\b',
                r'\b(migraine|stomach|back pain|joint|muscle)\b',
            ],
            Intent.KNOWLEDGE_QUERY: [
                r'^(what|why|how|when|where|who)\b',
                r'\b(tell me about|explain|can you|information about)\b',
                r'\b(information|details|learn|know about|understand)\b',
            ],
            Intent.ACKNOWLEDGMENT: [
                r'\b(okay|ok|yes|yeah|sure|thanks|thank you|got it|understood)\b',
                r'^(ok|okay|yes|yeah|sure|thanks)[\s\.,!?]*$',
                r'\b(alright|fine|good|great)\b',
            ],
        }
    
    def classify(self, text: str) -> Tuple[Intent, float]:
        """
        Classify user intent using pattern matching
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (Intent, confidence_score)
        """
        if not text or not text.strip():
            return Intent.UNKNOWN, 0.0
        
        text_lower = text.lower().strip()
        
        # Check each intent in priority order
        # Risk symptoms have highest priority
        for intent in [Intent.RISK_SYMPTOM, Intent.FAREWELL, Intent.MENTAL_HEALTH, Intent.GREETING, 
                       Intent.ACKNOWLEDGMENT, Intent.SYMPTOM_CHECK, Intent.KNOWLEDGE_QUERY]:
            patterns = self.patterns.get(intent, [])
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    confidence = self._calculate_confidence(text_lower, pattern)
                    logger.info(f"[Supervisor] intent: {intent.value}")
                    return intent, confidence
        
        # No pattern matched
        logger.info(f"[Supervisor] intent: {Intent.UNKNOWN.value}")
        return Intent.UNKNOWN, 0.0
    
    def _calculate_confidence(self, text: str, pattern: str) -> float:
        """
        Calculate confidence score for pattern match
        
        Args:
            text: Input text
            pattern: Matched regex pattern
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Simple confidence based on match quality
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return 0.0
        
        # Higher confidence for exact matches
        matched_text = match.group(0)
        if matched_text.lower() == text.lower():
            return 1.0
        
        # Medium confidence for partial matches
        match_ratio = len(matched_text) / len(text)
        return min(0.5 + match_ratio, 0.95)
    
    def get_confidence(self, text: str, intent: Intent) -> float:
        """
        Get confidence score for specific intent
        
        Args:
            text: Input text
            intent: Intent to check
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        classified_intent, confidence = self.classify(text)
        if classified_intent == intent:
            return confidence
        return 0.0
