"""
Load Initial Data into AI Health Companion
Loads user history from CSV and medical knowledge from PDF
"""
import asyncio
import csv
import logging
from pathlib import Path
from database import Database
from user_history_agent import UserHistoryAgent
from knowledge_agent import KnowledgeSpecialistAgent
from response_cache import ResponseCache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def load_user_history_from_csv(csv_path: str, history_agent: UserHistoryAgent):
    """
    Load user history from CSV file into database
    
    Args:
        csv_path: Path to user_history.csv
        history_agent: UserHistoryAgent instance
    """
    logger.info(f"Loading user history from {csv_path}...")
    
    if not Path(csv_path).exists():
        logger.warning(f"CSV file not found: {csv_path}")
        return
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        count = 0
        
        for row in reader:
            user_id = row['user_id']
            
            # Parse known conditions (comma-separated)
            conditions = [c.strip() for c in row['known_conditions'].split(';') if c.strip()]
            
            # Store in database
            await history_agent.store_conversation(
                user_id=user_id,
                summary=row['conversation_summary'],
                symptoms=[],  # Will be extracted from summary if needed
                conditions=conditions,
                mental_health_notes=row['mental_health_notes']
            )
            
            count += 1
            logger.info(f"Loaded history for user {user_id} ({row['name']})")
    
    logger.info(f"✓ Loaded {count} user history records")


async def load_medical_knowledge_from_pdf(pdf_path: str, knowledge_agent: KnowledgeSpecialistAgent):
    """
    Load medical knowledge from PDF into ChromaDB
    
    Args:
        pdf_path: Path to medical_knowledge.pdf
        knowledge_agent: KnowledgeSpecialistAgent instance
    """
    logger.info(f"Loading medical knowledge from {pdf_path}...")
    
    if not Path(pdf_path).exists():
        logger.warning(f"PDF file not found: {pdf_path}")
        return
    
    # Create temporary directory with the PDF
    import shutil
    temp_dir = Path("knowledge_temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Copy PDF to temp directory
    shutil.copy(pdf_path, temp_dir / "medical_knowledge.pdf")
    
    # Initialize knowledge agent with temp directory
    await knowledge_agent.initialize(pdf_directory=str(temp_dir))
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    logger.info("✓ Medical knowledge loaded successfully")


async def main():
    """Main function to load all initial data"""
    logger.info("=== Loading Initial Data ===")
    
    # Initialize database
    database = Database("data/user_history.db")
    await database.initialize()
    
    # Initialize agents
    history_agent = UserHistoryAgent(database)
    response_cache = ResponseCache()
    knowledge_agent = KnowledgeSpecialistAgent(response_cache, chroma_persist_dir="./chroma_db")
    
    # Load user history from CSV (check both backend and parent directory)
    csv_path = "user_history.csv" if Path("user_history.csv").exists() else "../user_history.csv"
    await load_user_history_from_csv(csv_path, history_agent)
    
    # Load medical knowledge from PDF (check both backend and parent directory)
    pdf_path = "medical_knowledge.pdf" if Path("medical_knowledge.pdf").exists() else "../medical_knowledge.pdf"
    await load_medical_knowledge_from_pdf(pdf_path, knowledge_agent)
    
    logger.info("=== Initial Data Loading Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
