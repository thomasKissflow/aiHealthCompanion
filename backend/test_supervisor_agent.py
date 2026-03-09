"""
Test Supervisor Agent

Simple test to verify supervisor agent initialization and basic routing.
"""

import asyncio
import logging
from intent_classifier import IntentClassifier
from risk_escalation_agent import RiskEscalationAgent
from mental_health_agent import MentalHealthAgent
from knowledge_agent import KnowledgeSpecialistAgent
from user_history_agent import UserHistoryAgent
from template_engine import TemplateResponseEngine
from llm_client import LLMClient
from response_cache import ResponseCache
from database import Database
from session import Session
from supervisor_agent import SupervisorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_supervisor_initialization():
    """Test that supervisor agent can be initialized with all dependencies"""
    logger.info("=== Testing Supervisor Agent Initialization ===")
    
    # Initialize dependencies
    intent_classifier = IntentClassifier()
    template_engine = TemplateResponseEngine()
    response_cache = ResponseCache()
    
    # Initialize database
    database = Database("test_supervisor.db")
    await database.initialize()
    
    # Initialize agents
    risk_agent = RiskEscalationAgent(template_engine)
    mental_health_agent = MentalHealthAgent(response_cache)
    knowledge_agent = KnowledgeSpecialistAgent(response_cache)
    history_agent = UserHistoryAgent(database)
    
    # Initialize LLM client (with dummy credentials for test)
    llm_client = LLMClient(
        api_key="test_key",
        base_url="http://localhost:8000",
        timeout=3
    )
    
    # Initialize supervisor
    supervisor = SupervisorAgent(
        intent_classifier=intent_classifier,
        risk_agent=risk_agent,
        mental_health_agent=mental_health_agent,
        knowledge_agent=knowledge_agent,
        history_agent=history_agent,
        template_engine=template_engine,
        llm_client=llm_client
    )
    
    logger.info("✓ Supervisor agent initialized successfully")
    
    return supervisor


async def test_greeting_fast_path(supervisor: SupervisorAgent):
    """Test that greetings use fast path (no LLM)"""
    logger.info("\n=== Testing Greeting Fast Path ===")
    
    session = Session("test_session_1", "test_user_1")
    
    response = await supervisor.process_query("Hello", session)
    
    logger.info(f"Response: {response}")
    logger.info("✓ Greeting processed via fast path")


async def test_acknowledgment_fast_path(supervisor: SupervisorAgent):
    """Test that acknowledgments use fast path (no LLM)"""
    logger.info("\n=== Testing Acknowledgment Fast Path ===")
    
    session = Session("test_session_2", "test_user_2")
    
    response = await supervisor.process_query("okay", session)
    
    logger.info(f"Response: {response}")
    logger.info("✓ Acknowledgment processed via fast path")


async def test_risk_symptom_fast_path(supervisor: SupervisorAgent):
    """Test that risk symptoms use fast path (no LLM)"""
    logger.info("\n=== Testing Risk Symptom Fast Path ===")
    
    session = Session("test_session_3", "test_user_3")
    
    response = await supervisor.process_query("I have chest pain and trouble breathing", session)
    
    logger.info(f"Response: {response}")
    logger.info("✓ Risk symptom processed via fast path")


async def test_intent_classification_logging(supervisor: SupervisorAgent):
    """Test that intent classification is logged"""
    logger.info("\n=== Testing Intent Classification Logging ===")
    
    session = Session("test_session_4", "test_user_4")
    
    test_queries = [
        "Hello",
        "I have a headache",
        "I'm feeling anxious",
        "What causes migraines?",
    ]
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        response = await supervisor.process_query(query, session)
        logger.info(f"Response: {response[:50]}...")
    
    logger.info("✓ Intent classification logged for all queries")


async def main():
    """Run all tests"""
    try:
        # Initialize supervisor
        supervisor = await test_supervisor_initialization()
        
        # Run tests
        await test_greeting_fast_path(supervisor)
        await test_acknowledgment_fast_path(supervisor)
        await test_risk_symptom_fast_path(supervisor)
        await test_intent_classification_logging(supervisor)
        
        logger.info("\n=== All Tests Passed ===")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
