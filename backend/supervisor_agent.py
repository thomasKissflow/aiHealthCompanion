"""
Supervisor Agent for AI Health Companion

This agent orchestrates the conversation flow by routing user inputs to
appropriate specialized agents based on intent classification. It coordinates
parallel agent execution and aggregates responses.

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from intent_classifier import IntentClassifier, Intent
from risk_escalation_agent import RiskEscalationAgent
from mental_health_agent import MentalHealthAgent
from knowledge_agent import KnowledgeSpecialistAgent
from user_history_agent import UserHistoryAgent
from template_engine import TemplateResponseEngine
from llm_client import LLMClient
from session import Session

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Response from a specialized agent"""
    agent_name: str
    content: str
    metadata: Dict[str, Any]
    processing_time_ms: float


class SupervisorAgent:
    """
    Orchestrates conversation flow and routes to specialized agents.
    
    Responsibilities:
    - Classify user intent using Intent Classifier
    - Route to appropriate specialized agents
    - Execute agents in parallel when independent
    - Aggregate agent responses into coherent reply
    - Log routing decisions
    """
    
    def __init__(
        self,
        intent_classifier: IntentClassifier,
        risk_agent: RiskEscalationAgent,
        mental_health_agent: MentalHealthAgent,
        knowledge_agent: KnowledgeSpecialistAgent,
        history_agent: UserHistoryAgent,
        template_engine: TemplateResponseEngine,
        llm_client: LLMClient
    ):
        """
        Initialize Supervisor Agent.
        
        Args:
            intent_classifier: Intent classification service
            risk_agent: Risk escalation agent
            mental_health_agent: Mental health support agent
            knowledge_agent: Knowledge specialist agent
            history_agent: User history agent
            template_engine: Template response engine
            llm_client: LLM client for complex reasoning
        """
        self.intent_classifier = intent_classifier
        self.risk_agent = risk_agent
        self.mental_health_agent = mental_health_agent
        self.knowledge_agent = knowledge_agent
        self.history_agent = history_agent
        self.template_engine = template_engine
        self.llm_client = llm_client
        
        logger.info("[Supervisor] Initialized")

    async def process_query(self, text: str, session: Session) -> str:
        """
        Process user query and return response.
        
        Main entry point for query processing. Classifies intent,
        routes to appropriate agents, and returns aggregated response.
        
        Requirements: 6.1, 6.2, 6.3, 6.5
        
        Args:
            text: User input text
            session: Current session context
            
        Returns:
            Final response text
        """
        if not text or not text.strip():
            return "I didn't catch that. Could you please say that again?"
        
        # Classify intent
        intent, confidence = self.intent_classifier.classify(text)
        
        # Log routing decision
        self.log_routing(intent, text)
        
        # Route based on intent
        response = await self._route_by_intent(intent, text, session)
        
        # Add message to session history
        session.add_message("user", text)
        session.add_message("assistant", response)
        
        return response

    async def _route_by_intent(
        self,
        intent: Intent,
        text: str,
        session: Session
    ) -> str:
        """
        Route query to appropriate agents based on intent.
        
        Requirements: 6.2, 6.4
        
        Args:
            intent: Classified intent
            text: User input text
            session: Current session context
            
        Returns:
            Response text
        """
        # Fast path: GREETING
        if intent == Intent.GREETING:
            logger.info("[LLM Agent] skipping model call")
            return self.template_engine.get_greeting()
        
        # Fast path: FAREWELL
        if intent == Intent.FAREWELL:
            logger.info("[LLM Agent] skipping model call")
            return self.template_engine.get_farewell()
        
        # Fast path: ACKNOWLEDGMENT
        if intent == Intent.ACKNOWLEDGMENT:
            logger.info("[LLM Agent] skipping model call")
            return self.template_engine.get_acknowledgment()
        
        # Fast path: RISK_SYMPTOM
        if intent == Intent.RISK_SYMPTOM:
            urgency, response = self.risk_agent.classify_urgency(text)
            if response:
                logger.info("[LLM Agent] skipping model call")
                return response
        
        # Check if mental health agent should activate
        if intent == Intent.MENTAL_HEALTH or self.mental_health_agent.detect_distress(text):
            self.mental_health_agent.activate(text)
        
        # Route to appropriate agents based on intent
        agents_to_run = []
        
        if intent == Intent.SYMPTOM_CHECK:
            # Run Knowledge + History + LLM in parallel
            agents_to_run = [
                self._run_knowledge_agent(text),
                self._run_history_agent(session.user_id)
            ]
        
        elif intent == Intent.MENTAL_HEALTH:
            # Run Mental Health + History in parallel
            agents_to_run = [
                self._run_mental_health_agent(text, session),
                self._run_history_agent(session.user_id)
            ]
        
        elif intent == Intent.KNOWLEDGE_QUERY:
            # Run Knowledge + History in parallel
            agents_to_run = [
                self._run_knowledge_agent(text),
                self._run_history_agent(session.user_id)
            ]
        
        elif intent == Intent.RISK_SYMPTOM:
            # Already handled above, but run with history for context
            agents_to_run = [
                self._run_history_agent(session.user_id)
            ]
        
        else:  # UNKNOWN or other
            # Run with history for context
            agents_to_run = [
                self._run_history_agent(session.user_id)
            ]
        
        # Execute agents in parallel
        if agents_to_run:
            agent_responses = await asyncio.gather(*agents_to_run, return_exceptions=True)
            
            # Filter out exceptions and None responses
            valid_responses = [
                r for r in agent_responses
                if r is not None and not isinstance(r, Exception)
            ]
            
            # Aggregate responses
            return await self._aggregate_responses(
                text,
                valid_responses,
                session,
                intent
            )
        
        # Fallback: use LLM with session context
        return await self._generate_llm_response(text, session, None, None)

    async def _run_knowledge_agent(self, text: str) -> Optional[AgentResponse]:
        """
        Run knowledge specialist agent.
        
        Args:
            text: User query
            
        Returns:
            AgentResponse or None
        """
        try:
            import time
            start = time.time()
            
            # Retrieve relevant chunks
            chunks = await self.knowledge_agent.retrieve(text)
            
            processing_time = (time.time() - start) * 1000
            
            return AgentResponse(
                agent_name="knowledge",
                content="",  # Chunks will be used in LLM prompt
                metadata={"chunks": chunks},
                processing_time_ms=processing_time
            )
        except Exception as e:
            logger.error(f"[Supervisor] Knowledge agent error: {e}")
            return None
    
    async def _run_history_agent(self, user_id: str) -> Optional[AgentResponse]:
        """
        Run user history agent.
        
        Args:
            user_id: User identifier
            
        Returns:
            AgentResponse or None
        """
        try:
            import time
            start = time.time()
            
            # Get user context
            context = await self.history_agent.get_context(user_id)
            
            processing_time = (time.time() - start) * 1000
            
            return AgentResponse(
                agent_name="history",
                content="",  # Context will be used in LLM prompt
                metadata={"context": context},
                processing_time_ms=processing_time
            )
        except Exception as e:
            logger.error(f"[Supervisor] History agent error: {e}")
            return None
    
    async def _run_mental_health_agent(
        self,
        text: str,
        session: Session
    ) -> Optional[AgentResponse]:
        """
        Run mental health support agent.
        
        Args:
            text: User input
            session: Current session
            
        Returns:
            AgentResponse or None
        """
        try:
            import time
            start = time.time()
            
            # Check if breathing exercise should be offered
            if self.mental_health_agent.should_offer_breathing_exercise(text):
                response = self.mental_health_agent.get_breathing_exercise()
                processing_time = (time.time() - start) * 1000
                
                return AgentResponse(
                    agent_name="mental_health",
                    content=response,
                    metadata={"type": "breathing_exercise"},
                    processing_time_ms=processing_time
                )
            
            # Otherwise, will generate supportive response via LLM
            processing_time = (time.time() - start) * 1000
            
            return AgentResponse(
                agent_name="mental_health",
                content="",  # Will be generated by LLM
                metadata={"type": "supportive"},
                processing_time_ms=processing_time
            )
        except Exception as e:
            logger.error(f"[Supervisor] Mental health agent error: {e}")
            return None

    async def _aggregate_responses(
        self,
        text: str,
        agent_responses: List[AgentResponse],
        session: Session,
        intent: Intent
    ) -> str:
        """
        Aggregate agent responses into coherent reply.
        
        Requirements: 6.5
        
        Args:
            text: Original user query
            agent_responses: List of agent responses
            session: Current session
            intent: Classified intent
            
        Returns:
            Aggregated response text
        """
        # Extract knowledge chunks and history context
        knowledge_chunks = []
        user_context = None
        direct_response = None
        
        for response in agent_responses:
            if response.agent_name == "knowledge":
                knowledge_chunks = response.metadata.get("chunks", [])
            elif response.agent_name == "history":
                user_context = response.metadata.get("context")
            elif response.agent_name == "mental_health":
                if response.content:  # Direct response (e.g., breathing exercise)
                    direct_response = response.content
        
        # If we have a direct response, return it
        if direct_response:
            return direct_response
        
        # Otherwise, generate response using LLM with context
        return await self._generate_llm_response(
            text,
            session,
            knowledge_chunks,
            user_context
        )

    async def _generate_llm_response(
        self,
        text: str,
        session: Session,
        knowledge_chunks: Optional[List[str]],
        user_context: Optional[Any]
    ) -> str:
        """
        Generate response using LLM with context.
        
        Requirements: 6.5, 6.7
        
        Args:
            text: User query
            session: Current session
            knowledge_chunks: Retrieved knowledge chunks
            user_context: User history context
            
        Returns:
            Generated response text
        """
        # Build prompt with context
        prompt_parts = []
        
        # Add session context
        session_context = session.get_context_for_prompt()
        if session_context:
            prompt_parts.append(session_context)
            prompt_parts.append("")
        
        # Add user history context
        if user_context:
            history_context = self.history_agent.format_context_for_prompt(user_context)
            if history_context:
                prompt_parts.append(history_context)
                prompt_parts.append("")
        
        # Add knowledge context
        if knowledge_chunks:
            prompt_parts.append("Medical Reference Context:")
            for i, chunk in enumerate(knowledge_chunks, 1):
                prompt_parts.append(f"[{i}] {chunk}")
            prompt_parts.append("")
        
        # Add current query
        prompt_parts.append(f"User: {text}")
        prompt_parts.append("Assistant:")
        
        prompt = "\n".join(prompt_parts)
        
        # System prompt
        system_prompt = (
            "You are a compassionate AI health companion. "
            "Provide brief, helpful, conversational responses (2-3 sentences maximum). "
            "Do not diagnose conditions or recommend specific medications. "
            "Do not include multiple choice questions, code, or training examples. "
            "Be warm, empathetic, and supportive. "
            "Respond directly to the user's question."
        )
        
        # Check if mental health agent is active
        if self.mental_health_agent.is_agent_active():
            system_prompt = (
                "You are a compassionate AI health companion providing emotional support. "
                "Respond with empathy and warmth in 2-3 sentences. "
                "DO NOT diagnose mental health conditions. "
                "DO NOT recommend specific medications or treatments. "
                "DO NOT include multiple choice questions, code, or examples. "
                "Focus on active listening, validation, and gentle guidance."
            )
        
        # Generate response
        response = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        # Handle timeout or error
        if response is None:
            logger.warning("[Supervisor] LLM timeout - using fallback")
            return self.template_engine.get_fallback_response()
        
        # Clean response - remove training artifacts
        response = self._clean_response(response)
        
        return response
    
    def _clean_response(self, response: str) -> str:
        """
        Clean LLM response by removing training artifacts.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Cleaned response
        """
        # Stop at common training artifact markers
        stop_markers = [
            "\n\nWhat would be",
            "\n\nPlease select",
            "\n\nCorrect answer:",
            "\n\nExplanation:",
            "```python",
            "```",
            "\n\nLet's move on",
            "\n\nQuestion:",
            "\nA)",
            "\nB)",
            "\nC)",
            "\nD)"
        ]
        
        for marker in stop_markers:
            if marker in response:
                response = response.split(marker)[0]
        
        # Remove trailing incomplete sentences
        response = response.strip()
        
        # Ensure it ends with proper punctuation
        if response and response[-1] not in '.!?':
            # Find last sentence ending
            for i in range(len(response) - 1, -1, -1):
                if response[i] in '.!?':
                    response = response[:i+1]
                    break
        
        return response.strip()
    
    def log_routing(self, intent: Intent, text: str) -> None:
        """
        Log routing decisions to terminal.
        
        Requirements: 6.3, 6.7
        
        Args:
            intent: Classified intent
            text: User input text
        """
        logger.info(
            f"[Supervisor] Routing query to agents - "
            f"Intent: {intent.value}, "
            f"Query length: {len(text)} chars"
        )
