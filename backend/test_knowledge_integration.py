"""
Integration test showing how Knowledge Specialist Agent integrates with other components.

This demonstrates the full flow:
1. User query comes in
2. Intent classifier detects SYMPTOM_CHECK or KNOWLEDGE_QUERY
3. Supervisor routes to Knowledge Agent
4. Knowledge Agent retrieves context and generates response
5. Response is cached for future queries
"""

import asyncio
import logging

from knowledge_agent import KnowledgeSpecialistAgent
from response_cache import ResponseCache
from intent_classifier import IntentClassifier, Intent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockLLMClient:
    """Mock LLM client for testing."""
    
    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """Generate a mock response based on the context."""
        # In real implementation, this would call Bedrock
        if "migraine" in prompt.lower():
            return ("Based on the medical information, migraines are characterized by intense, "
                   "throbbing pain usually on one side of the head. They can be accompanied by "
                   "nausea, sensitivity to light and sound, and visual disturbances. Common triggers "
                   "include stress, certain foods, and hormonal changes. If you're experiencing "
                   "frequent or severe headaches, it's important to consult with a healthcare provider.")
        elif "chest pain" in prompt.lower():
            return ("Chest pain can have many causes ranging from minor to serious. While not all "
                   "chest pain indicates a heart problem, it should be taken seriously. If you're "
                   "experiencing chest pain with difficulty breathing, sweating, or pain radiating "
                   "to your arm or jaw, seek emergency medical attention immediately.")
        else:
            return ("Based on the medical information provided, I can help you understand your symptoms. "
                   "However, for proper diagnosis and treatment, please consult with a healthcare professional.")


async def simulate_user_interaction():
    """Simulate a user interaction with the AI Health Companion."""
    
    print("\n" + "="*80)
    print("AI Health Companion - Knowledge Agent Integration Demo")
    print("="*80 + "\n")
    
    # Initialize components
    print("Initializing system components...")
    cache = ResponseCache(max_size=100, ttl_hours=24)
    intent_classifier = IntentClassifier()
    knowledge_agent = KnowledgeSpecialistAgent(response_cache=cache, chroma_persist_dir="./test_chroma_db")
    llm_client = MockLLMClient()
    
    # Initialize knowledge base
    print("Loading medical knowledge base...")
    await knowledge_agent.initialize(pdf_directory="knowledge")
    print("✓ System ready\n")
    
    # Simulate user queries
    user_queries = [
        "I've been having headaches with nausea for the past few days",
        "What are the symptoms of migraines?",
        "I have chest pain and trouble breathing",
        "What are the symptoms of migraines?",  # Repeat to test cache
    ]
    
    for i, query in enumerate(user_queries, 1):
        print(f"\n{'='*80}")
        print(f"User Query {i}: {query}")
        print('='*80)
        
        # Step 1: Intent Classification
        intent, confidence = intent_classifier.classify(query)
        print(f"\n[Supervisor] intent: {intent.value} (confidence: {confidence:.2f})")
        
        # Step 2: Route to appropriate agent
        if intent in [Intent.SYMPTOM_CHECK, Intent.KNOWLEDGE_QUERY]:
            print("[Supervisor] Routing to Knowledge Specialist Agent")
            
            # Step 3: Retrieve context
            print("[Knowledge Agent] retrieving medical context")
            chunks = await knowledge_agent.retrieve(query, n_results=3)
            print(f"[Knowledge Agent] Retrieved {len(chunks)} chunks")
            
            # Step 4: Generate response
            print("[LLM Agent] invoking bedrock")
            response = await knowledge_agent.generate_response(query, chunks, llm_client)
            
            print(f"\n[AI Response]:")
            print(f"{response}\n")
            
        elif intent == Intent.RISK_SYMPTOM:
            print("[Supervisor] Routing to Risk Escalation Agent")
            print("[Risk Agent] urgency level: EMERGENCY")
            print("\n[AI Response]:")
            print("Chest pain combined with difficulty breathing can sometimes indicate a serious "
                  "medical issue. I cannot provide medical advice, but those symptoms may require "
                  "immediate medical attention. If someone is experiencing this right now, it's "
                  "important to contact emergency services or seek medical care immediately.\n")
        
        else:
            print(f"[Supervisor] Routing to general handler for intent: {intent.value}")
    
    # Display final statistics
    print("\n" + "="*80)
    print("Session Statistics")
    print("="*80)
    cache.log_stats()
    print()


if __name__ == "__main__":
    asyncio.run(simulate_user_interaction())
