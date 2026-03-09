# Implementation Plan: AI Health Companion

## Overview

This implementation plan focuses on building a demo-ready AI Health Companion with voice-first conversational AI. The priority is ensuring the demo script executes reliably for video recording, with deployment to Vercel for live judge testing. The architecture implements a hybrid fast/smart approach with aggressive caching and direct streaming for optimal performance.

**Key Priorities:**
1. Demo script reliability (must work for video recording)
2. Live deployment on Vercel with working API keys
3. Fast path optimization (85% LLM reduction)
4. Voice streaming (no file I/O)
5. Async operations throughout

## Tasks

- [x] 1. Project Setup and Environment Configuration
  - Create project directory structure: `backend/`, `frontend/`, `docs/`
  - Set up Python virtual environment for backend
  - Create `.env.example` file with required environment variables
  - Create `.env` file for local development (AWS credentials, Bedrock endpoint)
  - Set up `.gitignore` to exclude `.env`, `__pycache__`, `node_modules`, etc.
  - Initialize git repository
  - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5, 23.6, 23.7_

- [x] 2. Backend Core Infrastructure
  - [x] 2.1 Install Python dependencies
    - Install FastAPI, uvicorn, python-dotenv, openai, boto3, chromadb, aiosqlite, asyncio
    - Create `requirements.txt` file
    - _Requirements: 24.1, 24.3, 24.4_
  
  - [x] 2.2 Create FastAPI application skeleton
    - Create `backend/main.py` with FastAPI app initialization
    - Set up CORS middleware for frontend communication
    - Create health check endpoint `/health`
    - Load environment variables from `.env`
    - _Requirements: 24.2, 24.5_
  
  - [x] 2.3 Implement AWS Connection Pool
    - Create `backend/aws_connection_pool.py`
    - Initialize boto3 clients for Transcribe, Polly, and Bedrock
    - Implement client reuse logic
    - Add connection failure handling and client recreation
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.6_
  
  - [ ]* 2.4 Write unit tests for AWS Connection Pool
    - Test client creation and reuse
    - Test connection failure recovery
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.6_

- [x] 3. Intent Classification and Fast Path
  - [x] 3.1 Implement Intent Classifier
    - Create `backend/intent_classifier.py`
    - Define Intent enum (GREETING, SYMPTOM_CHECK, MENTAL_HEALTH, RISK_SYMPTOM, KNOWLEDGE_QUERY, ACKNOWLEDGMENT, UNKNOWN)
    - Implement pattern matching using regex for each intent category
    - Add confidence scoring
    - Add terminal logging for detected intents
    - _Requirements: 5.1, 5.2, 5.3, 5.9_
  
  - [ ]* 3.2 Write property test for Intent Classifier
    - **Property 2: Intent Classification Determinism**
    - **Validates: Requirements 5.1, 5.3**
    - Test that same input produces same intent classification
    - Test that all intent categories are recognized
  
  - [x] 3.3 Implement Template Response Engine
    - Create `backend/template_engine.py`
    - Define greeting templates with variations
    - Define acknowledgment templates
    - Define immediate feedback phrases
    - Define risk classification templates (EMERGENCY, PROFESSIONAL, MONITOR)
    - Implement greeting rotation logic
    - Implement variable substitution
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_
  
  - [ ]* 3.4 Write property test for Template Response Engine
    - **Property 10: Template Response Variation**
    - **Validates: Requirements 12.2, 17.1**
    - Test that greetings vary across sessions
    - Test that at least 2 different greeting variations exist

- [x] 4. Response Caching System
  - [x] 4.1 Implement Response Cache
    - Create `backend/response_cache.py`
    - Implement LRU cache with OrderedDict (max 1000 entries)
    - Implement cache key normalization (lowercase, remove punctuation, stemming)
    - Implement 24-hour TTL for cache entries
    - Add cache hit/miss tracking
    - Add cache statistics logging
    - _Requirements: 11.1, 11.2, 11.6, 11.7, 11.8_
  
  - [ ]* 4.2 Write property test for cache LRU eviction
    - **Property 8: Cache LRU Eviction**
    - **Validates: Requirements 11.6**
    - Test that LRU eviction maintains cache size at or below maximum
  
  - [ ]* 4.3 Write property test for cache TTL expiration
    - **Property 9: Cache TTL Expiration**
    - **Validates: Requirements 11.8**
    - Test that entries older than 24 hours are expired
  
  - [ ]* 4.4 Write property test for cache round trip
    - **Property 7: Response Caching Round Trip**
    - **Validates: Requirements 11.2, 11.4**
    - Test that same query is served from cache on second request

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Risk Escalation Agent (Fast Path)
  - [x] 6.1 Implement Risk Escalation Agent
    - Create `backend/risk_escalation_agent.py`
    - Define UrgencyLevel enum (EMERGENCY, PROFESSIONAL, MONITOR, NONE)
    - Implement rule-based pattern matching for emergency symptoms
    - Implement urgency classification logic
    - Add terminal logging for urgency levels
    - Return template responses for each urgency level
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_
  
  - [ ]* 6.2 Write property test for emergency detection
    - **Property 4: Emergency Symptom Detection**
    - **Validates: Requirements 1.5, 7.3, 7.4, 7.6**
    - Test that emergency symptoms trigger EMERGENCY classification
    - Test that template response is used without LLM
  
  - [ ]* 6.3 Write unit tests for risk classification
    - Test chest pain detection
    - Test breathing difficulty detection
    - Test PROFESSIONAL and MONITOR classifications
    - _Requirements: 7.3, 7.4_

- [x] 7. Mental Health Support Agent
  - [x] 7.1 Implement Mental Health Support Agent
    - Create `backend/mental_health_agent.py`
    - Implement emotional distress keyword detection
    - Implement session activation tracking
    - Integrate with Response Cache
    - Add guided breathing exercise template
    - Add terminal logging for supportive responses
    - _Requirements: 8.1, 8.2, 8.3, 8.6, 8.7, 8.8_
  
  - [ ]* 7.2 Write property test for mental health activation
    - **Property 5: Mental Health Agent Activation**
    - **Validates: Requirements 1.3, 8.1, 8.2**
    - Test that distress keywords activate agent
    - Test that agent remains active for session duration
  
  - [ ]* 7.3 Write property test for medical advice prohibition
    - **Property 6: Medical Advice Prohibition**
    - **Validates: Requirements 8.4, 8.5, 17.5, 17.6**
    - Test that responses don't contain diagnoses
    - Test that responses don't contain medication names
  
  - [x] 7.4 Write unit test for guided breathing exercise
    - Test that breathing exercise is offered when user accepts support
    - _Requirements: 8.7_

- [x] 8. User History Agent and Database
  - [x] 8.1 Implement SQLite database schema
    - Create `backend/database.py`
    - Define user_history table schema
    - Implement async database initialization
    - _Requirements: 10.1, 10.2_
  
  - [x] 8.2 Implement User History Agent
    - Create `backend/user_history_agent.py`
    - Implement conversation storage (summary, symptoms, conditions, mental health notes)
    - Implement context retrieval
    - Implement context formatting for LLM prompts
    - Add terminal logging for context retrieval
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.7, 10.8, 10.9_
  
  - [ ]* 8.3 Write property test for history context injection
    - **Property 13: History Context Injection**
    - **Validates: Requirements 1.4, 10.3, 10.4, 10.9**
    - Test that stored history is retrieved and injected into prompts
  
  - [ ]* 8.4 Write property test for data minimization
    - **Property 25: History Data Minimization**
    - **Validates: Requirements 10.5**
    - Test that only summary data is stored, not full transcripts

- [x] 9. Knowledge Specialist Agent and ChromaDB
  - [x] 9.1 Set up ChromaDB and implement knowledge loading
    - Create `backend/knowledge_agent.py`
    - Initialize ChromaDB client and collection
    - Implement PDF loading and chunking logic
    - Implement embedding generation
    - Store embeddings in ChromaDB
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [x] 9.2 Implement knowledge retrieval with caching
    - Implement cache-first retrieval logic
    - Implement semantic search in ChromaDB
    - Add terminal logging for chunk retrieval count
    - Cache generated responses
    - _Requirements: 9.5, 9.6, 9.7, 9.8, 9.9, 9.10_
  
  - [x] 9.3 Add sample medical knowledge PDFs
    - Create `backend/knowledge/` directory
    - Add sample PDF about migraines/headaches
    - Add sample PDF about common symptoms
    - _Requirements: 9.1_
  
  - [ ]* 9.4 Write unit tests for knowledge retrieval
    - Test PDF loading and chunking
    - Test embedding generation
    - Test ChromaDB storage
    - Test cache-first behavior
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. LLM Client with Bedrock Integration
  - [x] 11.1 Implement LLM Client
    - Create `backend/llm_client.py`
    - Configure OpenAI client with Bedrock endpoint
    - Set model to openai.gpt-oss-120b
    - Implement 3-second timeout with asyncio.wait_for
    - Implement timeout fallback to template responses
    - Add terminal logging for LLM invocations and timeouts
    - Track LLM call count
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7_
  
  - [ ]* 11.2 Write property test for fast path LLM bypass
    - **Property 1: Fast Path Bypasses LLM**
    - **Validates: Requirements 1.1, 5.4, 7.1, 7.6, 13.1**
    - Test that GREETING, ACKNOWLEDGMENT, RISK_SYMPTOM intents don't invoke LLM
  
  - [ ]* 11.3 Write property test for timeout fallback
    - **Property 23: Timeout Fallback Behavior**
    - **Validates: Requirements 13.6, 13.7**
    - Test that timeouts trigger fallback responses
    - Test that timeout events are logged

- [x] 12. Session Management
  - [x] 12.1 Implement Session class
    - Create `backend/session.py`
    - Implement conversation history storage (last 10 turns)
    - Implement context formatting for LLM prompts
    - Implement session cleanup
    - _Requirements: 16.1, 16.4, 16.5, 16.6_
  
  - [ ]* 12.2 Write property test for session context retention
    - **Property 11: Session Context Retention**
    - **Validates: Requirements 16.4**
    - Test that last 10 turns are maintained
    - Test that 11th turn removes oldest
  
  - [ ]* 12.3 Write property test for session cleanup
    - **Property 24: Session Context Cleanup**
    - **Validates: Requirements 16.5**
    - Test that context is cleared on session end
  
  - [ ]* 12.4 Write property test for pronoun resolution
    - **Property 12: Pronoun Resolution**
    - **Validates: Requirements 16.2, 16.6**
    - Test that session context is injected for pronoun resolution

- [x] 13. Supervisor Agent and Orchestration
  - [x] 13.1 Implement Supervisor Agent
    - Create `backend/supervisor_agent.py`
    - Implement agent routing logic based on intent
    - Implement parallel agent execution with asyncio.gather
    - Implement response aggregation
    - Add terminal logging for routing decisions
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_
  
  - [ ]* 13.2 Write property test for correct agent routing
    - **Property 3: Correct Agent Routing**
    - **Validates: Requirements 5.5, 5.6, 5.7, 5.8, 6.2**
    - Test that each intent routes to correct agent(s)
  
  - [ ]* 13.3 Write property test for parallel execution
    - **Property 21: Parallel Agent Execution**
    - **Validates: Requirements 6.4**
    - Test that independent agents run concurrently
  
  - [ ]* 13.4 Write property test for response aggregation
    - **Property 22: Response Aggregation Completeness**
    - **Validates: Requirements 6.5**
    - Test that all successful agent responses are aggregated

- [ ] 14. Metrics Tracking
  - [x] 14.1 Implement Metrics Tracker
    - Create `backend/metrics_tracker.py`
    - Track total queries, fast path queries, cache hits/misses, LLM calls
    - Implement cache hit rate calculation
    - Implement LLM usage reduction calculation
    - Add periodic logging (every 10 queries)
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7_
  
  - [ ]* 14.2 Write property test for metrics tracking
    - **Property 15: Metrics Tracking Accuracy**
    - **Validates: Requirements 19.1, 19.2, 19.3, 19.4**
    - Test that appropriate metrics are incremented for each query type
  
  - [ ]* 14.3 Write property test for cache hit rate calculation
    - **Property 16: Cache Hit Rate Calculation**
    - **Validates: Requirements 19.5**
    - Test that hit rate formula is correct
  
  - [ ]* 14.4 Write property test for LLM reduction calculation
    - **Property 17: LLM Usage Reduction Calculation**
    - **Validates: Requirements 19.6**
    - Test that reduction formula is correct

- [x] 15. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 16. Voice Interface Layer
  - [x] 16.1 Implement Voice Interface for Transcribe
    - Create `backend/voice_interface.py`
    - Implement async audio streaming to Amazon Transcribe
    - Implement direct streaming (no file I/O)
    - Add interruption handling (stop playback on new input)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 16.2 Implement Voice Interface for Polly
    - Implement async text streaming to Amazon Polly
    - Implement direct audio streaming (no file I/O)
    - Implement immediate audio playback
    - Implement resume listening after playback
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 16.3 Implement interruption handling
    - Implement stop playback on user speech
    - Implement audio buffer cleanup
    - Implement immediate new input processing
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x]* 16.4 Write unit tests for voice interface
    - Test direct streaming (no file I/O)
    - Test interruption handling
    - Test async operations
    - _Requirements: 2.2, 2.5, 3.1, 3.3, 4.1, 4.2, 4.3_

- [x] 17. Main Request Processing Pipeline
  - [x] 17.1 Implement main query processing endpoint
    - Create `/api/query` POST endpoint in `backend/main.py`
    - Integrate Intent Classifier
    - Integrate Response Cache
    - Integrate Supervisor Agent
    - Integrate Metrics Tracker
    - Implement immediate feedback for complex queries
    - Add comprehensive error handling
    - _Requirements: 14.5, 15.1, 15.2, 15.3, 15.4, 15.6_
  
  - [x]* 17.2 Write property test for immediate feedback conditional usage
    - **Property 19: Immediate Feedback Conditional Usage**
    - **Validates: Requirements 15.6**
    - Test that fast path queries skip immediate feedback
    - Test that complex queries use immediate feedback
  
  - [x]* 17.3 Write property test for comprehensive logging
    - **Property 18: Comprehensive Agent Logging**
    - **Validates: Requirements 5.9, 6.3, 6.7, 7.5, 7.8, 8.8, 9.7, 10.7, 13.7**
    - Test that all agent operations produce appropriate logs

- [x] 18. Demo Script Integration Test
  - [x] 18.1 Write integration test for full demo script
    - Create `backend/tests/test_demo_script.py`
    - Test greeting flow (no LLM, varied response)
    - Test symptom check flow (Knowledge + History + LLM agents)
    - Test mental health activation flow
    - Test history retrieval with context references
    - Test emergency risk classification
    - Test guided breathing exercise offer
    - Verify all terminal logs match demo script expectations
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_
  
  - [x]* 18.2 Write property test for varied greeting across sessions
    - **Property 20: Greeting Variation Across Sessions**
    - **Validates: Requirements 17.1, 17.2**
    - Test that consecutive sessions use different greetings
  
  - [x]* 18.3 Write property test for follow-up questions
    - **Property 27: Follow-Up Question Generation**
    - **Validates: Requirements 17.2**
    - Test that symptom queries generate follow-up questions

- [x] 19. Frontend React Application
  - [x] 19.1 Create React app with Vite
    - Initialize Vite React project in `frontend/`
    - Install dependencies (react, react-dom, vite)
    - Set up basic project structure
    - _Requirements: 20.4_
  
  - [x] 19.2 Implement UI layout and styling
    - Create "AI Health Companion" title component
    - Create conversation window with message bubbles
    - Implement warm colors and minimal design aesthetic
    - Add CSS for modern, clean look
    - _Requirements: 20.1, 20.2, 20.3_
  
  - [x] 19.3 Implement UI controls
    - Create mute button component
    - Implement mute/unmute toggle functionality
    - Create "Connect Backend" button
    - Implement backend connection logic
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5_
  
  - [x] 19.4 Implement AI thinking indicator
    - Create animated typing indicator component
    - Show indicator during processing
    - Hide indicator when AI speaks
    - _Requirements: 22.1, 22.2, 22.3_
  
  - [x] 19.5 Implement WebSocket connection to backend
    - Set up WebSocket client
    - Handle voice input streaming
    - Handle voice output playback
    - Handle message display in conversation window
    - _Requirements: 2.1, 3.2_

- [x] 20. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 21. Local Testing and Demo Script Validation
  - [ ] 21.1 Test backend locally
    - Start backend with `uvicorn backend.main:app --reload`
    - Verify health check endpoint works
    - Verify environment variables are loaded
    - Test each agent endpoint individually
    - _Requirements: 23.7, 24.2_
  
  - [ ] 21.2 Test frontend locally
    - Start frontend with `npm run dev`
    - Verify UI renders correctly
    - Test "Connect Backend" button
    - Test mute button functionality
    - _Requirements: 20.1, 20.2, 20.3, 21.1, 21.2, 21.3_
  
  - [ ] 21.3 Run full demo script end-to-end
    - Test greeting flow
    - Test symptom check with history
    - Test mental health support activation
    - Test emergency risk detection
    - Verify all terminal logs match demo script
    - Record any issues for fixing
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [ ] 22. Deploy Backend and Frontend with Public URLs
  - [ ] 22.1 Deploy Backend to Render
    - Create `render.yaml` configuration file
    - Set up environment variables in Render dashboard
    - Deploy FastAPI backend to Render
    - Test deployed backend health endpoint
    - Get public backend URL
    - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5, 23.6_
  
  - [ ] 22.2 Deploy Frontend to Vercel
    - Create basic React frontend (minimal for now)
    - Create `vercel.json` configuration
    - Set up environment variables in Vercel dashboard
    - Deploy frontend to Vercel
    - Configure backend API URL
    - Get public frontend URL
    - _Requirements: 20.4_
  
  - [ ] 22.3 Test Public URLs
    - Test backend public URL accessibility
    - Test frontend public URL accessibility
    - Verify CORS configuration works
    - Share public URLs for demo access
    - _Requirements: 1.7_

- [ ] 23. Deployment Preparation (Legacy - Use Task 22 instead)
  - [ ] 22.1 Create Vercel configuration for frontend
    - Create `vercel.json` in frontend directory
    - Configure build settings for React/Vite
    - Configure environment variables for API endpoint
    - _Requirements: 20.4_
  
  - [ ] 22.2 Create Vercel configuration for backend
    - Create `vercel.json` in backend directory
    - Configure Python runtime
    - Configure FastAPI serverless function
    - Set up environment variables in Vercel dashboard
    - _Requirements: 24.1, 24.2_
  
  - [ ] 22.3 Create deployment documentation
    - Create `docs/DEPLOYMENT.md`
    - Document Vercel deployment steps
    - Document environment variable configuration
    - Document how to add API keys in Vercel dashboard
    - Include troubleshooting section
    - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5, 23.6_

- [ ] 23. Deploy to Vercel
  - [ ] 23.1 Deploy backend to Vercel
    - Install Vercel CLI: `npm install -g vercel`
    - Run `vercel` in backend directory
    - Configure environment variables in Vercel dashboard:
      - AWS_ACCESS_KEY_ID
      - AWS_SECRET_ACCESS_KEY
      - AWS_REGION
      - OPENAI_API_KEY
      - OPENAI_BASE_URL
    - Verify deployment URL works
    - Test health check endpoint
    - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5, 23.6, 24.2_
  
  - [ ] 23.2 Deploy frontend to Vercel
    - Run `vercel` in frontend directory
    - Configure backend API URL environment variable
    - Verify deployment URL works
    - Test UI loads correctly
    - _Requirements: 20.4_
  
  - [ ] 23.3 Test live deployment end-to-end
    - Open frontend deployment URL
    - Click "Connect Backend"
    - Run through demo script
    - Verify voice input/output works
    - Verify all features work as expected
    - _Requirements: 1.7_
  
  - [ ] 23.4 Create shareable demo link
    - Document the live frontend URL
    - Create a README with demo instructions
    - Test the link in incognito mode
    - Ensure judges can access without authentication
    - _Requirements: 1.7_

- [ ] 24. Final Demo Recording
  - [ ] 24.1 Record demo video
    - Open live deployment URL
    - Follow demo script exactly
    - Record screen and audio
    - Ensure all terminal logs are visible
    - Capture all demo script interactions
    - _Requirements: 1.7_
  
  - [ ] 24.2 Create demo documentation
    - Create `docs/DEMO.md`
    - Include live URL
    - Include demo script
    - Include expected terminal outputs
    - Include screenshots
    - _Requirements: 1.7_

- [ ] 25. Final Checkpoint - Deployment Verification
  - Verify live URL is accessible
  - Verify API keys are working
  - Verify demo script executes successfully
  - Verify judges can test without issues
  - Ask the user if any final adjustments are needed

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Demo script reliability is the top priority
- Deployment to Vercel with working API keys is critical for judge testing
- All async operations use asyncio for non-blocking execution
- Direct streaming eliminates file I/O for 6x faster voice processing
- Fast path optimization targets 85% LLM usage reduction
