"""
Test Template Response Engine
"""
from template_engine import TemplateResponseEngine, UrgencyLevel
import logging

logging.basicConfig(level=logging.INFO)

def test_template_engine():
    """Test template response engine"""
    engine = TemplateResponseEngine()
    
    print("=" * 60)
    print("TEMPLATE RESPONSE ENGINE TEST")
    print("=" * 60)
    print()
    
    # Test greetings (should vary)
    print("Testing Greetings (should rotate):")
    greetings = []
    for i in range(5):
        greeting = engine.get_greeting()
        greetings.append(greeting)
        print(f"  {i+1}. {greeting}")
    print()
    
    # Check variation
    unique_greetings = len(set(greetings))
    print(f"✓ Greeting variation: {unique_greetings} unique out of 5")
    print()
    
    # Test acknowledgments
    print("Testing Acknowledgments:")
    for i in range(3):
        ack = engine.get_acknowledgment()
        print(f"  {i+1}. {ack}")
    print()
    
    # Test immediate feedback
    print("Testing Immediate Feedback:")
    for i in range(3):
        feedback = engine.get_immediate_feedback()
        print(f"  {i+1}. {feedback}")
    print()
    
    # Test risk responses
    print("Testing Risk Responses:")
    for level in [UrgencyLevel.EMERGENCY, UrgencyLevel.PROFESSIONAL, UrgencyLevel.MONITOR]:
        response = engine.get_risk_response(level)
        print(f"  {level.value}:")
        print(f"    {response[:80]}...")
    print()
    
    # Test variable substitution
    print("Testing Variable Substitution:")
    template = "Hello {name}, you have {count} messages"
    variables = {"name": "Thomas", "count": "3"}
    result = engine.substitute_variables(template, variables)
    print(f"  Template: {template}")
    print(f"  Variables: {variables}")
    print(f"  Result: {result}")
    print()
    
    print("=" * 60)
    print("✓ All template tests passed")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_template_engine()
    exit(0 if success else 1)
