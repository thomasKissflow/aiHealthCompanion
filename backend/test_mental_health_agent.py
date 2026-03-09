"""
Test Mental Health Support Agent
Tests emotional distress detection and supportive response generation
"""
import pytest
from mental_health_agent import MentalHealthAgent
from response_cache import ResponseCache


@pytest.fixture
def response_cache():
    """Create response cache instance"""
    return ResponseCache(max_size=100, ttl_hours=24)


@pytest.fixture
def mental_health_agent(response_cache):
    """Create mental health agent instance"""
    return MentalHealthAgent(response_cache)


class TestDistressDetection:
    """Test emotional distress keyword detection"""
    
    def test_detect_hopeless(self, mental_health_agent):
        """Test hopeless keyword detection"""
        assert mental_health_agent.detect_distress("I feel hopeless") is True
    
    def test_detect_anxious(self, mental_health_agent):
        """Test anxious keyword detection"""
        assert mental_health_agent.detect_distress("I'm feeling anxious") is True
    
    def test_detect_depressed(self, mental_health_agent):
        """Test depressed keyword detection"""
        assert mental_health_agent.detect_distress("I've been depressed lately") is True
    
    def test_detect_overwhelmed(self, mental_health_agent):
        """Test overwhelmed keyword detection"""
        assert mental_health_agent.detect_distress("I'm overwhelmed with work") is True
    
    def test_detect_stressed(self, mental_health_agent):
        """Test stressed keyword detection"""
        assert mental_health_agent.detect_distress("I'm so stressed out") is True
    
    def test_detect_cant_keep_up(self, mental_health_agent):
        """Test can't keep up phrase detection"""
        assert mental_health_agent.detect_distress("I can't keep up with everything") is True
    
    def test_detect_burned_out(self, mental_health_agent):
        """Test burned out keyword detection"""
        assert mental_health_agent.detect_distress("I'm burned out") is True
    
    def test_detect_lonely(self, mental_health_agent):
        """Test lonely keyword detection"""
        assert mental_health_agent.detect_distress("I feel so lonely") is True
    
    def test_detect_scared(self, mental_health_agent):
        """Test scared keyword detection"""
        assert mental_health_agent.detect_distress("I'm scared about my health") is True
    
    def test_no_distress_general_question(self, mental_health_agent):
        """Test no distress in general question"""
        assert mental_health_agent.detect_distress("What causes headaches?") is False
    
    def test_no_distress_symptom_check(self, mental_health_agent):
        """Test no distress in symptom check"""
        assert mental_health_agent.detect_distress("I have a mild headache") is False
    
    def test_empty_text(self, mental_health_agent):
        """Test empty text returns False"""
        assert mental_health_agent.detect_distress("") is False
    
    def test_whitespace_only(self, mental_health_agent):
        """Test whitespace only returns False"""
        assert mental_health_agent.detect_distress("   ") is False


class TestAgentActivation:
    """Test agent activation and session tracking"""
    
    def test_activate_on_distress(self, mental_health_agent):
        """Test agent activates on distress detection"""
        assert mental_health_agent.is_agent_active() is False
        
        result = mental_health_agent.activate("I'm feeling anxious")
        
        assert result is True
        assert mental_health_agent.is_agent_active() is True
    
    def test_no_activate_without_distress(self, mental_health_agent):
        """Test agent doesn't activate without distress"""
        result = mental_health_agent.activate("What is a headache?")
        
        assert result is False
        assert mental_health_agent.is_agent_active() is False
    
    def test_remains_active_for_session(self, mental_health_agent):
        """Test agent remains active after initial activation"""
        mental_health_agent.activate("I'm stressed")
        assert mental_health_agent.is_agent_active() is True
        
        # Agent should remain active even for non-distress queries
        mental_health_agent.activate("What should I do?")
        assert mental_health_agent.is_agent_active() is True
    
    def test_deactivate(self, mental_health_agent):
        """Test agent deactivation"""
        mental_health_agent.activate("I'm anxious")
        assert mental_health_agent.is_agent_active() is True
        
        mental_health_agent.deactivate()
        assert mental_health_agent.is_agent_active() is False


class TestBreathingExercise:
    """Test guided breathing exercise"""
    
    def test_get_breathing_exercise(self, mental_health_agent):
        """Test breathing exercise template"""
        exercise = mental_health_agent.get_breathing_exercise()
        
        assert len(exercise) > 0
        assert "breathing" in exercise.lower()
        assert "4 counts" in exercise.lower()
    
    def test_should_offer_breathing_yes(self, mental_health_agent):
        """Test offering breathing exercise on yes"""
        assert mental_health_agent.should_offer_breathing_exercise("yes please") is True
    
    def test_should_offer_breathing_help(self, mental_health_agent):
        """Test offering breathing exercise on help request"""
        assert mental_health_agent.should_offer_breathing_exercise("what can I do?") is True
    
    def test_should_offer_breathing_okay(self, mental_health_agent):
        """Test offering breathing exercise on okay"""
        assert mental_health_agent.should_offer_breathing_exercise("okay") is True
    
    def test_should_not_offer_breathing_no(self, mental_health_agent):
        """Test not offering breathing exercise on no"""
        assert mental_health_agent.should_offer_breathing_exercise("no thanks") is False
    
    def test_should_not_offer_breathing_unrelated(self, mental_health_agent):
        """Test not offering breathing exercise on unrelated text"""
        assert mental_health_agent.should_offer_breathing_exercise("I have a headache") is False
    
    def test_breathing_exercise_offered_when_user_accepts_support(self, mental_health_agent):
        """
        Test that breathing exercise is offered when user accepts support
        Validates Requirement 8.7
        """
        # Activate agent with distress
        mental_health_agent.activate("I'm feeling anxious")
        assert mental_health_agent.is_agent_active() is True
        
        # User accepts support
        user_acceptance_phrases = [
            "yes please",
            "yes",
            "yeah",
            "sure",
            "okay",
            "ok",
            "please help",
            "what can I do?",
            "how can I feel better?",
            "I'd like that",
            "that would help"
        ]
        
        for phrase in user_acceptance_phrases:
            # Check if breathing exercise should be offered
            should_offer = mental_health_agent.should_offer_breathing_exercise(phrase)
            assert should_offer is True, f"Should offer breathing exercise for: '{phrase}'"
            
            # Get the breathing exercise
            exercise = mental_health_agent.get_breathing_exercise()
            
            # Verify exercise content
            assert exercise is not None, "Breathing exercise should not be None"
            assert len(exercise) > 0, "Breathing exercise should not be empty"
            assert "breathing" in exercise.lower(), "Exercise should mention breathing"
            assert "breath" in exercise.lower(), "Exercise should mention breath"
            assert "4 counts" in exercise.lower(), "Exercise should include 4 counts instruction"
            
        # Verify rejection cases don't offer exercise
        rejection_phrases = ["no", "no thanks", "not now", "maybe later"]
        for phrase in rejection_phrases:
            should_offer = mental_health_agent.should_offer_breathing_exercise(phrase)
            assert should_offer is False, f"Should NOT offer breathing exercise for: '{phrase}'"


class TestCacheIntegration:
    """Test integration with Response Cache"""
    
    def test_check_cache_miss(self, mental_health_agent):
        """Test cache miss returns None"""
        result = mental_health_agent.check_cache("I'm feeling anxious")
        assert result is None
    
    def test_cache_response(self, mental_health_agent):
        """Test caching supportive response"""
        text = "I'm feeling overwhelmed"
        response = "I hear you. It's okay to feel overwhelmed sometimes."
        
        mental_health_agent.cache_response(text, response)
        
        # Should retrieve from cache
        cached = mental_health_agent.check_cache(text)
        assert cached == response
    
    def test_cache_with_context(self, mental_health_agent):
        """Test caching with context"""
        text = "I'm stressed"
        response = "I understand. Let's work through this together."
        context = {"topic": "work_stress"}
        
        mental_health_agent.cache_response(text, response, context)
        
        # Should retrieve with same context
        cached = mental_health_agent.check_cache(text, context)
        assert cached == response
        
        # Should not retrieve with different context
        cached_different = mental_health_agent.check_cache(text, {"topic": "family_stress"})
        assert cached_different is None


class TestPromptGeneration:
    """Test LLM prompt generation"""
    
    def test_generate_supportive_prompt_basic(self, mental_health_agent):
        """Test basic prompt generation"""
        text = "I'm feeling anxious"
        prompt = mental_health_agent.generate_supportive_prompt(text)
        
        assert "compassionate" in prompt.lower()
        assert "empathy" in prompt.lower()
        assert "DO NOT diagnose" in prompt
        assert "DO NOT recommend specific medications" in prompt
        assert text in prompt
    
    def test_generate_supportive_prompt_with_history(self, mental_health_agent):
        """Test prompt generation with user history"""
        text = "I'm still stressed"
        history = "User mentioned work stress last week"
        prompt = mental_health_agent.generate_supportive_prompt(text, history)
        
        assert history in prompt
        assert text in prompt
    
    def test_prompt_prohibits_diagnosis(self, mental_health_agent):
        """Test prompt explicitly prohibits diagnosis"""
        prompt = mental_health_agent.generate_supportive_prompt("I'm depressed")
        
        assert "DO NOT diagnose mental health conditions" in prompt
    
    def test_prompt_prohibits_medication(self, mental_health_agent):
        """Test prompt explicitly prohibits medication recommendations"""
        prompt = mental_health_agent.generate_supportive_prompt("I'm anxious")
        
        assert "DO NOT recommend specific medications" in prompt


class TestLogging:
    """Test logging functionality"""
    
    def test_log_response_generated(self, mental_health_agent, caplog):
        """Test logging of supportive response generation"""
        import logging
        caplog.set_level(logging.INFO)
        
        mental_health_agent.log_response_generated()
        
        assert "[Mental Health Agent] supportive response generated" in caplog.text


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_multiple_distress_keywords(self, mental_health_agent):
        """Test text with multiple distress keywords"""
        text = "I'm anxious, overwhelmed, and can't keep up"
        assert mental_health_agent.detect_distress(text) is True
    
    def test_case_insensitive_detection(self, mental_health_agent):
        """Test case insensitive keyword detection"""
        assert mental_health_agent.detect_distress("I'm ANXIOUS") is True
        assert mental_health_agent.detect_distress("I'm Stressed") is True
    
    def test_distress_in_sentence(self, mental_health_agent):
        """Test distress keyword detection within sentence"""
        text = "My friend is anxious but I'm trying to help"
        assert mental_health_agent.detect_distress(text) is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
