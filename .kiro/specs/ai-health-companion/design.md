# Design Document: AI Health Companion

## Overview

The AI Health Companion is a voice-first conversational AI system designed for health guidance with a focus on speed, responsiveness, and natural conversation flow. The architecture implements a hybrid fast/smart approach where 95% of queries are handled through rule-based fast paths without LLM calls, while complex reasoning is delegated to LLM only when necessary.

### Core Design Principles

1. **Demo-First Development**: The system prioritizes reliable execution of the demo script to ensure successful video recording
2. **Fast Path Optimization**: Rule-based pattern matching handles greetings, acknowledgments, and risk detection without LLM
3. **Aggressive Caching**: 40-60% cache hit rate reduces LLM calls by 30x for repeat queries
4. **Direct Streaming**: Audio streams directly to/from AWS services without file I/O (6x faster)
5. **Async Everything**: All operations are non-blocking with parallel agent execution
6. **Immediate Feedback**: Acknowledgment phrases spoken within 500ms while processing complex queries

### Performance Targets

- Simple queries (greetings, acknowledgments): <500ms
- Risk detection queries: 500-1000ms (rule-based + templates)
- Knowledge queries (first time): 2-3s (with immediate feedback)
- Knowledge queries (cached): <500ms
- Overall cache hit rate: 40-60% after 100 queries
- LLM usage reduction: 85% through optimization

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Voice Input  │  │ Chat Display │  │   Controls   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Voice Interface Layer                          │ │
│  │  ┌──────────────────┐      ┌──────────────────┐           │ │
│  │  │ Amazon Transcribe│      │  Amazon Polly    │           │ │
│  │  │  (Speech-to-Text)│      │ (Text-to-Speech) │           │ │
│  │  └──────────────────┘      └──────────────────┘           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           Intent Classification Layer (Fast Path)           │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Pattern Matcher (2ms response)                       │  │ │
│  │  │  - Regex/keyword matching                             │  │ │
│  │  │  - Intent: GREETING, SYMPTOM_CHECK, MENTAL_HEALTH,   │  │ │
│  │  │           RISK_SYMPTOM, KNOWLEDGE_QUERY, ACK          │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Response Cache Layer                           │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  LRU Cache (1000 entries, 24hr TTL)                   │  │ │
│  │  │  - Normalized query keys                              │  │ │
│  │  │  - 40-60% hit rate target                             │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Supervisor Agent (Orchestrator)                │ │
│  │  - Routes to specialized agents                             │ │
│  │  - Runs agents in parallel (async)                          │ │
│  │  - Aggregates responses                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐      ┌─────────────┐     ┌─────────────┐     │
│  │    Risk     │      │   Mental    │     │  Knowledge  │     │
│  │ Escalation  │      │   Health    │     │  Specialist │     │
│  │   Agent     │      │   Support   │     │    Agent    │     │
│  │             │      │    Agent    │     │             │     │
│  │ (Fast Path) │      │ (LLM+Cache) │     │(ChromaDB+LLM)│     │
│  └─────────────┘      └─────────────┘     └─────────────┘     │
│         │                    │                    │             │
│         └────────────────────┼────────────────────┘             │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              User History Agent                             │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  SQLite Database                                      │  │ │
│  │  │  - conversation_summary                               │  │ │
│  │  │  - previous_symptoms                                  │  │ │
│  │  │  - known_conditions (e.g., "migraines")               │  │ │
│  │  │  - mental_health_notes (e.g., "work-related stress")  │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Template Response Engine                       │ │
│  │  - Greetings (varied)                                       │ │
│  │  - Risk classifications (EMERGENCY, PROFESSIONAL, MONITOR)  │ │
│  │  - Acknowledgments                                          │ │
│  │  - Immediate feedback phrases                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              AWS Connection Pool                            │ │
│  │  - Reusable boto3 clients                                   │ │
│  │  - Transcribe, Polly, Bedrock                               │ │
│  │  - 100-200ms latency savings                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              LLM Layer (Bedrock)                            │ │
│  │  - OpenAI client → Bedrock endpoint                         │ │
│  │  - Model: openai.gpt-oss-120b                               │ │
│  │  - 3-second timeout with fallback                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow

#### Fast Path (Greeting Example)
```
User: "Hello"
  ↓
Voice Interface (Transcribe) → 200ms
  ↓
Intent Classifier → 2ms → GREETING detected
  ↓
Template Response Engine → 50ms
  ↓
Voice Interface (Polly) → 100ms
  ↓
Total: ~350ms
```

#### Cached Knowledge Query
```
User: "What causes headaches?"
  ↓
Voice Interface (Transcribe) → 200ms
  ↓
Intent Classifier → 2ms → KNOWLEDGE_QUERY
  ↓
Response Cache → HIT → 50ms
  ↓
Voice Interface (Polly) → 100ms
  ↓
Total: ~350ms
```

#### Complex Query (First Time)
```
User: "I have a headache and nausea"
  ↓
Voice Interface (Transcribe) → 200ms
  ↓
Intent Classifier → 2ms → SYMPTOM_CHECK
  ↓
Immediate Feedback → "Let me check that for you" → 300ms
  ↓
Parallel Execution:
  - Knowledge Agent (ChromaDB) → 500ms
  - History Agent (SQLite) → 100ms
  - LLM (Bedrock) → 1500ms
  ↓
Response Aggregation → 100ms
  ↓
Cache Store → 50ms
  ↓
Voice Interface (Polly) → 100ms
  ↓
Total: ~2.8s (perceived: ~1.5s due to immediate feedback)
```

## Components and Interfaces

### 1. Voice Interface Layer

**Responsibilities:**
- Capture audio input continuously
- Stream audio directly to Amazon Transcribe (no file I/O)
- Stream text to Amazon Polly for synthesis
- Play audio output immediately
- Handle interruptions (stop playback when user speaks)

**Interface:**
```python
class VoiceInterface:
    async def start_listening(self) -> None:
        """Start continuous audio capture"""
        
    async def stop_listening(self) -> None:
        """Stop audio capture"""
        
    async def transcribe_audio_stream(self, audio_stream) -> str:
        """Stream audio to Transcribe, return text"""
        
    async def synthesize_and_play(self, text: str) -> None:
        """Stream text to Polly and play audio"""
        
    async def stop_playback(self) -> None:
        """Immediately stop current audio playback"""
```

**Implementation Notes:**
- Use asyncio for non-blocking operations
- Direct streaming eliminates S3 round trips (6x faster)
- Target 100-200ms latency for voice processing
- Maintain audio stream state for interruption handling

### 2. Intent Classification Layer

**Responsibilities:**
- Fast pattern matching using regex/keywords (2ms response)
- Classify user intent without LLM
- Route to appropriate fast path or agent
- Log intent to terminal

**Interface:**
```python
class IntentClassifier:
    def classify(self, text: str) -> Intent:
        """Classify intent using pattern matching"""
        
    def get_confidence(self) -> float:
        """Return classification confidence score"""

class Intent(Enum):
    GREETING = "greeting"
    SYMPTOM_CHECK = "symptom_check"
    MENTAL_HEALTH = "mental_health"
    RISK_SYMPTOM = "risk_symptom"
    KNOWLEDGE_QUERY = "knowledge_query"
    ACKNOWLEDGMENT = "acknowledgment"
    UNKNOWN = "unknown"
```

**Pattern Matching Rules:**
```python
PATTERNS = {
    Intent.GREETING: [
        r'\b(hello|hi|hey|good morning|good afternoon)\b',
    ],
    Intent.SYMPTOM_CHECK: [
        r'\b(headache|nausea|pain|dizzy|fever|cough)\b',
    ],
    Intent.MENTAL_HEALTH: [
        r'\b(anxious|depressed|overwhelmed|hopeless|stressed|too much|can\'t keep up)\b',
    ],
    Intent.RISK_SYMPTOM: [
        r'\b(chest pain|trouble breathing|difficulty breathing|can\'t breathe)\b',
    ],
    Intent.KNOWLEDGE_QUERY: [
        r'\b(what|why|how|tell me about|explain)\b',
    ],
    Intent.ACKNOWLEDGMENT: [
        r'\b(okay|ok|yes|yeah|sure|thanks|thank you)\b',
    ],
}
```

### 3. Response Cache Layer

**Responsibilities:**
- Store LLM responses with normalized query keys
- Implement LRU eviction (1000 entries max)
- 24-hour TTL for cache entries
- Track cache hit/miss statistics
- Achieve 40-60% hit rate after 100 queries

**Interface:**
```python
class ResponseCache:
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self.hits = 0
        self.misses = 0
        
    def get(self, query: str, context: dict) -> Optional[str]:
        """Get cached response if exists and not expired"""
        
    def put(self, query: str, context: dict, response: str) -> None:
        """Store response in cache with LRU eviction"""
        
    def normalize_key(self, query: str, context: dict) -> str:
        """Generate normalized cache key"""
        
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        
    def log_stats(self) -> None:
        """Log cache statistics to terminal"""
```

**Cache Key Normalization:**
- Lowercase text
- Remove punctuation
- Stem common words
- Include relevant context (intent, user history flags)

### 4. Supervisor Agent

**Responsibilities:**
- Orchestrate request flow
- Route to specialized agents based on intent
- Run agents in parallel when independent
- Aggregate agent responses
- Log routing decisions to terminal

**Interface:**
```python
class SupervisorAgent:
    def __init__(self, 
                 risk_agent: RiskEscalationAgent,
                 mental_health_agent: MentalHealthSupportAgent,
                 knowledge_agent: KnowledgeSpecialistAgent,
                 history_agent: UserHistoryAgent):
        self.agents = {...}
        
    async def process_query(self, text: str, session: Session) -> str:
        """Process query and return response"""
        
    async def route_to_agents(self, intent: Intent, text: str, session: Session) -> List[AgentResponse]:
        """Route to appropriate agents in parallel"""
        
    def aggregate_responses(self, responses: List[AgentResponse]) -> str:
        """Combine agent responses into coherent reply"""
        
    def log_routing(self, intent: Intent, agents: List[str]) -> None:
        """Log routing decisions to terminal"""
```

**Routing Logic:**
```python
async def route_to_agents(self, intent: Intent, text: str, session: Session):
    agents_to_run = []
    
    if intent == Intent.GREETING:
        # Fast path - no agents needed
        return []
    
    if intent == Intent.SYMPTOM_CHECK:
        # Run in parallel: Knowledge + History + LLM
        agents_to_run = [
            self.knowledge_agent.retrieve(text),
            self.history_agent.get_context(session.user_id),
        ]
        
    if intent == Intent.MENTAL_HEALTH:
        agents_to_run.append(
            self.mental_health_agent.generate_support(text, session)
        )
        
    if intent == Intent.RISK_SYMPTOM:
        agents_to_run.append(
            self.risk_agent.classify_urgency(text)
        )
        
    # Run all agents concurrently
    return await asyncio.gather(*agents_to_run)
```

### 5. Risk Escalation Agent

**Responsibilities:**
- Rule-based pattern matching for high-risk symptoms
- Classify urgency: EMERGENCY, PROFESSIONAL, MONITOR
- Fast path processing (100ms target)
- Log urgency level to terminal

**Interface:**
```python
class RiskEscalationAgent:
    def classify_urgency(self, text: str) -> UrgencyLevel:
        """Classify urgency using rule-based patterns"""
        
    def get_template_response(self, level: UrgencyLevel) -> str:
        """Get template response for urgency level"""
        
    def log_urgency(self, level: UrgencyLevel) -> None:
        """Log urgency level to terminal"""

class UrgencyLevel(Enum):
    EMERGENCY = "EMERGENCY"
    PROFESSIONAL = "PROFESSIONAL"
    MONITOR = "MONITOR"
    NONE = "NONE"
```

**Risk Detection Rules:**
```python
EMERGENCY_PATTERNS = [
    r'\b(chest pain|heart attack|can\'t breathe|difficulty breathing|severe bleeding)\b',
]

PROFESSIONAL_PATTERNS = [
    r'\b(persistent|chronic|worsening|severe)\b',
]

MONITOR_PATTERNS = [
    r'\b(mild|occasional|sometimes)\b',
]
```

**Template Responses:**
```python
TEMPLATES = {
    UrgencyLevel.EMERGENCY: 
        "Chest pain combined with difficulty breathing can sometimes indicate a serious medical issue. "
        "I cannot provide medical advice, but those symptoms may require immediate medical attention. "
        "If someone is experiencing this right now, it's important to contact emergency services or "
        "seek medical care immediately.",
        
    UrgencyLevel.PROFESSIONAL:
        "I recommend scheduling an appointment with your doctor within the next few days.",
        
    UrgencyLevel.MONITOR:
        "Keep an eye on these symptoms. If they worsen, please consult a healthcare professional.",
}
```

### 6. Mental Health Support Agent

**Responsibilities:**
- Detect emotional distress keywords
- Generate empathetic, supportive responses
- Offer guided breathing/grounding exercises
- Check cache before LLM call
- Log supportive response generation

**Interface:**
```python
class MentalHealthSupportAgent:
    def __init__(self, llm_client, response_cache: ResponseCache):
        self.llm = llm_client
        self.cache = response_cache
        self.active_sessions: Set[str] = set()
        
    async def generate_support(self, text: str, session: Session) -> str:
        """Generate empathetic support response"""
        
    def activate_for_session(self, session_id: str) -> None:
        """Mark session as needing mental health support"""
        
    def is_active(self, session_id: str) -> bool:
        """Check if mental health support is active for session"""
        
    def get_breathing_exercise(self) -> str:
        """Return guided breathing exercise template"""
        
    def log_support_response(self) -> None:
        """Log supportive response generation"""
```

**Guided Exercise Template:**
```python
BREATHING_EXERCISE = """
Okay, let's try something simple.
Take a slow breath in through your nose…
and slowly exhale through your mouth.
Now look around and name five things you can see.
This can help bring your mind back to the present moment.
"""
```

### 7. Knowledge Specialist Agent

**Responsibilities:**
- Load and embed medical reference PDFs
- Store embeddings in ChromaDB
- Retrieve relevant context chunks
- Check cache before retrieval
- Cache generated responses
- Log chunk retrieval count

**Interface:**
```python
class KnowledgeSpecialistAgent:
    def __init__(self, 
                 chroma_client,
                 llm_client,
                 response_cache: ResponseCache):
        self.chroma = chroma_client
        self.llm = llm_client
        self.cache = response_cache
        self.collection = None
        
    async def initialize(self, pdf_paths: List[str]) -> None:
        """Load PDFs, generate embeddings, store in ChromaDB"""
        
    async def retrieve(self, query: str) -> List[str]:
        """Retrieve relevant context chunks"""
        
    async def generate_response(self, query: str, context: List[str]) -> str:
        """Generate response using LLM with context"""
        
    def log_retrieval(self, num_chunks: int) -> None:
        """Log number of chunks retrieved"""
```

**ChromaDB Schema:**
```python
collection_schema = {
    "name": "medical_knowledge",
    "metadata": {
        "description": "Medical reference knowledge base"
    },
    "embedding_function": "default",  # Uses sentence-transformers
}

document_schema = {
    "id": "chunk_id",
    "document": "chunk_text",
    "metadata": {
        "source": "pdf_filename",
        "page": "page_number",
        "chunk_index": "index",
    }
}
```

### 8. User History Agent

**Responsibilities:**
- Store conversation summaries in SQLite
- Maintain known conditions and mental health notes
- Retrieve previous context for current session
- Inject context into LLM prompts
- Log context retrieval

**Interface:**
```python
class UserHistoryAgent:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    async def initialize(self) -> None:
        """Create SQLite database and tables"""
        
    async def store_conversation(self, 
                                 user_id: str,
                                 summary: str,
                                 symptoms: List[str],
                                 conditions: List[str],
                                 mental_health_notes: str) -> None:
        """Store conversation summary"""
        
    async def get_context(self, user_id: str) -> UserContext:
        """Retrieve previous context for user"""
        
    def format_context_for_prompt(self, context: UserContext) -> str:
        """Format context for LLM prompt injection"""
        
    def log_context_retrieval(self, context: UserContext) -> None:
        """Log context retrieval to terminal"""

class UserContext:
    user_id: str
    conversation_summary: str
    previous_symptoms: List[str]
    known_conditions: List[str]  # e.g., ["migraines"]
    mental_health_notes: str  # e.g., "work-related stress"
```

**SQLite Schema:**
```sql
CREATE TABLE user_history (
    user_id TEXT PRIMARY KEY,
    conversation_summary TEXT,
    previous_symptoms TEXT,  -- JSON array
    known_conditions TEXT,   -- JSON array
    mental_health_notes TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 9. Template Response Engine

**Responsibilities:**
- Store pre-formatted response templates
- Support variable substitution
- Provide varied greetings
- Immediate feedback phrases
- Risk classification responses

**Interface:**
```python
class TemplateResponseEngine:
    def __init__(self):
        self.templates = self._load_templates()
        self.greeting_index = 0
        
    def get_greeting(self) -> str:
        """Get varied greeting (rotates through options)"""
        
    def get_acknowledgment(self) -> str:
        """Get random acknowledgment"""
        
    def get_immediate_feedback(self) -> str:
        """Get random immediate feedback phrase"""
        
    def get_risk_response(self, level: UrgencyLevel) -> str:
        """Get template response for risk level"""
        
    def substitute_variables(self, template: str, variables: dict) -> str:
        """Substitute variables in template"""
```

**Template Definitions:**
```python
TEMPLATES = {
    "greetings": [
        "Hi there, I'm glad you reached out. How are you feeling today?",
        "Hello! What's on your mind?",
        "Hey! How can I help you today?",
    ],
    "acknowledgments": [
        "I understand",
        "Got it",
        "Okay",
        "Thanks for sharing that",
    ],
    "immediate_feedback": [
        "Let me check that for you",
        "One moment please",
        "Looking that up now",
    ],
    "risk": {
        "EMERGENCY": "...",  # See Risk Agent section
        "PROFESSIONAL": "...",
        "MONITOR": "...",
    }
}
```

### 10. AWS Connection Pool

**Responsibilities:**
- Create and maintain reusable boto3 clients
- Reduce per-request latency by 100-200ms
- Handle connection failures gracefully
- Recreate clients as needed

**Interface:**
```python
class AWSConnectionPool:
    def __init__(self, 
                 aws_access_key: str,
                 aws_secret_key: str,
                 region: str):
        self.credentials = {...}
        self.clients = {}
        
    def get_transcribe_client(self):
        """Get or create Transcribe client"""
        
    def get_polly_client(self):
        """Get or create Polly client"""
        
    def get_bedrock_client(self):
        """Get or create Bedrock client"""
        
    def recreate_client(self, service_name: str):
        """Recreate client on failure"""
```

### 11. LLM Layer

**Responsibilities:**
- Interface with Amazon Bedrock via OpenAI client
- 3-second timeout with graceful degradation
- Log LLM invocations
- Track LLM usage metrics

**Interface:**
```python
class LLMClient:
    def __init__(self, 
                 api_key: str,
                 base_url: str,
                 model: str = "openai.gpt-oss-120b",
                 timeout: int = 3):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.timeout = timeout
        self.call_count = 0
        
    async def generate(self, 
                      prompt: str,
                      system_prompt: str = None,
                      temperature: float = 0.7) -> Optional[str]:
        """Generate response with timeout"""
        
    def log_invocation(self) -> None:
        """Log LLM invocation to terminal"""
        
    def get_usage_stats(self) -> dict:
        """Return LLM usage statistics"""
```

**Timeout Handling:**
```python
async def generate(self, prompt: str, ...) -> Optional[str]:
    try:
        response = await asyncio.wait_for(
            self.client.chat.completions.create(
                model=self.model,
                messages=[...],
                temperature=temperature,
            ),
            timeout=self.timeout
        )
        self.call_count += 1
        return response.choices[0].message.content
        
    except asyncio.TimeoutError:
        logger.warning(f"LLM call timed out after {self.timeout}s")
        return None  # Caller uses template fallback
```

### 12. Session Management

**Responsibilities:**
- Maintain in-memory conversation context
- Store last 10 conversation turns
- Resolve pronouns and references
- Clear context on session end

**Interface:**
```python
class Session:
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.conversation_history: Deque[Message] = deque(maxlen=10)
        self.created_at = datetime.now()
        
    def add_message(self, role: str, content: str) -> None:
        """Add message to conversation history"""
        
    def get_context_for_prompt(self) -> str:
        """Format conversation history for LLM prompt"""
        
    def clear(self) -> None:
        """Clear session context"""

class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
```

### 13. Metrics Tracker

**Responsibilities:**
- Track total queries
- Track fast path usage
- Track cache hits/misses
- Calculate LLM usage reduction
- Log metrics every 10 queries

**Interface:**
```python
class MetricsTracker:
    def __init__(self):
        self.total_queries = 0
        self.fast_path_queries = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.llm_calls = 0
        
    def record_query(self, used_fast_path: bool, cache_hit: bool, used_llm: bool) -> None:
        """Record query metrics"""
        
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        
    def get_llm_reduction(self) -> float:
        """Calculate LLM usage reduction percentage"""
        
    def log_metrics(self) -> None:
        """Log metrics to terminal every 10 queries"""
```

## Data Models

### Intent
```python
class Intent(Enum):
    GREETING = "greeting"
    SYMPTOM_CHECK = "symptom_check"
    MENTAL_HEALTH = "mental_health"
    RISK_SYMPTOM = "risk_symptom"
    KNOWLEDGE_QUERY = "knowledge_query"
    ACKNOWLEDGMENT = "acknowledgment"
    UNKNOWN = "unknown"
```

### UrgencyLevel
```python
class UrgencyLevel(Enum):
    EMERGENCY = "EMERGENCY"
    PROFESSIONAL = "PROFESSIONAL"
    MONITOR = "MONITOR"
    NONE = "NONE"
```

### UserContext
```python
@dataclass
class UserContext:
    user_id: str
    conversation_summary: str
    previous_symptoms: List[str]
    known_conditions: List[str]
    mental_health_notes: str
    last_updated: datetime
```

### Session
```python
@dataclass
class Session:
    session_id: str
    user_id: str
    conversation_history: Deque[Message]
    created_at: datetime
    
@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
```

### AgentResponse
```python
@dataclass
class AgentResponse:
    agent_name: str
    content: str
    metadata: dict
    processing_time_ms: float
```

### CacheEntry
```python
@dataclass
class CacheEntry:
    key: str
    response: str
    created_at: datetime
    expires_at: datetime
    hit_count: int
```


## Error Handling

### 1. Voice Interface Errors

**Transcription Failures:**
- Retry up to 3 times with exponential backoff
- If all retries fail, speak: "I'm sorry, I didn't catch that. Could you please repeat?"
- Log error to terminal with audio stream metadata

**Synthesis Failures:**
- Retry up to 2 times
- If all retries fail, display text response in UI without audio
- Log error to terminal

**Audio Stream Interruptions:**
- Gracefully handle mid-stream interruptions
- Clean up resources (close streams, release buffers)
- Resume listening immediately

### 2. LLM Timeout Handling

**3-Second Timeout:**
```python
try:
    response = await asyncio.wait_for(llm.generate(prompt), timeout=3.0)
except asyncio.TimeoutError:
    logger.warning("LLM timeout - using template fallback")
    response = template_engine.get_fallback_response(intent)
```

**Fallback Strategy:**
- Use template response appropriate for intent
- Log timeout event with query metadata
- Continue conversation without error message to user

### 3. Cache Errors

**Memory Pressure:**
- LRU eviction handles memory limits
- If eviction fails, clear entire cache and log warning
- Continue operation without cache

**Corrupted Cache Entries:**
- Skip corrupted entry
- Log corruption with key
- Fetch fresh response from LLM

### 4. Database Errors

**SQLite Connection Failures:**
- Retry connection up to 3 times
- If all retries fail, continue without history context
- Log error but don't block conversation

**ChromaDB Failures:**
- Retry query up to 2 times
- If all retries fail, use LLM without retrieved context
- Log error with query details

### 5. AWS Service Errors

**Connection Pool Failures:**
- Recreate failed client automatically
- If recreation fails 3 times, log critical error
- Attempt to continue with remaining services

**Rate Limiting:**
- Implement exponential backoff
- Queue requests if rate limit hit
- Inform user: "I'm experiencing high demand. One moment please."

**Service Unavailability:**
- Detect service outages
- Use fallback mechanisms (templates, cached responses)
- Log service status

### 6. Agent Coordination Errors

**Parallel Agent Failures:**
```python
try:
    results = await asyncio.gather(
        agent1.process(),
        agent2.process(),
        return_exceptions=True
    )
    
    # Filter out exceptions, use successful results
    successful_results = [r for r in results if not isinstance(r, Exception)]
    
    # Log failures
    for r in results:
        if isinstance(r, Exception):
            logger.error(f"Agent failed: {r}")
            
except Exception as e:
    logger.error(f"Agent coordination failed: {e}")
    # Use template fallback
```

**Partial Failures:**
- Continue with successful agent responses
- Don't block on single agent failure
- Aggregate available information

### 7. Demo Script Reliability

**Critical Path Protection:**
- Wrap demo script intents in try-except blocks
- Ensure terminal logging always succeeds
- Fallback to simple responses if complex processing fails
- Priority: demo must complete successfully even if features degrade

**Graceful Degradation:**
```python
async def process_demo_query(query: str) -> str:
    try:
        # Attempt full processing
        return await full_processing_pipeline(query)
    except Exception as e:
        logger.error(f"Full pipeline failed: {e}")
        try:
            # Fallback to template response
            return template_engine.get_response(query)
        except Exception as e2:
            logger.error(f"Template fallback failed: {e2}")
            # Last resort: generic response
            return "I'm here to help. Could you tell me more?"
```

## Testing Strategy

### Overview

The testing strategy employs a dual approach combining unit tests for specific examples and edge cases with property-based tests for universal correctness properties. This ensures both concrete bug detection and general correctness verification.

### Unit Testing

**Focus Areas:**
- Specific examples from demo script
- Edge cases and error conditions
- Integration points between components
- Template response variations
- Cache key normalization

**Example Unit Tests:**
```python
def test_greeting_intent_classification():
    classifier = IntentClassifier()
    assert classifier.classify("Hello") == Intent.GREETING
    assert classifier.classify("Hi there") == Intent.GREETING
    assert classifier.classify("Hey") == Intent.GREETING

def test_emergency_risk_detection():
    agent = RiskEscalationAgent()
    level = agent.classify_urgency("I have chest pain and can't breathe")
    assert level == UrgencyLevel.EMERGENCY

def test_cache_key_normalization():
    cache = ResponseCache()
    key1 = cache.normalize_key("What causes headaches?", {})
    key2 = cache.normalize_key("what causes headaches", {})
    assert key1 == key2

def test_template_greeting_variation():
    engine = TemplateResponseEngine()
    greetings = [engine.get_greeting() for _ in range(10)]
    assert len(set(greetings)) > 1  # Multiple variations

def test_demo_script_greeting():
    """Test exact demo script flow"""
    classifier = IntentClassifier()
    intent = classifier.classify("Hello")
    assert intent == Intent.GREETING
    
    template = TemplateResponseEngine()
    response = template.get_greeting()
    assert "how are you feeling" in response.lower() or "what's on your mind" in response.lower()
```

**Integration Tests:**
```python
async def test_symptom_check_flow():
    """Test full symptom check with all agents"""
    supervisor = SupervisorAgent(...)
    response = await supervisor.process_query(
        "I have a headache and nausea",
        session
    )
    assert "migraine" in response.lower()
    assert len(response) > 0

async def test_mental_health_activation():
    """Test mental health agent activation"""
    supervisor = SupervisorAgent(...)
    response = await supervisor.process_query(
        "I'm feeling really anxious",
        session
    )
    assert mental_health_agent.is_active(session.session_id)
```

### Property-Based Testing

**Configuration:**
- Library: Hypothesis (Python)
- Minimum 100 iterations per property test
- Each test tagged with: `# Feature: ai-health-companion, Property {N}: {description}`

**Property Test Structure:**
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=200))
def test_property_name(input_text):
    """
    Feature: ai-health-companion, Property 1: Description
    Validates: Requirements X.Y
    """
    # Test implementation
    pass
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Fast Path Bypasses LLM

*For any* query classified as GREETING, ACKNOWLEDGMENT, or RISK_SYMPTOM intent, the system should respond without invoking the LLM (Bedrock) and should complete within the fast-path performance target.

**Validates: Requirements 1.1, 5.4, 7.1, 7.6, 13.1**

### Property 2: Intent Classification Determinism

*For any* user input text, the Intent_Classifier should produce the same intent classification when given the same input, and should recognize all defined intent categories (GREETING, SYMPTOM_CHECK, MENTAL_HEALTH, RISK_SYMPTOM, KNOWLEDGE_QUERY, ACKNOWLEDGMENT, UNKNOWN).

**Validates: Requirements 5.1, 5.3**

### Property 3: Correct Agent Routing

*For any* classified intent, the Supervisor_Agent should route to the appropriate specialized agent(s): RISK_SYMPTOM → Risk_Escalation_Agent, MENTAL_HEALTH → Mental_Health_Support_Agent, SYMPTOM_CHECK/KNOWLEDGE_QUERY → Knowledge_Specialist_Agent, and UNKNOWN → Supervisor_Agent for LLM analysis.

**Validates: Requirements 5.5, 5.6, 5.7, 5.8, 6.2**

### Property 4: Emergency Symptom Detection

*For any* text containing emergency symptom keywords (chest pain, difficulty breathing, can't breathe, severe bleeding), the Risk_Escalation_Agent should classify the urgency level as EMERGENCY and use a template response without LLM invocation.

**Validates: Requirements 1.5, 7.3, 7.4, 7.6**

### Property 5: Mental Health Agent Activation

*For any* text containing emotional distress keywords (anxious, depressed, overwhelmed, hopeless, stressed, too much, can't keep up), the Mental_Health_Support_Agent should activate and remain active for the duration of the session.

**Validates: Requirements 1.3, 8.1, 8.2**

### Property 6: Medical Advice Prohibition

*For any* response generated by the system (whether from templates, cache, or LLM), the response should not contain medical diagnoses (keywords like "you have", "diagnosed with", "condition is") or specific medication recommendations (drug names from a medication list).

**Validates: Requirements 8.4, 8.5, 17.5, 17.6**

### Property 7: Response Caching Round Trip

*For any* query that requires LLM invocation, if the same normalized query (same text and context) is submitted twice, the second request should be served from cache without invoking the LLM again.

**Validates: Requirements 11.2, 11.4**

### Property 8: Cache LRU Eviction

*For any* sequence of cache insertions exceeding the maximum size (1000 entries), the least recently used entries should be evicted first, maintaining the cache size at or below the maximum.

**Validates: Requirements 11.6**

### Property 9: Cache TTL Expiration

*For any* cached entry, if more than 24 hours have elapsed since creation, the entry should be considered expired and not returned on cache lookup, requiring a fresh LLM call.

**Validates: Requirements 11.8**

### Property 10: Template Response Variation

*For any* sequence of greeting requests across different sessions, the system should use varied greeting templates (not the same greeting every time), demonstrating at least 2 different greeting variations.

**Validates: Requirements 12.2, 17.1**

### Property 11: Session Context Retention

*For any* session, the system should maintain the last 10 conversation turns in memory, and when an 11th turn is added, the oldest turn should be removed (FIFO with size limit).

**Validates: Requirements 16.4**

### Property 12: Pronoun Resolution

*For any* user input containing pronouns (it, that, them, this) within an active session with conversation history, the system should inject the session context into the LLM prompt to enable pronoun resolution.

**Validates: Requirements 16.2, 16.6**

### Property 13: History Context Injection

*For any* user with stored history (known conditions, previous symptoms, mental health notes), when that user submits a query, the system should retrieve and inject the relevant historical context into the LLM prompt.

**Validates: Requirements 1.4, 10.3, 10.4, 10.9**

### Property 14: Connection Pool Reuse

*For any* sequence of AWS service requests (Transcribe, Polly, Bedrock), the system should reuse boto3 clients from the connection pool rather than creating new clients for each request.

**Validates: Requirements 18.2, 18.3, 18.4**

### Property 15: Metrics Tracking Accuracy

*For any* query processed by the system, the appropriate metrics should be incremented: total_queries always increments, fast_path_queries increments when no LLM is used, cache_hits increments on cache hit, cache_misses increments on cache miss, and llm_calls increments when LLM is invoked.

**Validates: Requirements 19.1, 19.2, 19.3, 19.4**

### Property 16: Cache Hit Rate Calculation

*For any* state of the metrics tracker with N cache hits and M cache misses, the calculated cache hit rate should equal N / (N + M) * 100, representing the percentage of queries served from cache.

**Validates: Requirements 19.5**

### Property 17: LLM Usage Reduction Calculation

*For any* state of the metrics tracker with T total queries and L LLM calls, the calculated LLM usage reduction should equal (1 - L / T) * 100, representing the percentage of queries that avoided LLM calls.

**Validates: Requirements 19.6**

### Property 18: Comprehensive Agent Logging

*For any* agent operation (intent classification, routing decision, risk evaluation, mental health activation, knowledge retrieval, history retrieval, LLM invocation), the system should produce appropriate terminal logs in the specified format (e.g., "[Supervisor] intent: {intent}", "[Risk Agent] urgency level: {level}").

**Validates: Requirements 5.9, 6.3, 6.7, 7.5, 7.8, 8.8, 9.7, 10.7, 13.7**

### Property 19: Immediate Feedback Conditional Usage

*For any* query, if the query uses the fast path (completes within 500ms), the system should not speak immediate feedback phrases; immediate feedback should only be used for complex queries requiring LLM or knowledge retrieval.

**Validates: Requirements 15.6**

### Property 20: Greeting Variation Across Sessions

*For any* two consecutive new sessions, the greeting template used should differ, demonstrating that the system rotates through available greeting variations rather than repeating the same greeting.

**Validates: Requirements 17.1, 17.2**

### Property 21: Parallel Agent Execution

*For any* query requiring multiple independent agents (e.g., Knowledge_Specialist_Agent and User_History_Agent), the agents should execute concurrently (in parallel) rather than sequentially, with the total execution time being closer to the maximum individual agent time rather than the sum of all agent times.

**Validates: Requirements 6.4**

### Property 22: Response Aggregation Completeness

*For any* query that triggers multiple agents, the Supervisor_Agent should aggregate all successful agent responses into the final response, ensuring no agent output is lost (unless the agent failed).

**Validates: Requirements 6.5**

### Property 23: Timeout Fallback Behavior

*For any* LLM call that exceeds the 3-second timeout, the system should cancel the request, log a timeout event, and return a template-based fallback response appropriate for the intent, ensuring the conversation continues without error.

**Validates: Requirements 13.6, 13.7**

### Property 24: Session Context Cleanup

*For any* session, when the session ends, the in-memory conversation history should be cleared, ensuring no context leaks between sessions.

**Validates: Requirements 16.5**

### Property 25: History Data Minimization

*For any* conversation stored by the User_History_Agent, only summary data (conversation_summary, previous_symptoms, known_conditions, mental_health_notes) should be stored, not detailed medical records or full conversation transcripts.

**Validates: Requirements 10.5**

### Property 26: Varied Immediate Feedback Phrases

*For any* sequence of complex queries requiring immediate feedback, the system should use varied immediate feedback phrases (at least 2 different phrases like "Let me check that for you", "One moment please", "Looking that up now") rather than the same phrase every time.

**Validates: Requirements 15.2**

### Property 27: Follow-Up Question Generation

*For any* symptom-related query, the system should generate follow-up questions to clarify user concerns (e.g., "When did the headache start, and is the pain throbbing or constant?"), demonstrating conversational engagement.

**Validates: Requirements 17.2**

