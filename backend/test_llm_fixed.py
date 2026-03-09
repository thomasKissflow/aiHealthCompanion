"""
Test the fixed LLM client
"""
import asyncio
import os
from dotenv import load_dotenv
from llm_client import LLMClient

load_dotenv()

async def test_llm():
    print("Testing fixed LLM client...")
    
    client = LLMClient(
        aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region=os.getenv("AWS_REGION", "us-east-1"),
        model="meta.llama3-8b-instruct-v1:0",
        timeout=5
    )
    
    # Test 1: Simple query
    print("\n=== Test 1: Simple greeting ===")
    response = await client.generate("Say hello in one sentence")
    print(f"Response: {response}")
    
    # Test 2: Medical query
    print("\n=== Test 2: Medical query ===")
    response = await client.generate(
        "What are common symptoms of a migraine?",
        system_prompt="You are a helpful medical assistant. Provide brief, accurate information."
    )
    print(f"Response: {response}")
    
    # Test 3: Stats
    print("\n=== Usage Stats ===")
    stats = client.get_usage_stats()
    print(f"Total calls: {stats['total_calls']}")
    print(f"Timeouts: {stats['timeouts']}")
    print(f"Success rate: {stats['success_rate']:.1f}%")

if __name__ == "__main__":
    asyncio.run(test_llm())
