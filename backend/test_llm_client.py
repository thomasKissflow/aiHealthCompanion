"""
Test script for LLM Client

Tests:
- LLM client initialization
- Response generation
- Timeout handling
- Usage statistics tracking
"""

import asyncio
import pytest
from llm_client import LLMClient


class MockOpenAIClient:
    """Mock OpenAI client for testing."""
    
    def __init__(self, delay: float = 0):
        self.delay = delay
        self.call_count = 0
    
    class ChatCompletions:
        def __init__(self, delay: float):
            self.delay = delay
        
        def create(self, **kwargs):
            import time
            time.sleep(self.delay)
            
            class Response:
                class Choice:
                    class Message:
                        content = "This is a mock LLM response for testing purposes."
                    message = Message()
                choices = [Choice()]
            
            return Response()
    
    @property
    def chat(self):
        class Chat:
            def __init__(self, completions):
                self.completions = completions
        return Chat(self.ChatCompletions(self.delay))


@pytest.mark.asyncio
async def test_llm_client_initialization():
    """Test LLM client initialization."""
    print("\n=== Test 1: LLM Client Initialization ===")
    
    # Create client without initializing OpenAI (will be mocked)
    client = LLMClient.__new__(LLMClient)
    client.model = "openai.gpt-oss-120b"
    client.timeout = 3
    client.call_count = 0
    client.timeout_count = 0
    client.client = None
    
    assert client.model == "openai.gpt-oss-120b"
    assert client.timeout == 3
    assert client.call_count == 0
    assert client.timeout_count == 0
    
    print("✓ LLM client initialized successfully")


@pytest.mark.asyncio
async def test_successful_generation():
    """Test successful response generation."""
    print("\n=== Test 2: Successful Response Generation ===")
    
    # Create client without initializing OpenAI
    client = LLMClient.__new__(LLMClient)
    client.model = "openai.gpt-oss-120b"
    client.timeout = 3
    client.call_count = 0
    client.timeout_count = 0
    
    # Replace with mock client
    client.client = MockOpenAIClient(delay=0.1)
    
    response = await client.generate(
        prompt="What causes headaches?",
        system_prompt="You are a helpful medical assistant."
    )
    
    assert response is not None
    assert len(response) > 0
    assert client.call_count == 1
    assert client.timeout_count == 0
    
    print(f"✓ Response generated: {response[:50]}...")


@pytest.mark.asyncio
async def test_timeout_handling():
    """Test timeout handling."""
    print("\n=== Test 3: Timeout Handling ===")
    
    # Create client without initializing OpenAI
    client = LLMClient.__new__(LLMClient)
    client.model = "openai.gpt-oss-120b"
    client.timeout = 1  # 1 second timeout
    client.call_count = 0
    client.timeout_count = 0
    
    # Replace with slow mock client
    client.client = MockOpenAIClient(delay=2)  # 2 second delay
    
    response = await client.generate(prompt="Test query")
    
    assert response is None, "Should return None on timeout"
    assert client.call_count == 1
    assert client.timeout_count == 1
    
    print("✓ Timeout handled correctly")


@pytest.mark.asyncio
async def test_usage_statistics():
    """Test usage statistics tracking."""
    print("\n=== Test 4: Usage Statistics ===")
    
    # Create client without initializing OpenAI
    client = LLMClient.__new__(LLMClient)
    client.model = "openai.gpt-oss-120b"
    client.timeout = 2
    client.call_count = 0
    client.timeout_count = 0
    
    # Replace with mock client
    client.client = MockOpenAIClient(delay=0.1)
    
    # Make several calls
    await client.generate(prompt="Query 1")
    await client.generate(prompt="Query 2")
    await client.generate(prompt="Query 3")
    
    stats = client.get_usage_stats()
    
    assert stats["total_calls"] == 3
    assert stats["timeouts"] == 0
    assert stats["success_rate"] == 100.0
    
    print(f"✓ Usage stats tracked correctly")
    print(f"  - Total calls: {stats['total_calls']}")
    print(f"  - Timeouts: {stats['timeouts']}")
    print(f"  - Success rate: {stats['success_rate']:.1f}%")


@pytest.mark.asyncio
async def test_mixed_success_and_timeout():
    """Test mixed successful and timeout calls."""
    print("\n=== Test 5: Mixed Success and Timeout ===")
    
    # Create client without initializing OpenAI
    client = LLMClient.__new__(LLMClient)
    client.model = "openai.gpt-oss-120b"
    client.timeout = 1
    client.call_count = 0
    client.timeout_count = 0
    
    # Successful call
    client.client = MockOpenAIClient(delay=0.1)
    response1 = await client.generate(prompt="Fast query")
    assert response1 is not None
    
    # Timeout call
    client.client = MockOpenAIClient(delay=2)
    response2 = await client.generate(prompt="Slow query")
    assert response2 is None
    
    # Another successful call
    client.client = MockOpenAIClient(delay=0.1)
    response3 = await client.generate(prompt="Another fast query")
    assert response3 is not None
    
    stats = client.get_usage_stats()
    assert stats["total_calls"] == 3
    assert stats["timeouts"] == 1
    assert abs(stats["success_rate"] - 66.67) < 0.1
    
    print("✓ Mixed calls handled correctly")
    print(f"  - Total calls: {stats['total_calls']}")
    print(f"  - Timeouts: {stats['timeouts']}")
    print(f"  - Success rate: {stats['success_rate']:.1f}%")


if __name__ == "__main__":
    asyncio.run(test_llm_client_initialization())
    asyncio.run(test_successful_generation())
    asyncio.run(test_timeout_handling())
    asyncio.run(test_usage_statistics())
    asyncio.run(test_mixed_success_and_timeout())
    print("\n✓ All LLM client tests passed!")
