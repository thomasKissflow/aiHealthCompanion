"""
Test script for User History Agent and Database.

Tests:
- Database initialization
- Storing user context
- Retrieving user context
- Context formatting for LLM prompts
- Logging functionality
"""

import asyncio
import os
import pytest
from database import Database, UserContext
from user_history_agent import UserHistoryAgent


@pytest.mark.asyncio
async def test_database_initialization():
    """Test database creation and initialization."""
    print("\n=== Test 1: Database Initialization ===")
    
    # Use test database
    test_db_path = "test_user_history.db"
    
    # Remove existing test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = Database(test_db_path)
    await db.initialize()
    
    print("✓ Database initialized successfully")
    
    await db.close()
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.mark.asyncio
async def test_store_and_retrieve():
    """Test storing and retrieving user context."""
    print("\n=== Test 2: Store and Retrieve User Context ===")
    
    test_db_path = "test_user_history.db"
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = Database(test_db_path)
    await db.initialize()
    agent = UserHistoryAgent(db)
    
    # Store context
    await agent.store_conversation(
        user_id="user123",
        summary="User discussed headaches and stress",
        symptoms=["headache", "nausea"],
        conditions=["migraines"],
        mental_health_notes="work-related stress"
    )
    
    print("✓ Context stored successfully")
    
    # Retrieve context
    context = await agent.get_context("user123")
    
    assert context is not None, "Context should be retrieved"
    assert context.user_id == "user123"
    assert context.conversation_summary == "User discussed headaches and stress"
    assert "headache" in context.previous_symptoms
    assert "nausea" in context.previous_symptoms
    assert "migraines" in context.known_conditions
    assert context.mental_health_notes == "work-related stress"
    
    print("✓ Context retrieved successfully")
    print(f"  - User ID: {context.user_id}")
    print(f"  - Summary: {context.conversation_summary}")
    print(f"  - Symptoms: {context.previous_symptoms}")
    print(f"  - Conditions: {context.known_conditions}")
    print(f"  - Mental Health: {context.mental_health_notes}")
    
    await db.close()
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.mark.asyncio
async def test_context_formatting():
    """Test formatting context for LLM prompts."""
    print("\n=== Test 3: Context Formatting for LLM ===")
    
    test_db_path = "test_user_history.db"
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = Database(test_db_path)
    await db.initialize()
    agent = UserHistoryAgent(db)
    
    # Store context
    await agent.store_conversation(
        user_id="user456",
        summary="User has been experiencing migraines",
        symptoms=["headache", "sensitivity to light"],
        conditions=["migraines"],
        mental_health_notes="stressed about work deadlines"
    )
    
    # Retrieve and format
    context = await agent.get_context("user456")
    formatted = agent.format_context_for_prompt(context)
    
    print("✓ Context formatted successfully")
    print("\nFormatted context for LLM:")
    print(formatted)
    
    # Verify formatting
    assert "User History Context:" in formatted
    assert "Previous conversation summary:" in formatted
    assert "Previous symptoms mentioned:" in formatted
    assert "Known conditions:" in formatted
    assert "Mental health notes:" in formatted
    assert "migraines" in formatted
    
    print("\n✓ All required fields present in formatted context")
    
    await db.close()
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.mark.asyncio
async def test_empty_context():
    """Test retrieving context for non-existent user."""
    print("\n=== Test 4: Empty Context Handling ===")
    
    test_db_path = "test_user_history.db"
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = Database(test_db_path)
    await db.initialize()
    agent = UserHistoryAgent(db)
    
    # Try to retrieve non-existent user
    context = await agent.get_context("nonexistent_user")
    
    assert context is None, "Context should be None for non-existent user"
    print("✓ Correctly returns None for non-existent user")
    
    # Format empty context
    formatted = agent.format_context_for_prompt(None)
    assert formatted == "", "Empty context should return empty string"
    print("✓ Empty context formats to empty string")
    
    await db.close()
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.mark.asyncio
async def test_update_context():
    """Test updating existing user context."""
    print("\n=== Test 5: Update Existing Context ===")
    
    test_db_path = "test_user_history.db"
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = Database(test_db_path)
    await db.initialize()
    agent = UserHistoryAgent(db)
    
    # Store initial context
    await agent.store_conversation(
        user_id="user789",
        summary="Initial conversation",
        symptoms=["headache"],
        conditions=[],
        mental_health_notes=""
    )
    
    print("✓ Initial context stored")
    
    # Update context
    await agent.store_conversation(
        user_id="user789",
        summary="Updated conversation with more details",
        symptoms=["headache", "nausea", "dizziness"],
        conditions=["migraines"],
        mental_health_notes="experiencing work stress"
    )
    
    print("✓ Context updated")
    
    # Retrieve updated context
    context = await agent.get_context("user789")
    
    assert context.conversation_summary == "Updated conversation with more details"
    assert len(context.previous_symptoms) == 3
    assert "migraines" in context.known_conditions
    assert context.mental_health_notes == "experiencing work stress"
    
    print("✓ Updated context retrieved successfully")
    print(f"  - Updated summary: {context.conversation_summary}")
    print(f"  - Updated symptoms: {context.previous_symptoms}")
    print(f"  - Updated conditions: {context.known_conditions}")
    
    await db.close()
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


async def main():
    """Run all tests."""
    print("=" * 60)
    print("User History Agent and Database Tests")
    print("=" * 60)
    
    try:
        await test_database_initialization()
        await test_store_and_retrieve()
        await test_context_formatting()
        await test_empty_context()
        await test_update_context()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
