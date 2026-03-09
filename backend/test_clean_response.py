"""
Test cleaned LLM responses
"""
import asyncio
import os
from dotenv import load_dotenv
from llm_client import LLMClient

load_dotenv()

async def test_responses():
    print("Testing cleaned LLM responses...")
    
    client = LLMClient(
        aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region=os.getenv("AWS_REGION", "us-east-1"),
        model="meta.llama3-8b-instruct-v1:0",
        timeout=10
    )
    
    # Test 1: Mental health query
    print("\n=== Test 1: Mental Health ===")
    system_prompt = (
        "You are a compassionate AI health companion providing emotional support. "
        "Respond with empathy and warmth in 2-3 sentences. "
        "DO NOT diagnose mental health conditions. "
        "DO NOT recommend specific medications or treatments. "
        "DO NOT include multiple choice questions, code, or examples. "
        "Focus on active listening, validation, and gentle guidance."
    )
    
    response = await client.generate(
        "I'm feeling really stressed with work",
        system_prompt=system_prompt,
        temperature=0.7
    )
    print(f"Response: {response}")
    
    # Test 2: Symptom check
    print("\n=== Test 2: Symptom Check ===")
    system_prompt = (
        "You are a compassionate AI health companion. "
        "Provide brief, helpful, conversational responses (2-3 sentences maximum). "
        "Do not diagnose conditions or recommend specific medications. "
        "Do not include multiple choice questions, code, or training examples. "
        "Be warm, empathetic, and supportive. "
        "Respond directly to the user's question."
    )
    
    response = await client.generate(
        "I have a headache and nausea",
        system_prompt=system_prompt,
        temperature=0.7
    )
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_responses())
