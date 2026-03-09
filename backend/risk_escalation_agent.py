"""
Risk Escalation Agent
Fast path rule-based risk detection and classification
"""
import re
import logging
from enum import Enum
from typing import Tuple
from template_engine import TemplateResponseEngine, UrgencyLevel

logger = logging.getLogger(__name__)


class RiskEscalationAgent:
    """
    Rule-based risk detection and urgency classification
    Fast path processing without LLM (100ms target)
    """
    
    def __init__(self, template_engine: TemplateResponseEngine):
        """
        Initialize risk escalation agent
        
        Args:
            template_engine: Template response engine for responses
        """
        self.template_engine = template_engine
        
        # Emergency symptom patterns
        self.emergency_patterns = [
            r'\b(chest pain|heart attack|crushing chest|chest pressure)\b',
            r'\b(can\'t breathe|cannot breathe|difficulty breathing|trouble breathing)\b',
            r'\b(shortness of breath|gasping for air|choking)\b',
            r'\b(severe bleeding|heavy bleeding|bleeding heavily)\b',
            r'\b(stroke|seizure|convulsion|unconscious|unresponsive)\b',
            r'\b(severe head injury|head trauma)\b',
            r'\b(suicide|suicidal|kill myself|end my life)\b',
        ]
        
        # Professional care patterns
        self.professional_patterns = [
            r'\b(persistent|chronic|ongoing|constant|continuous)\b',
            r'\b(worsening|getting worse|deteriorating)\b',
            r'\b(severe|intense|extreme|unbearable)\b',
            r'\b(high fever|fever over|temperature over)\b',
            r'\b(vomiting blood|blood in stool|blood in urine)\b',
        ]
        
        # Monitor patterns
        self.monitor_patterns = [
            r'\b(mild|slight|minor|occasional)\b',
            r'\b(sometimes|occasionally|now and then)\b',
            r'\b(improving|getting better|feeling better)\b',
        ]
    
    def classify_urgency(self, text: str) -> Tuple[UrgencyLevel, str]:
        """
        Classify urgency using rule-based pattern matching
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (UrgencyLevel, template_response)
        """
        if not text or not text.strip():
            return UrgencyLevel.NONE, ""
        
        text_lower = text.lower().strip()
        
        logger.info("[Risk Agent] evaluating symptoms")
        
        # Check emergency patterns first (highest priority)
        for pattern in self.emergency_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"[Risk Agent] urgency level: {UrgencyLevel.EMERGENCY.value}")
                response = self.template_engine.get_risk_response(UrgencyLevel.EMERGENCY)
                return UrgencyLevel.EMERGENCY, response
        
        # Check professional care patterns
        for pattern in self.professional_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"[Risk Agent] urgency level: {UrgencyLevel.PROFESSIONAL.value}")
                response = self.template_engine.get_risk_response(UrgencyLevel.PROFESSIONAL)
                return UrgencyLevel.PROFESSIONAL, response
        
        # Check monitor patterns
        for pattern in self.monitor_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"[Risk Agent] urgency level: {UrgencyLevel.MONITOR.value}")
                response = self.template_engine.get_risk_response(UrgencyLevel.MONITOR)
                return UrgencyLevel.MONITOR, response
        
        # No specific risk pattern detected
        return UrgencyLevel.NONE, ""
    
    def is_emergency(self, text: str) -> bool:
        """
        Quick check if text contains emergency symptoms
        
        Args:
            text: User input text
            
        Returns:
            True if emergency symptoms detected
        """
        urgency, _ = self.classify_urgency(text)
        return urgency == UrgencyLevel.EMERGENCY
    
    def get_response(self, text: str) -> str:
        """
        Get risk response for text
        
        Args:
            text: User input text
            
        Returns:
            Risk response or empty string if no risk detected
        """
        _, response = self.classify_urgency(text)
        return response
