# Frontend Integration Guide

## Overview

This guide explains how to run the complete AI Health Companion system with both backend and frontend.

## Prerequisites

1. **Backend Setup**
   - Python 3.8+ with virtual environment
   - AWS credentials configured
   - All backend dependencies installed
   - Backend running on port 8000

2. **Frontend Setup**
   - Node.js 16+ installed
   - npm package manager
   - Frontend dependencies installed

## Quick Start

### 1. Start the Backend

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the backend server
python main.py
```

Backend will be available at: `http://localhost:8000`

Verify backend is running:
```bash
curl http://localhost:8000/health
```

### 2. Start the Frontend

In a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Start the development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 3. Test the Application

1. Open browser to `http://localhost:5173`
2. Click **"Connect Backend"** button
3. Try the example queries:
   - "Hello" - Fast path greeting
   - "I have a headache and nausea" - Symptom check
   - "I'm feeling really stressed with work" - Mental health support
   - "I have chest pain and trouble breathing" - Risk escalation

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (localhost:5173)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              React Frontend (Vite)                      │ │
│  │  - UI Components                                        │ │
│  │  - Message Display                                      │ │
│  │  - Connection Management                                │ │
│  │  - Example Queries                                      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              │ (fetch requests)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Backend Server (localhost:8000)               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              FastAPI Backend                            │ │
│  │  - /api/query endpoint                                  │ │
│  │  - /health endpoint                                     │ │
│  │  - Intent Classification                                │ │
│  │  - Response Cache                                       │ │
│  │  - Supervisor Agent                                     │ │
│  │  - Specialized Agents                                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ AWS SDK (boto3)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      AWS Services                            │
│  - Amazon Bedrock (LLM)                                      │
│  - Amazon Transcribe (Speech-to-Text)                        │
│  - Amazon Polly (Text-to-Speech)                             │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

### Backend Endpoints

1. **POST /api/query**
   - Process user queries
   - Returns AI response with metadata
   - Request body:
     ```json
     {
       "query": "Hello",
       "session_id": "optional-session-id",
       "user_id": "demo_user"
     }
     ```
   - Response:
     ```json
     {
       "response": "Hi there, I'm glad you reached out...",
       "session_id": "uuid",
       "intent": "greeting",
       "used_fast_path": true,
       "cache_hit": false,
       "used_llm": false,
       "immediate_feedback": null
     }
     ```

2. **GET /health**
   - Health check endpoint
   - Returns backend status

3. **GET /api/metrics**
   - Get optimization metrics
   - Returns cache hit rate, LLM usage, etc.

4. **DELETE /api/session/{session_id}**
   - End a session
   - Clear session context

## Frontend Features

### UI Components

1. **Header**
   - Title: "AI Health Companion"
   - Warm orange gradient background

2. **Conversation Window**
   - Scrollable message area
   - Message bubbles (user, assistant, system)
   - Auto-scroll to latest message
   - Typing indicator during processing

3. **Example Queries**
   - Quick test buttons
   - Appears after connection
   - Four demo queries

4. **Controls**
   - Connect Backend button
   - Mute/Unmute button

### Message Types

- **User Messages**: Right-aligned, orange gradient
- **Assistant Messages**: Left-aligned, white background
- **System Messages**: Centered, light background
- **Thinking Indicator**: Animated dots

### Metadata Display

Each AI response shows:
- **Intent**: Classified intent type
- **Fast Path**: Template-based response
- **Cached**: Response from cache
- **LLM**: LLM invocation required

## Testing Scenarios

### 1. Fast Path (Greeting)

**Query**: "Hello"

**Expected Behavior**:
- Fast response (<500ms)
- Badge: "greeting", "Fast Path"
- No LLM call
- Template response with variation

**Backend Logs**:
```
[Query] Classified intent: greeting (confidence: 0.95)
[LLM Agent] skipping model call
```

### 2. Symptom Check (Knowledge Retrieval)

**Query**: "I have a headache and nausea"

**Expected Behavior**:
- Thinking indicator appears
- Immediate feedback: "Let me check that for you"
- Response includes medical context
- Badge: "symptom_check", "LLM"

**Backend Logs**:
```
[Query] Classified intent: symptom_check (confidence: 0.88)
[Immediate Feedback] Let me check that for you
[Knowledge Agent] retrieving medical context
[History Agent] retrieving user history
[LLM Agent] invoking bedrock
```

### 3. Mental Health Support

**Query**: "I'm feeling really stressed with work"

**Expected Behavior**:
- Empathetic response
- Offer of breathing exercises
- Badge: "mental_health", "LLM"

**Backend Logs**:
```
[Query] Classified intent: mental_health (confidence: 0.92)
[Mental Health Agent] activated
[LLM Agent] invoking bedrock
```

### 4. Risk Escalation

**Query**: "I have chest pain and trouble breathing"

**Expected Behavior**:
- Fast response with urgent guidance
- Template response about seeking care
- Badge: "risk_symptom", "Fast Path"

**Backend Logs**:
```
[Query] Classified intent: risk_symptom (confidence: 0.98)
[Risk Agent] urgency level: EMERGENCY
[LLM Agent] skipping model call
```

## Troubleshooting

### Backend Issues

**Problem**: Backend won't start
- Check Python version: `python --version`
- Verify virtual environment activated
- Check environment variables in `.env`
- Verify AWS credentials

**Problem**: LLM calls failing
- Check AWS credentials
- Verify Bedrock access
- Check `OPENAI_API_KEY` and `OPENAI_BASE_URL`

**Problem**: Port 8000 in use
- Stop other processes: `lsof -ti:8000 | xargs kill`
- Or change port in `main.py`

### Frontend Issues

**Problem**: Can't connect to backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in backend
- Check browser console for errors

**Problem**: Port 5173 in use
- Stop other Vite servers
- Or use different port: `npm run dev -- --port 3000`

**Problem**: Build fails
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear Vite cache: `npm run dev -- --force`

### Network Issues

**Problem**: CORS errors
- Backend CORS is configured for `*` in development
- For production, specify exact origins

**Problem**: Slow responses
- Check network tab in browser DevTools
- Verify backend logs for performance
- Check AWS service latency

## Performance Monitoring

### Frontend Metrics

Monitor in browser DevTools:
- Network tab: API call timing
- Console: Connection status
- Performance tab: Render performance

### Backend Metrics

Check backend logs for:
- Intent classification time
- Cache hit/miss rate
- LLM invocation count
- Response time per query

Access metrics endpoint:
```bash
curl http://localhost:8000/api/metrics
```

## Production Deployment

### Backend Deployment

1. **AWS EC2 / ECS**
   - Deploy FastAPI with uvicorn
   - Configure environment variables
   - Set up load balancer
   - Enable HTTPS

2. **Environment Variables**
   ```
   AWS_ACCESS_KEY_ID=xxx
   AWS_SECRET_ACCESS_KEY=xxx
   AWS_REGION=us-east-1
   OPENAI_API_KEY=xxx
   OPENAI_BASE_URL=xxx
   ENVIRONMENT=production
   ```

### Frontend Deployment

1. **Build for Production**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy to Vercel**
   ```bash
   npm install -g vercel
   vercel deploy
   ```

3. **Deploy to Netlify**
   - Drag `dist/` folder to Netlify
   - Or use CLI: `netlify deploy --prod`

4. **Configure Environment**
   - Set `VITE_API_URL` to production backend URL
   - Update CORS settings in backend

## Security Considerations

### Backend

- ✓ Environment variables for secrets
- ✓ CORS configured (restrict in production)
- ⚠ Add rate limiting
- ⚠ Add authentication
- ⚠ Add input validation

### Frontend

- ✓ No secrets in client code
- ✓ HTTPS in production
- ⚠ Add CSP headers
- ⚠ Add authentication
- ⚠ Sanitize user input

## Monitoring and Logging

### Backend Logging

Logs include:
- Intent classification
- Agent routing
- LLM invocations
- Cache hits/misses
- Error traces

### Frontend Logging

Console logs include:
- Connection status
- API requests
- Error messages
- State changes

## Next Steps

1. **Test all scenarios** with example queries
2. **Monitor performance** using metrics endpoint
3. **Review logs** for optimization opportunities
4. **Add WebSocket** for real-time voice streaming
5. **Implement authentication** for production
6. **Add analytics** for usage tracking
7. **Deploy to production** when ready

## Support

For issues or questions:
1. Check backend logs
2. Check browser console
3. Review this guide
4. Check individual README files
5. Review requirements and design documents

## Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can connect from frontend to backend
- [ ] All example queries work
- [ ] Metadata displays correctly
- [ ] Thinking indicator appears
- [ ] Messages display properly
- [ ] Mute button toggles
- [ ] No console errors
- [ ] Performance is acceptable

Once all items are checked, the system is ready for demo and testing!
