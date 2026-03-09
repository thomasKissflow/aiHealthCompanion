"""
Test script for Knowledge Specialist Agent

Tests the initialization, PDF loading, embedding generation, and retrieval functionality.
"""

import asyncio
import logging
import pytest
from pathlib import Path

from knowledge_agent import KnowledgeSpecialistAgent
from response_cache import ResponseCache


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockLLMClient:
    """Mock LLM client for testing without actual Bedrock calls."""
    
    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """Mock generate method that returns a simple response."""
        return "Based on the medical information provided, headaches can have various causes including migraines, tension, and other factors. If symptoms persist, consult a healthcare provider."


@pytest.mark.asyncio
async def test_knowledge_agent():
    """Test the Knowledge Specialist Agent functionality."""
    
    print("\n" + "="*80)
    print("Testing Knowledge Specialist Agent")
    print("="*80 + "\n")
    
    # Initialize components
    print("1. Initializing Response Cache...")
    cache = ResponseCache(max_size=100, ttl_hours=24)
    print("   ✓ Cache initialized\n")
    
    # Initialize Knowledge Agent
    print("2. Initializing Knowledge Specialist Agent...")
    agent = KnowledgeSpecialistAgent(
        response_cache=cache,
        chroma_persist_dir="./test_chroma_db"
    )
    print("   ✓ Agent initialized\n")
    
    # Load knowledge base
    print("3. Loading knowledge base from PDFs...")
    await agent.initialize(pdf_directory="knowledge")
    print("   ✓ Knowledge base loaded\n")
    
    # Test retrieval
    print("4. Testing knowledge retrieval...")
    
    test_queries = [
        "What are the symptoms of migraines?",
        "What causes headaches and nausea?",
        "Tell me about chest pain",
        "What should I do if I have difficulty breathing?"
    ]
    
    mock_llm = MockLLMClient()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query}")
        print("   " + "-"*70)
        
        # Retrieve context chunks
        chunks = await agent.retrieve(query, n_results=3)
        print(f"   Retrieved {len(chunks)} chunks:")
        for j, chunk in enumerate(chunks, 1):
            preview = chunk[:100].replace('\n', ' ') + "..." if len(chunk) > 100 else chunk.replace('\n', ' ')
            print(f"     {j}. {preview}")
        
        # Generate response (first time - should call LLM)
        print(f"\n   Generating response (first time)...")
        response = await agent.generate_response(query, chunks, mock_llm)
        print(f"   Response: {response[:150]}...")
        
        # Generate response (second time - should use cache)
        print(f"\n   Generating response (second time - should use cache)...")
        response_cached = await agent.generate_response(query, chunks, mock_llm)
        print(f"   Response: {response_cached[:150]}...")
        
        if response == response_cached:
            print("   ✓ Cache working correctly!")
        else:
            print("   ✗ Cache not working as expected")
    
    print("\n" + "="*80)
    print("Testing Complete!")
    print("="*80 + "\n")
    
    # Display cache statistics
    print("Cache Statistics:")
    print(f"  Total queries: {cache.hits + cache.misses}")
    print(f"  Cache hits: {cache.hits}")
    print(f"  Cache misses: {cache.misses}")
    print(f"  Hit rate: {cache.get_hit_rate():.1f}%")
    print()


@pytest.mark.asyncio
async def test_specific_migraine_query():
    """Test that the agent retrieves migraine information when user mentions headache."""
    
    print("\n" + "="*80)
    print("Testing Migraine Context Retrieval (Requirement 9.10)")
    print("="*80 + "\n")
    
    cache = ResponseCache()
    agent = KnowledgeSpecialistAgent(response_cache=cache, chroma_persist_dir="./test_chroma_db")
    
    # Agent should already be initialized from previous test
    # If not, initialize it
    if not agent.collection or agent.collection.count() == 0:
        await agent.initialize(pdf_directory="knowledge")
    
    # Test query mentioning headache symptoms
    query = "I have a headache and feel nauseous"
    print(f"Query: {query}\n")
    
    chunks = await agent.retrieve(query, n_results=3)
    
    print(f"Retrieved {len(chunks)} chunks:\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}:")
        print(chunk[:300] + "...\n" if len(chunk) > 300 else chunk + "\n")
    
    # Check if migraine information is in the retrieved chunks
    migraine_mentioned = any("migraine" in chunk.lower() for chunk in chunks)
    
    if migraine_mentioned:
        print("✓ SUCCESS: Migraine information retrieved when user mentions headache symptoms")
    else:
        print("✗ WARNING: Migraine information not found in retrieved chunks")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_knowledge_agent())
    asyncio.run(test_specific_migraine_query())
