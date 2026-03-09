"""
Test Intent Classifier
"""
from intent_classifier import IntentClassifier, Intent
import logging

logging.basicConfig(level=logging.INFO)

def test_intent_classifier():
    """Test intent classification with various inputs"""
    classifier = IntentClassifier()
    
    test_cases = [
        # Greetings
        ("Hello", Intent.GREETING),
        ("Hi there", Intent.GREETING),
        ("Good morning", Intent.GREETING),
        
        # Risk symptoms
        ("I have chest pain", Intent.RISK_SYMPTOM),
        ("Can't breathe", Intent.RISK_SYMPTOM),
        ("Trouble breathing", Intent.RISK_SYMPTOM),
        
        # Mental health
        ("I'm feeling anxious", Intent.MENTAL_HEALTH),
        ("I'm depressed", Intent.MENTAL_HEALTH),
        ("Too much stress", Intent.MENTAL_HEALTH),
        
        # Symptom check
        ("I have a headache", Intent.SYMPTOM_CHECK),
        ("Feeling dizzy", Intent.SYMPTOM_CHECK),
        ("I have a fever", Intent.SYMPTOM_CHECK),
        
        # Knowledge query
        ("What causes headaches?", Intent.KNOWLEDGE_QUERY),
        ("Why do I get migraines?", Intent.KNOWLEDGE_QUERY),
        ("Tell me about migraines", Intent.KNOWLEDGE_QUERY),
        
        # Acknowledgment
        ("Okay", Intent.ACKNOWLEDGMENT),
        ("Thanks", Intent.ACKNOWLEDGMENT),
        ("Got it", Intent.ACKNOWLEDGMENT),
    ]
    
    print("=" * 60)
    print("INTENT CLASSIFIER TEST")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    for text, expected_intent in test_cases:
        intent, confidence = classifier.classify(text)
        status = "✓" if intent == expected_intent else "✗"
        
        if intent == expected_intent:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} '{text}'")
        print(f"  Expected: {expected_intent.value}")
        print(f"  Got: {intent.value} (confidence: {confidence:.2f})")
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = test_intent_classifier()
    exit(0 if success else 1)
