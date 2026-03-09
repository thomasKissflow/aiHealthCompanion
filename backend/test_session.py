"""
Test script for Session Management

Tests:
- Session initialization
- Adding messages to conversation history
- Maintaining last 10 turns (LRU behavior)
- Context formatting for LLM prompts
- Session cleanup
- Pronoun resolution support
"""

import pytest
from session import Session, Message


class TestSessionInitialization:
    """Test session initialization."""
    
    def test_create_session(self):
        """Test creating a new session."""
        print("\n=== Test: Create Session ===")
        
        session = Session(session_id="test_session_1", user_id="user123")
        
        assert session.session_id == "test_session_1"
        assert session.user_id == "user123"
        assert session.get_message_count() == 0
        assert session.created_at is not None
        
        print("✓ Session created successfully")
        print(f"  - Session ID: {session.session_id}")
        print(f"  - User ID: {session.user_id}")
        print(f"  - Message count: {session.get_message_count()}")


class TestMessageManagement:
    """Test message addition and retrieval."""
    
    def test_add_single_message(self):
        """Test adding a single message."""
        print("\n=== Test: Add Single Message ===")
        
        session = Session(session_id="test_session_2", user_id="user123")
        session.add_message(role="user", content="Hello, I have a headache")
        
        assert session.get_message_count() == 1
        last_msg = session.get_last_message()
        assert last_msg.role == "user"
        assert last_msg.content == "Hello, I have a headache"
        
        print("✓ Message added successfully")
    
    def test_add_multiple_messages(self):
        """Test adding multiple messages."""
        print("\n=== Test: Add Multiple Messages ===")
        
        session = Session(session_id="test_session_3", user_id="user123")
        
        session.add_message(role="user", content="I have a headache")
        session.add_message(role="assistant", content="I'm sorry to hear that. How long have you had it?")
        session.add_message(role="user", content="About 2 hours")
        
        assert session.get_message_count() == 3
        
        print("✓ Multiple messages added successfully")
        print(f"  - Total messages: {session.get_message_count()}")
    
    def test_get_last_message(self):
        """Test retrieving the last message."""
        print("\n=== Test: Get Last Message ===")
        
        session = Session(session_id="test_session_4", user_id="user123")
        
        session.add_message(role="user", content="First message")
        session.add_message(role="assistant", content="Second message")
        session.add_message(role="user", content="Third message")
        
        last_msg = session.get_last_message()
        assert last_msg.content == "Third message"
        assert last_msg.role == "user"
        
        print("✓ Last message retrieved correctly")
    
    def test_empty_session_last_message(self):
        """Test getting last message from empty session."""
        print("\n=== Test: Empty Session Last Message ===")
        
        session = Session(session_id="test_session_5", user_id="user123")
        
        last_msg = session.get_last_message()
        assert last_msg is None
        
        print("✓ Empty session returns None for last message")


class TestContextRetention:
    """Test conversation context retention (last 10 turns)."""
    
    def test_maintain_last_10_turns(self):
        """Test that only last 10 messages are kept."""
        print("\n=== Test: Maintain Last 10 Turns ===")
        
        session = Session(session_id="test_session_6", user_id="user123")
        
        # Add 15 messages
        for i in range(15):
            role = "user" if i % 2 == 0 else "assistant"
            session.add_message(role=role, content=f"Message {i+1}")
        
        # Should only have last 10 messages
        assert session.get_message_count() == 10
        
        # First message should be "Message 6" (messages 1-5 were evicted)
        first_msg = list(session.conversation_history)[0]
        assert first_msg.content == "Message 6"
        
        # Last message should be "Message 15"
        last_msg = session.get_last_message()
        assert last_msg.content == "Message 15"
        
        print("✓ Last 10 turns maintained correctly")
        print(f"  - Total messages: {session.get_message_count()}")
        print(f"  - First message: {first_msg.content}")
        print(f"  - Last message: {last_msg.content}")
    
    def test_11th_message_removes_oldest(self):
        """Test that 11th message removes the oldest."""
        print("\n=== Test: 11th Message Removes Oldest ===")
        
        session = Session(session_id="test_session_7", user_id="user123")
        
        # Add exactly 10 messages
        for i in range(10):
            session.add_message(role="user", content=f"Message {i+1}")
        
        assert session.get_message_count() == 10
        first_msg_before = list(session.conversation_history)[0]
        assert first_msg_before.content == "Message 1"
        
        # Add 11th message
        session.add_message(role="user", content="Message 11")
        
        # Should still have 10 messages
        assert session.get_message_count() == 10
        
        # First message should now be "Message 2"
        first_msg_after = list(session.conversation_history)[0]
        assert first_msg_after.content == "Message 2"
        
        # Last message should be "Message 11"
        last_msg = session.get_last_message()
        assert last_msg.content == "Message 11"
        
        print("✓ 11th message correctly removes oldest")
        print(f"  - Messages after 11th: {session.get_message_count()}")
        print(f"  - New first message: {first_msg_after.content}")


class TestContextFormatting:
    """Test context formatting for LLM prompts."""
    
    def test_format_context_basic(self):
        """Test basic context formatting."""
        print("\n=== Test: Format Context Basic ===")
        
        session = Session(session_id="test_session_8", user_id="user123")
        
        session.add_message(role="user", content="I have a headache")
        session.add_message(role="assistant", content="How long have you had it?")
        session.add_message(role="user", content="About 2 hours")
        
        context = session.get_context_for_prompt()
        
        assert "Previous conversation:" in context
        assert "User: I have a headache" in context
        assert "Assistant: How long have you had it?" in context
        assert "User: About 2 hours" in context
        
        print("✓ Context formatted correctly")
        print("\nFormatted context:")
        print(context)
    
    def test_format_empty_context(self):
        """Test formatting empty context."""
        print("\n=== Test: Format Empty Context ===")
        
        session = Session(session_id="test_session_9", user_id="user123")
        
        context = session.get_context_for_prompt()
        
        assert context == ""
        
        print("✓ Empty context returns empty string")
    
    def test_pronoun_resolution_context(self):
        """Test that context supports pronoun resolution."""
        print("\n=== Test: Pronoun Resolution Context ===")
        
        session = Session(session_id="test_session_10", user_id="user123")
        
        # Simulate conversation with pronouns
        session.add_message(role="user", content="I've been having migraines")
        session.add_message(role="assistant", content="How often do you get them?")
        session.add_message(role="user", content="They happen about twice a week")
        
        context = session.get_context_for_prompt()
        
        # Context should include the antecedent for pronouns
        assert "migraines" in context
        assert "They happen" in context
        
        print("✓ Context supports pronoun resolution")
        print("\nContext for pronoun resolution:")
        print(context)


class TestSessionCleanup:
    """Test session cleanup functionality."""
    
    def test_clear_session(self):
        """Test clearing session context."""
        print("\n=== Test: Clear Session ===")
        
        session = Session(session_id="test_session_11", user_id="user123")
        
        # Add some messages
        session.add_message(role="user", content="Message 1")
        session.add_message(role="assistant", content="Message 2")
        session.add_message(role="user", content="Message 3")
        
        assert session.get_message_count() == 3
        
        # Clear the session
        session.clear()
        
        assert session.get_message_count() == 0
        assert session.get_last_message() is None
        assert session.get_context_for_prompt() == ""
        
        print("✓ Session cleared successfully")
    
    def test_session_after_clear(self):
        """Test that session can be used after clearing."""
        print("\n=== Test: Session After Clear ===")
        
        session = Session(session_id="test_session_12", user_id="user123")
        
        # Add messages, clear, then add more
        session.add_message(role="user", content="Before clear")
        session.clear()
        session.add_message(role="user", content="After clear")
        
        assert session.get_message_count() == 1
        last_msg = session.get_last_message()
        assert last_msg.content == "After clear"
        
        print("✓ Session works correctly after clearing")


class TestSessionRepresentation:
    """Test session string representation."""
    
    def test_session_repr(self):
        """Test session __repr__ method."""
        print("\n=== Test: Session Representation ===")
        
        session = Session(session_id="test_session_13", user_id="user123")
        session.add_message(role="user", content="Test message")
        
        repr_str = repr(session)
        
        assert "test_session_13" in repr_str
        assert "user123" in repr_str
        assert "messages=1" in repr_str
        
        print("✓ Session representation correct")
        print(f"  - Repr: {repr_str}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
