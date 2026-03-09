"""
Test Risk Escalation Agent
Tests rule-based risk detection and urgency classification
"""
import pytest
from risk_escalation_agent import RiskEscalationAgent
from template_engine import TemplateResponseEngine, UrgencyLevel


@pytest.fixture
def template_engine():
    """Create template engine instance"""
    return TemplateResponseEngine()


@pytest.fixture
def risk_agent(template_engine):
    """Create risk escalation agent instance"""
    return RiskEscalationAgent(template_engine)


class TestEmergencyDetection:
    """Test emergency symptom detection"""
    
    def test_chest_pain_emergency(self, risk_agent):
        """Test chest pain triggers EMERGENCY"""
        text = "I'm having severe chest pain"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.EMERGENCY
        assert "serious medical issue" in response.lower()
        assert "emergency services" in response.lower()
        assert len(response) > 0
    
    def test_breathing_difficulty_emergency(self, risk_agent):
        """Test breathing difficulty triggers EMERGENCY"""
        text = "I can't breathe properly"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.EMERGENCY
        assert len(response) > 0
    
    def test_severe_bleeding_emergency(self, risk_agent):
        """Test severe bleeding triggers EMERGENCY"""
        text = "I'm bleeding heavily and can't stop it"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.EMERGENCY
        assert len(response) > 0
    
    def test_stroke_symptoms_emergency(self, risk_agent):
        """Test stroke symptoms trigger EMERGENCY"""
        text = "I think I'm having a stroke"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.EMERGENCY
        assert len(response) > 0
    
    def test_is_emergency_helper(self, risk_agent):
        """Test is_emergency helper method"""
        assert risk_agent.is_emergency("chest pain and shortness of breath") is True
        assert risk_agent.is_emergency("mild headache") is False


class TestProfessionalCareDetection:
    """Test professional care classification"""
    
    def test_persistent_symptoms(self, risk_agent):
        """Test persistent symptoms trigger PROFESSIONAL"""
        text = "I've had a persistent headache for 3 days"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.PROFESSIONAL
        assert "doctor" in response.lower() or "healthcare" in response.lower()
        assert len(response) > 0
    
    def test_worsening_symptoms(self, risk_agent):
        """Test worsening symptoms trigger PROFESSIONAL"""
        text = "My symptoms are getting worse"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.PROFESSIONAL
        assert len(response) > 0
    
    def test_severe_symptoms(self, risk_agent):
        """Test severe symptoms trigger PROFESSIONAL"""
        text = "I have severe back pain"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.PROFESSIONAL
        assert len(response) > 0
    
    def test_high_fever(self, risk_agent):
        """Test high fever triggers PROFESSIONAL"""
        text = "I have a high fever over 103"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.PROFESSIONAL
        assert len(response) > 0


class TestMonitorClassification:
    """Test monitor classification"""
    
    def test_mild_symptoms(self, risk_agent):
        """Test mild symptoms trigger MONITOR"""
        text = "I have a mild headache"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.MONITOR
        assert "monitor" in response.lower() or "keep an eye" in response.lower()
        assert len(response) > 0
    
    def test_occasional_symptoms(self, risk_agent):
        """Test occasional symptoms trigger MONITOR"""
        text = "I occasionally feel dizzy"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.MONITOR
        assert len(response) > 0
    
    def test_improving_symptoms(self, risk_agent):
        """Test improving symptoms trigger MONITOR"""
        text = "My cough is improving"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.MONITOR
        assert len(response) > 0


class TestNoRiskDetection:
    """Test cases with no risk detected"""
    
    def test_general_question(self, risk_agent):
        """Test general question returns NONE"""
        text = "What causes migraines?"
        urgency, response = risk_agent.classify_urgency(text)
        
        assert urgency == UrgencyLevel.NONE
        assert response == ""
    
    def test_empty_text(self, risk_agent):
        """Test empty text returns NONE"""
        urgency, response = risk_agent.classify_urgency("")
        
        assert urgency == UrgencyLevel.NONE
        assert response == ""
    
    def test_whitespace_only(self, risk_agent):
        """Test whitespace only returns NONE"""
        urgency, response = risk_agent.classify_urgency("   ")
        
        assert urgency == UrgencyLevel.NONE
        assert response == ""


class TestTemplateResponseUsage:
    """Test that template responses are used without LLM"""
    
    def test_emergency_uses_template(self, risk_agent):
        """Test emergency uses template response"""
        text = "chest pain and difficulty breathing"
        urgency, response = risk_agent.classify_urgency(text)
        
        # Verify it's using the template from template_engine
        assert urgency == UrgencyLevel.EMERGENCY
        assert "serious medical issue" in response.lower()
        assert "emergency services" in response.lower()
    
    def test_get_response_helper(self, risk_agent):
        """Test get_response helper method"""
        response = risk_agent.get_response("chest pain")
        assert len(response) > 0
        assert "emergency" in response.lower()
        
        response = risk_agent.get_response("what is a headache?")
        assert response == ""


class TestPriorityOrdering:
    """Test that emergency patterns have priority over others"""
    
    def test_emergency_overrides_monitor(self, risk_agent):
        """Test emergency symptoms override monitor patterns"""
        # Text contains both "mild" (monitor) and "chest pain" (emergency)
        text = "I have mild chest pain"
        urgency, response = risk_agent.classify_urgency(text)
        
        # Emergency should take priority
        assert urgency == UrgencyLevel.EMERGENCY
    
    def test_emergency_overrides_professional(self, risk_agent):
        """Test emergency symptoms override professional patterns"""
        # Text contains both "persistent" (professional) and "can't breathe" (emergency)
        text = "I have persistent trouble breathing and can't breathe"
        urgency, response = risk_agent.classify_urgency(text)
        
        # Emergency should take priority
        assert urgency == UrgencyLevel.EMERGENCY


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
