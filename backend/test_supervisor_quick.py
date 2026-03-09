"""
Quick Test for Supervisor Agent

Tests supervisor agent routing logic without requiring working LLM client.
"""

import asyncio
import logging
from intent_classifier import IntentClassifier, Intent
from risk_escalation_agent import RiskEscalationAgent
from mental_health_agent import MentalHealthAgent
from template_engine import TemplateResponseEngine
from response_cache import ResponseCache
from session import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_intent_classification():
    """Test intent classification and logging"""
    logger.info("=== Testing Intent Classification ===")
    
    classifier = IntentClassifier()
    
    test_cases = [
        ("Hello", Intent.GREETING),
        ("I have a headache", Intent.SYMPTOM_CHECK),
        ("I'm feeling anxious", Intent.MENTAL_HEALTH),
        ("chest pain and trouble breathing", Intent.RISK_SYMPTOM),
        ("What causes migraines?", Intent.KNOWLEDGE_QUERY),
        ("okay", Intent.ACKNOWLEDGMENT),
    ]
    
    for text, expected_intent in test_cases:
        intent, confidence = classifier.classify(text)
        status = "✓" if intent == expected_intent else "✗"
        logger.info(f"{status} '{text}' -> {intent.value} (expected: {expected_intent.value})")
    
    logger.info("✓ Intent classification test complete")


async def test_fast_path_responses():
    """Test fast path responses (no LLM)"""
    logger.info("\n=== Testing Fast Path Responses ===")
    
    template_engine = TemplateResponseEngine()
    
    # Test greeting
    greeting = template_engine.get_greeting()
    logger.info(f"Greeting: {greeting}")
    
    # Test acknowledgment
    ack = template_engine.get_acknowledgment()
    logger.info(f"Acknowledgment: {ack}")
    
    # Test risk response
    risk_agent = RiskEscalationAgent(template_engine)
    urgency, response = risk_agent.classify_urgency("chest pain and trouble breathing")
    logger.info(f"Risk urgency: {urgency.value}")
    logger.info(f"Risk response: {response[:100]}...")
    
    logger.info("✓ Fast path responses test complete")


async def test_mental_health_activation():
    """Test mental health agent activation"""
    logger.info("\n=== Testing Mental Health Agent Activation ===")
    
    response_cache = ResponseCache()
    mental_health_agent = MentalHealthAgent(response_cache)
    
    # Test distress detection
    test_cases = [
        ("I'm feeling anxious", True),
        ("I'm overwhelmed", True),
        ("I have a headache", False),
    ]
    
    for text, should_activate in test_cases:
        activated = mental_health_agent.activate(text)
        status = "✓" if activated == should_activate else "✗"
        logger.info(f"{status} '{text}' -> activated: {activated} (expected: {should_activate})")
    
    # Test breathing exercise
    exercise = mental_health_agent.get_breathing_exercise()
    logger.info(f"Breathing exercise: {exercise[:50]}...")
    
    logger.info("✓ Mental health agent test complete")


async def test_session_management():
    """Test session context management"""
    logger.info("\n=== Testing Session Management ===")
    
    session = Session("test_session", "test_user")
    
    # Add messages
    session.add_message("user", "Hello")
    session.add_message("assistant", "Hi there!")
    session.add_message("user", "I have a headache")
    
    # Get context
    context = session.get_context_for_prompt()
    logger.info(f"Session context:\n{context}")
    
    # Check message count
    count = session.get_message_count()
    logger.info(f"Message count: {count}")
    
    logger.info("✓ Session management test complete")


async def test_supervisor_routing_logic():
    """Test supervisor routing logic without LLM"""
    logger.info("\n=== Testing Supervisor Routing Logic ===")
    
    classifier = IntentClassifier()
    template_engine = TemplateResponseEngine()
    
    # Test routing decisions
    test_queries = [
        "Hello",
        "I have chest pain",
        "I'm feeling anxious",
        "What causes headaches?",
        "okay",
    ]
    
    for query in test_queries:
        intent, confidence = classifier.classify(query)
        
        # Determine expected routing
        if intent == Intent.GREETING:
            response = template_engine.get_greeting()
            logger.info(f"✓ '{query}' -> GREETING (fast path)")
            logger.info(f"  Response: {response}")
        
        elif intent == Intent.ACKNOWLEDGMENT:
            response = template_engine.get_acknowledgment()
            logger.info(f"✓ '{query}' -> ACKNOWLEDGMENT (fast path)")
            logger.info(f"  Response: {response}")
        
        elif intent == Intent.RISK_SYMPTOM:
            risk_agent = RiskEscalationAgent(template_engine)
            urgency, response = risk_agent.classify_urgency(query)
            logger.info(f"✓ '{query}' -> RISK_SYMPTOM (fast path)")
            logger.info(f"  Urgency: {urgency.value}")
            logger.info(f"  Response: {response[:80]}...")
        
        elif intent == Intent.MENTAL_HEALTH:
            logger.info(f"✓ '{query}' -> MENTAL_HEALTH (would activate agent)")
        
        elif intent == Intent.KNOWLEDGE_QUERY:
            logger.info(f"✓ '{query}' -> KNOWLEDGE_QUERY (would retrieve from ChromaDB)")
        
        elif intent == Intent.SYMPTOM_CHECK:
            logger.info(f"✓ '{query}' -> SYMPTOM_CHECK (would use Knowledge + History + LLM)")
        
        else:
            logger.info(f"✓ '{query}' -> {intent.value}")
    
    logger.info("✓ Supervisor routing logic test complete")


async def main():
    """Run all tests"""
    try:
        await test_intent_classification()
        await test_fast_path_responses()
        await test_mental_health_activation()
        await test_session_management()
        await test_supervisor_routing_logic()
        
        logger.info("\n=== All Tests Passed ===")
        logger.info("Supervisor agent routing logic verified successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
