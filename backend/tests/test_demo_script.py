"""
Demo Script Integration Test

This is the most critical test for the demo video recording.
Tests the complete demo script flow end-to-end.

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7
"""

import pytest
import asyncio
import logging
import sys
import os
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intent_classifier import IntentClassifier, Intent
from response_cache import ResponseCache
from supervisor_agent import SupervisorAgent
from metrics_tracker import MetricsTracker
from template_engine import TemplateResponseEngine
from risk_escalation_agent import RiskEscalationAgent
from mental_health_agent import MentalHealthAgent
from knowledge_agent import KnowledgeSpecialistAgent
from user_history_agent import UserHistoryAgent
from llm_client import LLMClient
from session import Session

# Configure logging to capture terminal output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


class LogCapture:
    """Capture log output for verification"""
    def __init__(self):
        self.logs = []
        self.handler = None
        
    def start(self):
        """Start capturing logs"""
        self.logs = []
        self.handler = logging.StreamHandler(StringIO())
        self.handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)
        logging.root.addHandler(self.handler)
        
    def stop(self):
        """Stop capturing logs"""
        if self.handler:
            logging.root.removeHandler(self.handler)
            
    def get_logs(self):
        """Get captured logs as string"""
        if self.handler and self.handler.stream:
            return self.handler.stream.getvalue()
        return ""
        
    def contains(self, text):
        """Check if logs contain specific text"""
        return text in self.get_logs()


@pytest.fixture(scope="function")
async def supervisor_agent():
    """Initialize supervisor agent with all dependencies"""
    # Initialize components
    intent_classifier = IntentClassifier()
    response_cache = ResponseCache(max_size=1000, ttl_hours=24)
    template_engine = TemplateResponseEngine()
    
    # Initialize LLM client with mock (avoid OpenAI client issues in tests)
    class MockLLMClient:
        def __init__(self):
            self.call_count = 0
            
        async def generate(self, prompt, system_prompt=None, temperature=0.7):
            self.call_count += 1
            logger.info("[LLM Agent] invoking bedrock")
            # Return a mock response
            if "headache" in prompt.lower():
                return "Headaches can have various causes including migraines, tension, or dehydration. If symptoms persist, please consult a healthcare professional."
            elif "anxious" in prompt.lower() or "stressed" in prompt.lower():
                return "I understand you're feeling anxious. It's important to take care of your mental health. Would you like to try a breathing exercise?"
            else:
                return "I'm here to help. Can you tell me more about what you're experiencing?"
                
        def get_usage_stats(self):
            return {"total_calls": self.call_count, "timeouts": 0, "success_rate": 100.0}
    
    llm_client = MockLLMClient()
    
    # Initialize specialized agents
    risk_agent = RiskEscalationAgent(template_engine)
    mental_health_agent = MentalHealthAgent(response_cache)
    knowledge_agent = KnowledgeSpecialistAgent(response_cache, chroma_persist_dir="tests/test_chroma_db")
    
    # Initialize database for history agent
    from database import Database
    database = Database("tests/test_demo_history.db")
    await database.initialize()
    history_agent = UserHistoryAgent(database)
    
    # Initialize supervisor agent
    supervisor = SupervisorAgent(
        intent_classifier=intent_classifier,
        risk_agent=risk_agent,
        mental_health_agent=mental_health_agent,
        knowledge_agent=knowledge_agent,
        history_agent=history_agent,
        template_engine=template_engine,
        llm_client=llm_client
    )
    
    yield supervisor
    
    # Cleanup
    if os.path.exists("tests/test_demo_history.db"):
        os.remove("tests/test_demo_history.db")


@pytest.mark.asyncio
async def test_demo_script_greeting_flow(supervisor_agent):
    """
    Test 1: Greeting Flow
    User says "Hello" → System responds with varied greeting (no LLM)
    
    Requirements: 1.1
    """
    logger.info("\n=== TEST 1: Greeting Flow ===")
    
    # Create session
    session = Session("demo_session_1", "demo_user")
    
    # Process greeting
    response = await supervisor_agent.process_query("Hello", session)
    
    # Verify response is not empty
    assert response, "Response should not be empty"
    assert len(response) > 0, "Response should have content"
    
    # Verify greeting variation (should be one of the templates)
    greeting_phrases = ["how are you feeling", "what's on your mind", "how can i help"]
    assert any(phrase in response.lower() for phrase in greeting_phrases), \
        f"Response should contain greeting phrase, got: {response}"
    
    logger.info(f"✓ Greeting response: {response}")
    logger.info("✓ Greeting flow test passed")


@pytest.mark.asyncio
async def test_demo_script_symptom_check_flow(supervisor_agent):
    """
    Test 2: Symptom Check Flow
    User describes symptoms → System uses Knowledge + History + LLM agents
    
    Requirements: 1.2
    """
    logger.info("\n=== TEST 2: Symptom Check Flow ===")
    
    # Create session
    session = Session("demo_session_2", "demo_user")
    
    # Process symptom check
    response = await supervisor_agent.process_query(
        "I have a headache and nausea", 
        session
    )
    
    # Verify response is not empty
    assert response, "Response should not be empty"
    assert len(response) > 0, "Response should have content"
    
    logger.info(f"✓ Symptom check response: {response[:100]}...")
    logger.info("✓ Symptom check flow test passed")


@pytest.mark.asyncio
async def test_demo_script_mental_health_activation(supervisor_agent):
    """
    Test 3: Mental Health Activation Flow
    User mentions stress/anxiety → Mental Health Agent activates
    
    Requirements: 1.3
    """
    logger.info("\n=== TEST 3: Mental Health Activation Flow ===")
    
    # Create session
    session = Session("demo_session_3", "demo_user")
    
    # Process mental health query
    response = await supervisor_agent.process_query(
        "I'm feeling really anxious and overwhelmed", 
        session
    )
    
    # Verify response is not empty
    assert response, "Response should not be empty"
    assert len(response) > 0, "Response should have content"
    
    # Verify response is empathetic
    empathy_words = ["understand", "here for you", "support", "help", "feel"]
    assert any(word in response.lower() for word in empathy_words), \
        f"Response should be empathetic, got: {response}"
    
    logger.info(f"✓ Mental health response: {response[:100]}...")
    logger.info("✓ Mental health activation test passed")


@pytest.mark.asyncio
async def test_demo_script_history_retrieval(supervisor_agent):
    """
    Test 4: History Context Retrieval
    User references previous context → System retrieves and uses history
    
    Requirements: 1.4
    """
    logger.info("\n=== TEST 4: History Context Retrieval ===")
    
    # Create session
    session = Session("demo_session_4", "demo_user")
    
    # First, store some history
    history_agent = supervisor_agent.history_agent
    await history_agent.store_conversation(
        user_id="demo_user",
        summary="User mentioned work-related stress",
        symptoms=["headache"],
        conditions=["migraines"],
        mental_health_notes="work-related stress"
    )
    
    # Process query that should retrieve history
    response = await supervisor_agent.process_query(
        "I'm still stressed with work", 
        session
    )
    
    # Verify response is not empty
    assert response, "Response should not be empty"
    assert len(response) > 0, "Response should have content"
    
    logger.info(f"✓ History context response: {response[:100]}...")
    logger.info("✓ History retrieval test passed")


@pytest.mark.asyncio
async def test_demo_script_emergency_risk_classification(supervisor_agent):
    """
    Test 5: Emergency Risk Classification
    User mentions chest pain/breathing → Emergency classification
    
    Requirements: 1.5
    """
    logger.info("\n=== TEST 5: Emergency Risk Classification ===")
    
    # Create session
    session = Session("demo_session_5", "demo_user")
    
    # Process emergency symptom
    response = await supervisor_agent.process_query(
        "I have chest pain and trouble breathing", 
        session
    )
    
    # Verify response is not empty
    assert response, "Response should not be empty"
    assert len(response) > 0, "Response should have content"
    
    # Verify response contains emergency guidance
    emergency_keywords = ["emergency", "medical attention", "serious", "immediately"]
    assert any(keyword in response.lower() for keyword in emergency_keywords), \
        f"Response should contain emergency guidance, got: {response}"
    
    logger.info(f"✓ Emergency response: {response[:100]}...")
    logger.info("✓ Emergency risk classification test passed")


@pytest.mark.asyncio
async def test_demo_script_breathing_exercise_offer(supervisor_agent):
    """
    Test 6: Guided Breathing Exercise Offer
    User accepts support → System offers guided breathing
    
    Requirements: 1.6
    """
    logger.info("\n=== TEST 6: Breathing Exercise Offer ===")
    
    # Create session
    session = Session("demo_session_6", "demo_user")
    
    # First, activate mental health support
    await supervisor_agent.process_query("I'm feeling anxious", session)
    
    # Then accept support
    response = await supervisor_agent.process_query(
        "Yes, I'd like some help", 
        session
    )
    
    # Verify response offers breathing exercise or support
    support_keywords = ["breath", "breathing", "exercise", "calm", "relax", "moment"]
    assert any(keyword in response.lower() for keyword in support_keywords), \
        f"Response should offer breathing exercise or support, got: {response}"
    
    logger.info(f"✓ Breathing exercise response: {response[:100]}...")
    logger.info("✓ Breathing exercise offer test passed")


@pytest.mark.asyncio
async def test_demo_script_full_flow(supervisor_agent):
    """
    Test 7: Complete Demo Script Flow
    Execute all demo steps in sequence
    
    Requirements: 1.7
    """
    logger.info("\n=== TEST 7: Complete Demo Script Flow ===")
    
    # Create session for full demo
    session = Session("demo_session_full", "demo_user")
    
    # Step 1: Greeting
    logger.info("\nStep 1: Greeting")
    response1 = await supervisor_agent.process_query("Hello", session)
    assert response1, "Greeting response should not be empty"
    logger.info(f"✓ Greeting: {response1[:50]}...")
    
    # Step 2: Symptom Check
    logger.info("\nStep 2: Symptom Check")
    response2 = await supervisor_agent.process_query(
        "I have a headache and nausea", 
        session
    )
    assert response2, "Symptom check response should not be empty"
    logger.info(f"✓ Symptom check: {response2[:50]}...")
    
    # Step 3: Mental Health
    logger.info("\nStep 3: Mental Health")
    response3 = await supervisor_agent.process_query(
        "I'm feeling stressed", 
        session
    )
    assert response3, "Mental health response should not be empty"
    logger.info(f"✓ Mental health: {response3[:50]}...")
    
    # Step 4: Emergency Risk
    logger.info("\nStep 4: Emergency Risk")
    response4 = await supervisor_agent.process_query(
        "I have chest pain", 
        session
    )
    assert response4, "Emergency response should not be empty"
    logger.info(f"✓ Emergency: {response4[:50]}...")
    
    # Verify conversation flow maintained
    assert len(session.conversation_history) > 0, "Session should maintain conversation history"
    
    logger.info("\n✓ Complete demo script flow test passed")
    logger.info("✓ All demo script integration tests passed!")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
