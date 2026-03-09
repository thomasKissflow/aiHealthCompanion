"""
Test Bedrock API response format
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

print("Testing Bedrock API response format...")
print(f"Base URL: {os.getenv('OPENAI_BASE_URL')}")
print(f"Model: openai.gpt-oss-120b")

try:
    response = client.chat.completions.create(
        model="openai.gpt-oss-120b",
        messages=[
            {"role": "user", "content": "Say hello in one sentence"}
        ],
        temperature=0.7
    )
    
    print("\n=== RAW RESPONSE ===")
    print(f"Type: {type(response)}")
    print(f"Response object: {response}")
    print(f"\nDir: {[attr for attr in dir(response) if not attr.startswith('_')]}")
    
    print("\n=== RESPONSE ATTRIBUTES ===")
    if hasattr(response, 'choices'):
        print(f"choices: {response.choices}")
        print(f"choices type: {type(response.choices)}")
        if response.choices:
            print(f"choices[0]: {response.choices[0]}")
            if hasattr(response.choices[0], 'message'):
                print(f"message: {response.choices[0].message}")
                print(f"content: {response.choices[0].message.content}")
    
    if hasattr(response, 'model_dump'):
        print("\n=== MODEL DUMP ===")
        print(json.dumps(response.model_dump(), indent=2))
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
