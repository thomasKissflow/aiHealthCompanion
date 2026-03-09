"""
User History Agent for managing conversation context and history.

This agent stores and retrieves user conversation summaries, symptoms,
known conditions, and mental health notes to provide personalized context.
"""

from typing import Optional, List
from database import Database, UserContext


class UserHistoryAgent:
    """
    Agent for managing user conversation history and context.
    
    Responsibilities:
    - Store conversation summaries in SQLite database
    - Maintain known conditions and mental health notes
    - Retrieve previous context for current session
    - Inject context into LLM prompts
    - Log context retrieval
    """
    
    def __init__(self, database: Database):
        """
        Initialize User History Agent.
        
        Args:
            database: Database instance for storage operations
        """
        self.database = database
    
    async def store_conversation(
        self,
        user_id: str,
        summary: str = "",
        symptoms: Optional[List[str]] = None,
        conditions: Optional[List[str]] = None,
        mental_health_notes: str = ""
    ) -> None:
        """
        Store conversation summary and context for a user.
        
        Args:
            user_id: User identifier
            summary: Conversation summary
            symptoms: List of symptoms mentioned (e.g., ["headache", "nausea"])
            conditions: List of known conditions (e.g., ["migraines"])
            mental_health_notes: Mental health context (e.g., "work-related stress")
        """
        await self.database.store_user_context(
            user_id=user_id,
            conversation_summary=summary,
            previous_symptoms=symptoms or [],
            known_conditions=conditions or [],
            mental_health_notes=mental_health_notes
        )
        
        print(f"[History Agent] stored context for user {user_id}")
    
    async def get_context(self, user_id: str) -> Optional[UserContext]:
        """
        Retrieve previous conversation context for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            UserContext if found, None otherwise
        """
        context = await self.database.get_user_context(user_id)
        
        if context:
            print(f"[History Agent] retrieved previous context")
            self.log_context_retrieval(context)
        
        return context
    
    def format_context_for_prompt(self, context: Optional[UserContext]) -> str:
        """
        Format user context for injection into LLM prompts.
        
        Args:
            context: User context data
            
        Returns:
            Formatted context string for LLM prompt
        """
        if not context:
            return ""
        
        parts = []
        
        if context.conversation_summary:
            parts.append(f"Previous conversation summary: {context.conversation_summary}")
        
        if context.previous_symptoms:
            symptoms_str = ", ".join(context.previous_symptoms)
            parts.append(f"Previous symptoms mentioned: {symptoms_str}")
        
        if context.known_conditions:
            conditions_str = ", ".join(context.known_conditions)
            parts.append(f"Known conditions: {conditions_str}")
        
        if context.mental_health_notes:
            parts.append(f"Mental health notes: {context.mental_health_notes}")
        
        if parts:
            return "\n".join(["User History Context:", *parts])
        
        return ""
    
    def log_context_retrieval(self, context: UserContext) -> None:
        """
        Log context retrieval details to terminal.
        
        Args:
            context: Retrieved user context
        """
        details = []
        
        if context.conversation_summary:
            details.append(f"summary: {context.conversation_summary[:50]}...")
        
        if context.previous_symptoms:
            details.append(f"symptoms: {', '.join(context.previous_symptoms)}")
        
        if context.known_conditions:
            details.append(f"conditions: {', '.join(context.known_conditions)}")
        
        if context.mental_health_notes:
            details.append(f"mental_health: {context.mental_health_notes[:50]}...")
        
        if details:
            print(f"[History Agent] context details: {'; '.join(details)}")
