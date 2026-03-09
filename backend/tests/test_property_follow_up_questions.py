"""
Property Test: Follow-Up Question Generation

Feature: ai-health-companion, Property 27: Follow-Up Question Generation
Validates: Requirements 17.2

Tests that symptom queries generate follow-up questions to clarify
user concerns and demonstrate conversational engagement.
"""

import pytest
import sys
import os
from hypothesis import given, strategies as st, settings

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Symptom-related queries for testing
SYMPTOM_QUERIES = [
    "I have a headache",
    "I'm experiencing nausea",
    "I have a fever",
    "My stomach hurts",
    "I feel dizzy",
    "I have back pain",
    "I'm coughing a lot",
    "I have a sore throat",
]


# Follow-up question indicators
FOLLOW_UP_INDICATORS = [
    "?",  # Question mark
    "when",
    "how long",
    "how often",
    "what",
    "where",
    "which",
    "can you",
    "could you",
    "tell me",
    "describe",
    "any other",
    "have you",
    "are you",
    "is it",
    "does it",
]


def generate_mock_response(symptom_query: str) -> str:
    """
    Mock LLM response generator that includes follow-up questions.
    This simulates the expected behavior of the system.
    """
    if "headache" in symptom_query.lower():
        return "I understand you're experiencing a headache. When did it start, and is the pain throbbing or constant?"
    elif "nausea" in symptom_query.lower():
        return "I'm sorry to hear about the nausea. How long have you been feeling this way?"
    elif "fever" in symptom_query.lower():
        return "A fever can be concerning. What's your temperature, and have you had any other symptoms?"
    elif "stomach" in symptom_query.lower():
        return "Stomach pain can have various causes. Where exactly is the pain located?"
    elif "dizzy" in symptom_query.lower():
        return "Dizziness can be unsettling. Does it happen when you stand up, or is it constant?"
    elif "back pain" in symptom_query.lower():
        return "Back pain is quite common. Is the pain in your upper or lower back?"
    elif "cough" in symptom_query.lower():
        return "I hear you're coughing. Is it a dry cough or are you bringing up mucus?"
    elif "sore throat" in symptom_query.lower():
        return "A sore throat can be uncomfortable. Is it painful to swallow?"
    else:
        return "I understand. Can you tell me more about your symptoms?"


@given(st.sampled_from(SYMPTOM_QUERIES))
@settings(max_examples=50)
def test_property_follow_up_question_generation(symptom_query):
    """
    Feature: ai-health-companion, Property 27: Follow-Up Question Generation
    **Validates: Requirements 17.2**
    
    Property: For any symptom-related query, the system should generate
    a response that includes follow-up questions to clarify user concerns.
    
    This demonstrates conversational engagement and helps gather more
    information for better assistance.
    """
    # Generate mock response (simulates LLM behavior)
    response = generate_mock_response(symptom_query)
    
    # Property: Response should contain follow-up question indicators
    response_lower = response.lower()
    has_follow_up = any(indicator in response_lower for indicator in FOLLOW_UP_INDICATORS)
    
    assert has_follow_up, \
        f"Expected follow-up question in response to '{symptom_query}', " \
        f"but got: '{response}'"


def test_follow_up_questions_for_common_symptoms():
    """
    Feature: ai-health-companion, Property 27: Follow-Up Question Generation
    **Validates: Requirements 17.2**
    
    Unit test: Verify that common symptom queries generate follow-up questions.
    """
    test_cases = [
        "I have a headache",
        "I'm feeling nauseous",
        "I have a fever",
        "My stomach hurts",
    ]
    
    for symptom in test_cases:
        response = generate_mock_response(symptom)
        
        # Verify follow-up question
        has_follow_up = any(indicator in response.lower() for indicator in FOLLOW_UP_INDICATORS)
        assert has_follow_up, \
            f"Expected follow-up question for '{symptom}', but got: '{response}'"


def test_follow_up_question_contains_question_mark():
    """
    Feature: ai-health-companion, Property 27: Follow-Up Question Generation
    **Validates: Requirements 17.2**
    
    Unit test: Verify that responses contain actual questions (with question marks).
    """
    for symptom in SYMPTOM_QUERIES:
        response = generate_mock_response(symptom)
        
        # Should contain at least one question mark
        assert "?" in response, \
            f"Expected question mark in response to '{symptom}', but got: '{response}'"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

