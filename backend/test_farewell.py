"""
Test farewell responses
"""
from intent_classifier import IntentClassifier, Intent
from template_engine import TemplateResponseEngine

# Test intent classification
classifier = IntentClassifier()
template_engine = TemplateResponseEngine()

test_phrases = [
    "bye",
    "goodbye",
    "thank you",
    "thanks for your help",
    "thanks for helping me",
    "that's all",
    "take care",
    "gotta go",
]

print("Testing Farewell Intent Classification:")
print("=" * 60)

for phrase in test_phrases:
    intent, confidence = classifier.classify(phrase)
    print(f"\nPhrase: '{phrase}'")
    print(f"Intent: {intent.value}")
    print(f"Confidence: {confidence:.2f}")
    
    if intent == Intent.FAREWELL:
        response = template_engine.get_farewell()
        print(f"Response: {response}")

print("\n" + "=" * 60)
print("✓ All farewell tests complete!")
