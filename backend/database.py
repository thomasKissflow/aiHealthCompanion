"""
SQLite database module for user history storage.

This module provides async database operations for storing and retrieving
user conversation history, symptoms, conditions, and mental health notes.
"""

import aiosqlite
import json
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class UserContext:
    """User context data model."""
    user_id: str
    conversation_summary: str
    previous_symptoms: List[str]
    known_conditions: List[str]
    mental_health_notes: str
    last_updated: datetime


class Database:
    """Async SQLite database manager for user history."""
    
    def __init__(self, db_path: str = "user_history.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def initialize(self) -> None:
        """
        Initialize database and create tables if they don't exist.
        
        Creates the user_history table with the following schema:
        - user_id (TEXT PRIMARY KEY): Unique user identifier
        - conversation_summary (TEXT): Summary of previous conversations
        - previous_symptoms (TEXT): JSON array of symptoms mentioned
        - known_conditions (TEXT): JSON array of known conditions (e.g., "migraines")
        - mental_health_notes (TEXT): Mental health context (e.g., "work-related stress")
        - last_updated (TIMESTAMP): Last update timestamp
        """
        self._connection = await aiosqlite.connect(self.db_path)
        
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS user_history (
                user_id TEXT PRIMARY KEY,
                conversation_summary TEXT,
                previous_symptoms TEXT,
                known_conditions TEXT,
                mental_health_notes TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self._connection.commit()
        print(f"[Database] initialized at {self.db_path}")
    
    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    async def get_user_context(self, user_id: str) -> Optional[UserContext]:
        """
        Retrieve user context from database.
        
        Args:
            user_id: User identifier
            
        Returns:
            UserContext if found, None otherwise
        """
        if not self._connection:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        cursor = await self._connection.execute(
            """
            SELECT user_id, conversation_summary, previous_symptoms, 
                   known_conditions, mental_health_notes, last_updated
            FROM user_history
            WHERE user_id = ?
            """,
            (user_id,)
        )
        
        row = await cursor.fetchone()
        await cursor.close()
        
        if not row:
            return None
        
        return UserContext(
            user_id=row[0],
            conversation_summary=row[1] or "",
            previous_symptoms=json.loads(row[2]) if row[2] else [],
            known_conditions=json.loads(row[3]) if row[3] else [],
            mental_health_notes=row[4] or "",
            last_updated=datetime.fromisoformat(row[5]) if row[5] else datetime.now()
        )
    
    async def store_user_context(
        self,
        user_id: str,
        conversation_summary: str = "",
        previous_symptoms: Optional[List[str]] = None,
        known_conditions: Optional[List[str]] = None,
        mental_health_notes: str = ""
    ) -> None:
        """
        Store or update user context in database.
        
        Args:
            user_id: User identifier
            conversation_summary: Summary of conversations
            previous_symptoms: List of symptoms mentioned
            known_conditions: List of known conditions (e.g., ["migraines"])
            mental_health_notes: Mental health context notes
        """
        if not self._connection:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        previous_symptoms = previous_symptoms or []
        known_conditions = known_conditions or []
        
        await self._connection.execute(
            """
            INSERT INTO user_history 
                (user_id, conversation_summary, previous_symptoms, 
                 known_conditions, mental_health_notes, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                conversation_summary = excluded.conversation_summary,
                previous_symptoms = excluded.previous_symptoms,
                known_conditions = excluded.known_conditions,
                mental_health_notes = excluded.mental_health_notes,
                last_updated = excluded.last_updated
            """,
            (
                user_id,
                conversation_summary,
                json.dumps(previous_symptoms),
                json.dumps(known_conditions),
                mental_health_notes,
                datetime.now().isoformat()
            )
        )
        
        await self._connection.commit()
