"""
Session Management Module

This module provides session management for maintaining conversation context
across multiple turns. It stores the last 10 conversation turns and provides
context formatting for LLM prompts.

Requirements:
- 16.1: Store conversation history (last 10 turns)
- 16.4: Maintain last 10 turns
- 16.5: Implement session cleanup
- 16.6: Format context for LLM prompts
"""

import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Deque, Optional

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """
    Represents a single message in the conversation.
    
    Attributes:
        role: Either "user" or "assistant"
        content: The message text
        timestamp: When the message was created
    """
    role: str
    content: str
    timestamp: datetime


class Session:
    """
    Manages conversation context for a single user session.
    
    Maintains the last 10 conversation turns and provides context
    formatting for LLM prompts to enable pronoun resolution and
    conversation continuity.
    """
    
    def __init__(self, session_id: str, user_id: str):
        """
        Initialize a new session.
        
        Args:
            session_id: Unique identifier for this session
            user_id: Unique identifier for the user
        """
        self.session_id = session_id
        self.user_id = user_id
        self.conversation_history: Deque[Message] = deque(maxlen=10)
        self.created_at = datetime.now()
        
        logger.info(f"[Session] Created session {session_id} for user {user_id}")
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Automatically maintains the last 10 turns by using a deque
        with maxlen=10. When the 11th message is added, the oldest
        message is automatically removed.
        
        Args:
            role: Either "user" or "assistant"
            content: The message text
        """
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        self.conversation_history.append(message)
        
        logger.debug(
            f"[Session] Added {role} message to session {self.session_id} "
            f"(history size: {len(self.conversation_history)})"
        )
    
    def get_context_for_prompt(self) -> str:
        """
        Format conversation history for LLM prompt injection.
        
        Returns the conversation history as a formatted string that
        can be injected into LLM prompts to provide context for
        pronoun resolution and conversation continuity.
        
        Returns:
            Formatted conversation history string
        """
        if not self.conversation_history:
            return ""
        
        context_lines = ["Previous conversation:"]
        
        for msg in self.conversation_history:
            role_label = "User" if msg.role == "user" else "Assistant"
            context_lines.append(f"{role_label}: {msg.content}")
        
        context = "\n".join(context_lines)
        
        logger.debug(
            f"[Session] Generated context for session {self.session_id} "
            f"({len(self.conversation_history)} messages)"
        )
        
        return context
    
    def clear(self) -> None:
        """
        Clear all conversation history from the session.
        
        This should be called when the session ends to free up memory
        and ensure privacy.
        """
        self.conversation_history.clear()
        
        logger.info(f"[Session] Cleared session {self.session_id}")
    
    def get_message_count(self) -> int:
        """
        Get the number of messages in the conversation history.
        
        Returns:
            Number of messages currently stored
        """
        return len(self.conversation_history)
    
    def get_last_message(self) -> Optional[Message]:
        """
        Get the most recent message in the conversation.
        
        Returns:
            The last message, or None if history is empty
        """
        if self.conversation_history:
            return self.conversation_history[-1]
        return None
    
    def __repr__(self) -> str:
        """String representation of the session."""
        return (
            f"Session(id={self.session_id}, user={self.user_id}, "
            f"messages={len(self.conversation_history)}, "
            f"created={self.created_at.isoformat()})"
        )
