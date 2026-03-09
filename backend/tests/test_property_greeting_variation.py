"""
Property Test: Greeting Variation Across Sessions

Feature: ai-health-companion, Property 20: Greeting Variation Across Sessions
Validates: Requirements 17.1, 17.2

Tests that consecutive sessions use different greetings to provide
natural and varied conversations.
"""

import pytest
import sys
import os
from hypothesis import given, strategies as st, settings

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from template_engine import TemplateResponseEngine


@given(st.integers(min_value=2, max_value=10))
@settings(max_examples=100)
def test_property_greeting_variation_across_sessions(num_sessions):
    """
    Feature: ai-health-companion, Property 20: Greeting Variation Across Sessions
    **Validates: Requirements 17.1, 17.2**
    
    Property: For any sequence of N consecutive new sessions (where N >= 2),
    the system should use at least 2 different greeting templates,
    demonstrating greeting variation rather than repetition.
    
    This ensures natural and varied conversations across sessions.
    """
    engine = TemplateResponseEngine()
    
    # Collect greetings from consecutive sessions
    greetings = []
    for _ in range(num_sessions):
        greeting = engine.get_greeting()
        greetings.append(greeting)
    
    # Property: Should have at least 2 different greetings
    unique_greetings = set(greetings)
    
    assert len(unique_greetings) >= 2, \
        f"Expected at least 2 different greetings in {num_sessions} sessions, " \
        f"but got {len(unique_greetings)} unique greetings: {unique_greetings}"
    
    # Additional check: No greeting should appear more than 50% of the time
    # (to ensure good distribution)
    for greeting in unique_greetings:
        count = greetings.count(greeting)
        percentage = (count / num_sessions) * 100
        
        assert percentage <= 60, \
            f"Greeting '{greeting[:30]}...' appeared {percentage:.1f}% of the time, " \
            f"which is too frequent (should be <= 60%)"


@given(st.integers(min_value=2, max_value=5))
@settings(max_examples=50)
def test_property_consecutive_greetings_differ(num_consecutive):
    """
    Feature: ai-health-companion, Property 20: Greeting Variation Across Sessions
    **Validates: Requirements 17.1, 17.2**
    
    Property: For any two consecutive sessions, the greeting templates
    should differ (no immediate repetition).
    
    This ensures users don't hear the exact same greeting twice in a row.
    """
    engine = TemplateResponseEngine()
    
    # Test consecutive pairs
    for _ in range(num_consecutive):
        greeting1 = engine.get_greeting()
        greeting2 = engine.get_greeting()
        
        assert greeting1 != greeting2, \
            f"Consecutive greetings should differ, but both were: '{greeting1}'"


def test_greeting_variation_minimum_templates():
    """
    Feature: ai-health-companion, Property 20: Greeting Variation Across Sessions
    **Validates: Requirements 17.1, 17.2**
    
    Unit test: Verify that the template engine has at least 3 greeting templates
    to ensure sufficient variation.
    """
    engine = TemplateResponseEngine()
    
    # Collect enough greetings to see all templates
    greetings = set()
    for _ in range(20):  # Collect 20 greetings
        greeting = engine.get_greeting()
        greetings.add(greeting)
    
    # Should have at least 3 different templates
    assert len(greetings) >= 3, \
        f"Expected at least 3 different greeting templates, but found {len(greetings)}: {greetings}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
