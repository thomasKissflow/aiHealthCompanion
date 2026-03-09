"""
Test full system integration
"""
import asyncio
import requests
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_query(query_text, expected_intent=None):
    """Test query endpoint"""
    print(f"\n=== Testing Query: '{query_text}' ===")
    start = time.time()
    
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"query": query_text, "user_id": "test_user"}
    )
    
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success ({elapsed:.2f}s)")
        print(f"  Intent: {data['intent']}")
        print(f"  Response: {data['response'][:100]}...")
        print(f"  Fast Path: {data['used_fast_path']}")
        print(f"  Cache Hit: {data['cache_hit']}")
        print(f"  Used LLM: {data['used_llm']}")
        
        if expected_intent and data['intent'] != expected_intent:
            print(f"  ⚠️  Expected intent '{expected_intent}', got '{data['intent']}'")
        
        return True
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  {response.text}")
        return False

def main():
    print("AI Health Companion - Full System Test")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Backend not running! Start with: python main.py")
        return
    
    # Test 2: Greeting (fast path)
    test_query("Hello", "greeting")
    
    # Test 3: Symptom check (LLM)
    test_query("I have a headache and feel nauseous", "symptom_check")
    
    # Test 4: Mental health (LLM)
    test_query("I'm feeling really stressed with work", "mental_health")
    
    # Test 5: Risk symptom (fast path)
    test_query("I have severe chest pain", "risk_symptom")
    
    # Test 6: Cached response (should be fast)
    test_query("I have a headache and feel nauseous", "symptom_check")
    
    print("\n" + "=" * 50)
    print("✓ All tests complete!")
    print("\nCheck the backend terminal for detailed logs.")

if __name__ == "__main__":
    main()
