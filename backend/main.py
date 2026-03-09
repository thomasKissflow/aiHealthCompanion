"""
AI Health Companion - FastAPI Backend
Main application entry point
"""
import os
import uuid
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

# Import agents and components
from intent_classifier import IntentClassifier, Intent
from response_cache import ResponseCache
from supervisor_agent import SupervisorAgent
from metrics_tracker import MetricsTracker
from template_engine import TemplateResponseEngine
from risk_escalation_agent import RiskEscalationAgent
from mental_health_agent import MentalHealthAgent
from knowledge_agent import KnowledgeSpecialistAgent
from user_history_agent import UserHistoryAgent
from database import Database
from llm_client import LLMClient
from session import Session
from aws_connection_pool import AWSConnectionPool
from voice_interface import VoiceInterface
from transcribe_api import TranscribeService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Health Companion",
    description="Voice-first conversational AI for health guidance",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components (initialized on startup)
intent_classifier: Optional[IntentClassifier] = None
response_cache: Optional[ResponseCache] = None
supervisor_agent: Optional[SupervisorAgent] = None
metrics_tracker: Optional[MetricsTracker] = None
template_engine: Optional[TemplateResponseEngine] = None
aws_connection_pool: Optional[AWSConnectionPool] = None
voice_interface: Optional[VoiceInterface] = None
transcribe_service: Optional[TranscribeService] = None

# Session storage (in-memory for MVP)
sessions: Dict[str, Session] = {}


class QueryRequest(BaseModel):
    """Request model for /api/query endpoint"""
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = "default_user"


class QueryResponse(BaseModel):
    """Response model for /api/query endpoint"""
    response: str
    session_id: str
    intent: str
    used_fast_path: bool
    cache_hit: bool
    used_llm: bool
    immediate_feedback: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize all components on startup"""
    global intent_classifier, response_cache, supervisor_agent, metrics_tracker, template_engine, aws_connection_pool, voice_interface, transcribe_service
    
    logger.info("Initializing AI Health Companion backend...")
    
    try:
        # Initialize AWS connection pool
        aws_connection_pool = AWSConnectionPool(
            aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region=os.getenv("AWS_REGION", "us-east-1")
        )
        
        # Initialize voice interface
        voice_interface = VoiceInterface(aws_connection_pool)
        
        # Initialize transcribe service
        transcribe_service = TranscribeService(region=os.getenv("AWS_REGION", "us-east-1"))
        
        # Initialize components
        intent_classifier = IntentClassifier()
        response_cache = ResponseCache(max_size=1000, ttl_hours=24)
        metrics_tracker = MetricsTracker(log_interval=10)
        template_engine = TemplateResponseEngine()
        
        # Initialize LLM client
        llm_client = LLMClient(
            aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region=os.getenv("AWS_REGION", "us-east-1"),
            model="meta.llama3-8b-instruct-v1:0",
            timeout=10  # Increased to 10s for cold start
        )
        
        # Initialize specialized agents
        risk_agent = RiskEscalationAgent(template_engine)
        mental_health_agent = MentalHealthAgent(response_cache)
        knowledge_agent = KnowledgeSpecialistAgent(response_cache, chroma_persist_dir="./chroma_db")
        
        # Initialize knowledge agent with PDFs
        # First try root directory medical_knowledge.pdf, then backend/knowledge/
        from pathlib import Path
        import shutil
        
        if Path("medical_knowledge.pdf").exists():
            logger.info("[Startup] Loading medical_knowledge.pdf from root directory")
            # Copy to backend/knowledge for processing
            Path("backend/knowledge").mkdir(parents=True, exist_ok=True)
            shutil.copy("medical_knowledge.pdf", "backend/knowledge/medical_knowledge.pdf")
        
        await knowledge_agent.initialize(pdf_directory="backend/knowledge")
        
        # Initialize database and history agent
        # Create data directory if it doesn't exist
        Path("data").mkdir(parents=True, exist_ok=True)
        database = Database(db_path="data/user_history.db")
        await database.initialize()
        history_agent = UserHistoryAgent(database)
        
        # Initialize supervisor agent
        supervisor_agent = SupervisorAgent(
            intent_classifier=intent_classifier,
            risk_agent=risk_agent,
            mental_health_agent=mental_health_agent,
            knowledge_agent=knowledge_agent,
            history_agent=history_agent,
            template_engine=template_engine,
            llm_client=llm_client
        )
        
        logger.info("✓ All components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Main query processing endpoint
    
    Integrates:
    - Intent Classifier
    - Response Cache
    - Supervisor Agent
    - Metrics Tracker
    - Immediate feedback for complex queries
    
    Requirements: 14.5, 15.1, 15.2, 15.3, 15.4, 15.6
    """
    try:
        # Validate query
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in sessions:
            sessions[session_id] = Session(session_id, request.user_id)
        session = sessions[session_id]
        
        # Step 1: Classify intent
        intent, confidence = intent_classifier.classify(request.query)
        logger.info(f"[Query] Classified intent: {intent.value} (confidence: {confidence:.2f})")
        
        # Initialize tracking variables
        used_fast_path = False
        cache_hit = False
        used_llm = False
        immediate_feedback_phrase = None
        response_text = None
        
        # Step 2: Check if this is a fast path query
        if intent in [Intent.GREETING, Intent.ACKNOWLEDGMENT]:
            # Fast path - use template response
            used_fast_path = True
            if intent == Intent.GREETING:
                response_text = template_engine.get_greeting()
            else:
                response_text = template_engine.get_acknowledgment()
            logger.info("[LLM Agent] skipping model call")
        
        elif intent == Intent.RISK_SYMPTOM:
            # Fast path - use risk agent template
            used_fast_path = True
            from risk_escalation_agent import RiskEscalationAgent
            risk_agent = RiskEscalationAgent(template_engine)
            urgency, risk_response = risk_agent.classify_urgency(request.query)
            if risk_response:
                response_text = risk_response
                logger.info("[LLM Agent] skipping model call")
        
        # Step 3: Check cache for non-fast-path queries
        if not used_fast_path and response_text is None:
            cached_response = response_cache.get(request.query, {"intent": intent.value})
            if cached_response:
                cache_hit = True
                response_text = cached_response
                logger.info("[Cache] Response served from cache")
        
        # Step 4: Provide immediate feedback for complex queries
        if not used_fast_path and not cache_hit:
            # Complex query - provide immediate feedback
            immediate_feedback_phrase = template_engine.get_immediate_feedback()
            logger.info(f"[Immediate Feedback] {immediate_feedback_phrase}")
        
        # Step 5: Route to Supervisor Agent if needed
        if response_text is None:
            logger.info("[LLM Agent] invoking bedrock")
            used_llm = True
            response_text = await supervisor_agent.process_query(request.query, session)
            
            # Cache the response
            if response_text:
                response_cache.put(request.query, response_text, {"intent": intent.value})
        
        # Step 6: Track metrics
        metrics_tracker.record_query(
            used_fast_path=used_fast_path,
            cache_hit=cache_hit,
            used_llm=used_llm
        )
        
        # Return response
        return QueryResponse(
            response=response_text,
            session_id=session_id,
            intent=intent.value,
            used_fast_path=used_fast_path,
            cache_hit=cache_hit,
            used_llm=used_llm,
            immediate_feedback=immediate_feedback_phrase
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        
        # Graceful degradation - return fallback response
        fallback_response = template_engine.get_fallback_response()
        
        return QueryResponse(
            response=fallback_response,
            session_id=request.session_id or str(uuid.uuid4()),
            intent="error",
            used_fast_path=True,
            cache_hit=False,
            used_llm=False,
            immediate_feedback=None
        )


@app.delete("/api/session/{session_id}")
async def end_session(session_id: str):
    """
    End a session and clear its context
    
    Args:
        session_id: Session identifier
    """
    if session_id in sessions:
        sessions[session_id].clear()
        del sessions[session_id]
        logger.info(f"[Session] Ended session {session_id}")
        return {"status": "success", "message": f"Session {session_id} ended"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/api/metrics")
async def get_metrics():
    """Get current optimization metrics"""
    if metrics_tracker:
        return metrics_tracker.get_metrics_summary()
    return {"error": "Metrics tracker not initialized"}


@app.post("/api/voice/synthesize")
async def synthesize_speech(request: dict):
    """
    Synthesize speech from text using Amazon Polly
    
    Args:
        request: {"text": "text to synthesize", "session_id": "optional"}
    
    Returns:
        Audio data or error
    """
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        logger.info(f"[Voice API] Synthesizing: {text[:50]}...")
        
        # Synthesize using voice interface
        await voice_interface.synthesize_and_play(text)
        
        return {
            "status": "success",
            "message": "Speech synthesized and played"
        }
        
    except Exception as e:
        logger.error(f"[Voice API] Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/stop")
async def stop_voice():
    """Stop current voice playback (interruption)"""
    try:
        await voice_interface.stop_playback()
        logger.info("[Voice API] Playback stopped (interrupted)")
        return {"status": "success", "message": "Playback stopped"}
    except Exception as e:
        logger.error(f"[Voice API] Stop error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/transcribe")
async def transcribe_audio(request: dict):
    """
    Transcribe audio to text using Amazon Transcribe
    
    Args:
        request: {"audio": "base64_encoded_audio_data"}
    
    Returns:
        {"text": "transcribed text"} or error
    """
    try:
        import base64
        
        audio_base64 = request.get("audio", "")
        if not audio_base64:
            raise HTTPException(status_code=400, detail="Audio data is required")
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_base64)
        
        logger.info(f"[Transcribe API] Received {len(audio_bytes)} bytes")
        
        # Transcribe using Amazon Transcribe
        text = await transcribe_service.transcribe_audio_bytes(audio_bytes)
        
        if text:
            logger.info(f"[Transcribe API] Result: {text}")
            return {
                "status": "success",
                "text": text
            }
        else:
            logger.warning("[Transcribe API] No transcription result")
            return {
                "status": "error",
                "text": "",
                "message": "Could not transcribe audio"
            }
        
    except Exception as e:
        logger.error(f"[Transcribe API] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Health Companion",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "components": {
            "intent_classifier": intent_classifier is not None,
            "response_cache": response_cache is not None,
            "supervisor_agent": supervisor_agent is not None,
            "metrics_tracker": metrics_tracker is not None,
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Health Companion API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
