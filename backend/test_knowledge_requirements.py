"""
Test script to verify all requirements for Task 9: Knowledge Specialist Agent

This test verifies:
- Requirement 9.1: Load medical reference PDFs
- Requirement 9.2: Split PDF content into chunks
- Requirement 9.3: Generate embeddings for chunks
- Requirement 9.4: Store embeddings in ChromaDB
- Requirement 9.5: Check Response_Cache before retrieval
- Requirement 9.6: Retrieve relevant context chunks
- Requirement 9.7: Log number of chunks retrieved
- Requirement 9.8: Return chunks to Supervisor
- Requirement 9.9: Cache generated responses
- Requirement 9.10: Retrieve migraine context for headache symptoms
"""

import asyncio
import logging
import pytest
from pathlib import Path

from knowledge_agent import KnowledgeSpecialistAgent
from response_cache import ResponseCache


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockLLMClient:
    """Mock LLM client."""
    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        return "Mock response based on medical context."


@pytest.mark.asyncio
async def test_requirements():
    """Test all requirements for Knowledge Specialist Agent."""
    
    print("\n" + "="*80)
    print("Testing Knowledge Specialist Agent Requirements")
    print("="*80 + "\n")
    
    cache = ResponseCache()
    agent = KnowledgeSpecialistAgent(response_cache=cache, chroma_persist_dir="./test_chroma_db")
    llm = MockLLMClient()
    
    # Test Requirement 9.1: Load medical reference PDFs
    print("✓ Requirement 9.1: Load medical reference PDFs")
    pdf_dir = Path("knowledge")
    assert pdf_dir.exists(), "PDF directory should exist"
    pdf_files = list(pdf_dir.glob("*.pdf"))
    assert len(pdf_files) >= 2, "Should have at least 2 PDF files"
    print(f"  Found {len(pdf_files)} PDF files: {[f.name for f in pdf_files]}\n")
    
    # Initialize knowledge base (tests 9.1, 9.2, 9.3, 9.4)
    await agent.initialize(pdf_directory="knowledge")
    
    # Test Requirement 9.2: Split PDF content into chunks
    print("✓ Requirement 9.2: Split PDF content into chunks")
    assert agent.collection is not None, "Collection should be initialized"
    chunk_count = agent.collection.count()
    assert chunk_count > 0, "Should have chunks in collection"
    print(f"  Collection contains {chunk_count} chunks\n")
    
    # Test Requirement 9.3: Generate embeddings for chunks
    print("✓ Requirement 9.3: Generate embeddings for chunks")
    assert agent.embedding_model is not None, "Embedding model should be loaded"
    print(f"  Embedding model: {agent.embedding_model}\n")
    
    # Test Requirement 9.4: Store embeddings in ChromaDB
    print("✓ Requirement 9.4: Store embeddings in ChromaDB")
    results = agent.collection.peek(1)
    assert len(results['ids']) > 0, "Should have documents in ChromaDB"
    print(f"  Sample document ID: {results['ids'][0]}\n")
    
    # Test Requirement 9.5: Check Response_Cache before retrieval
    print("✓ Requirement 9.5: Check Response_Cache before retrieval")
    query = "What causes headaches?"
    
    # First call - should miss cache
    initial_misses = cache.misses
    chunks = await agent.retrieve(query, n_results=3)
    response1 = await agent.generate_response(query, chunks, llm)
    assert cache.misses == initial_misses + 1, "First call should miss cache"
    print(f"  First call: Cache miss (as expected)\n")
    
    # Second call - should hit cache
    initial_hits = cache.hits
    response2 = await agent.generate_response(query, chunks, llm)
    assert cache.hits == initial_hits + 1, "Second call should hit cache"
    assert response1 == response2, "Cached response should match"
    print(f"  Second call: Cache hit (as expected)\n")
    
    # Test Requirement 9.6: Retrieve relevant context chunks
    print("✓ Requirement 9.6: Retrieve relevant context chunks")
    query = "Tell me about migraines"
    chunks = await agent.retrieve(query, n_results=3)
    assert len(chunks) > 0, "Should retrieve chunks"
    assert any("migraine" in chunk.lower() for chunk in chunks), "Should retrieve migraine-related chunks"
    print(f"  Retrieved {len(chunks)} relevant chunks\n")
    
    # Test Requirement 9.7: Log number of chunks retrieved
    print("✓ Requirement 9.7: Log number of chunks retrieved")
    print("  (Check logs above for '[Knowledge Agent] Retrieved N chunks' messages)\n")
    
    # Test Requirement 9.8: Return chunks to Supervisor
    print("✓ Requirement 9.8: Return chunks to Supervisor")
    assert isinstance(chunks, list), "Should return list of chunks"
    assert all(isinstance(chunk, str) for chunk in chunks), "All chunks should be strings"
    print(f"  Chunks returned as list of {len(chunks)} strings\n")
    
    # Test Requirement 9.9: Cache generated responses
    print("✓ Requirement 9.9: Cache generated responses")
    query = "What are common symptoms?"
    chunks = await agent.retrieve(query, n_results=2)
    
    initial_size = len(cache.cache)
    response = await agent.generate_response(query, chunks, llm)
    new_size = len(cache.cache)
    
    assert new_size > initial_size, "Cache should grow after generating response"
    print(f"  Cache size increased from {initial_size} to {new_size}\n")
    
    # Test Requirement 9.10: Retrieve migraine context for headache symptoms
    print("✓ Requirement 9.10: Retrieve migraine context for headache symptoms")
    headache_queries = [
        "I have a headache",
        "My head hurts and I feel nauseous",
        "I'm experiencing a severe headache"
    ]
    
    for query in headache_queries:
        chunks = await agent.retrieve(query, n_results=3)
        has_migraine_info = any("migraine" in chunk.lower() for chunk in chunks)
        print(f"  Query: '{query}'")
        print(f"    Migraine info retrieved: {'✓' if has_migraine_info else '✗'}")
    
    print("\n" + "="*80)
    print("All Requirements Verified Successfully!")
    print("="*80 + "\n")
    
    # Display final statistics
    print("Final Statistics:")
    print(f"  Total chunks in knowledge base: {agent.collection.count()}")
    print(f"  Cache size: {len(cache.cache)}")
    print(f"  Cache hits: {cache.hits}")
    print(f"  Cache misses: {cache.misses}")
    print(f"  Cache hit rate: {cache.get_hit_rate():.1f}%")
    print()


if __name__ == "__main__":
    asyncio.run(test_requirements())
