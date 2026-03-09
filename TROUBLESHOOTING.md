# Troubleshooting Guide - AI Health Companion

## Issues Fixed

### 1. LLM Error: 'NoneType' object is not subscriptable ✅

**Problem:** Bedrock returns 200 OK but response parsing fails

**Fix Applied:**
- Added better error handling in `backend/llm_client.py`
- Now checks if response, choices, message, and content exist before accessing
- Provides detailed error messages for debugging

**What to check:**
```bash
# Check your .env file has correct values
cat backend/.env | grep OPENAI

# Should show:
# OPENAI_API_KEY=your-key
# OPENAI_BASE_URL=https://bedrock-runtime.us-east-1.amazonaws.com/v1
```

### 2. Knowledge Agent Collection Not Initialized ✅

**Problem:** `WARNING:knowledge_agent:[Knowledge Agent] Collection not initialized`

**Fix Applied:**
- Added `await knowledge_agent.initialize()` in `backend/main.py` startup
- Now loads PDFs from `backend/knowledge/` directory on startup

**What to check:**
```bash
# Verify PDF files exist
ls -la backend/knowledge/

# Should show:
# common_symptoms_guide.pdf
# migraines_and_headaches.pdf
```

### 3. No Voice Input/Output (Expected)

**Status:** Voice interface exists but not integrated into main.py yet

**Current State:**
- Voice interface module created (`backend/voice_interface.py`)
- Not connected to main API endpoint
- Frontend uses text-based queries for now

**For Demo:**
- Use the example query buttons in the UI
- Text-based interaction works perfectly
- Voice can be added post-demo if needed

---

## Restart Instructions

After fixes, restart the backend:

```bash
# Stop backend (Ctrl+C in backend terminal)

# Restart backend
cd backend
source venv/bin/activate
python main.py
```

**Expected startup logs:**
```
INFO:__main__:Initializing AI Health Companion backend...
INFO:intent_classifier:Intent Classifier initialized
INFO:response_cache:Response Cache initialized (max_size=1000, ttl=24h)
INFO:metrics_tracker:Metrics Tracker initialized (log_interval=10)
INFO:template_engine:Template Response Engine initialized with 3 greeting templates
INFO:llm_client:LLM Client initialized with model: openai.gpt-oss-120b, timeout: 3s
INFO:risk_escalation_agent:Risk Escalation Agent initialized
INFO:mental_health_agent:Mental Health Support Agent initialized
INFO:knowledge_agent:[Knowledge Agent] Initialized
INFO:knowledge_agent:[Knowledge Agent] Starting knowledge base initialization...
INFO:knowledge_agent:[Knowledge Agent] Collection 'medical_knowledge' ready
INFO:knowledge_agent:[Knowledge Agent] Found 2 PDF files to process
INFO:knowledge_agent:[Knowledge Agent] Processing common_symptoms_guide.pdf...
INFO:knowledge_agent:[Knowledge Agent] Processing migraines_and_headaches.pdf...
INFO:knowledge_agent:[Knowledge Agent] Generating embeddings for X chunks...
INFO:knowledge_agent:[Knowledge Agent] Successfully loaded X chunks into knowledge base
INFO:database:Database initialized at data/user_history.db
INFO:user_history_agent:User History Agent initialized
INFO:supervisor_agent:Supervisor Agent initialized
INFO:__main__:✓ All components initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Testing After Fixes

### Test 1: Greeting (Should work - Fast Path)
```
Query: "Hello"
Expected: Fast response with greeting
Logs: [LLM Agent] skipping model call
```

### Test 2: Symptom Check (Should work now)
```
Query: "I have a headache and nausea"
Expected: Response with medical context
Logs: 
  [Knowledge Agent] retrieving medical context
  [Knowledge Agent] Retrieved 3 chunks
  [LLM Agent] invoking bedrock
  [LLM Agent] response received (X chars)
```

### Test 3: Mental Health (Should work now)
```
Query: "I'm feeling really stressed with work"
Expected: Empathetic response
Logs:
  [Mental Health Agent] activated
  [LLM Agent] invoking bedrock
  [LLM Agent] response received (X chars)
```

### Test 4: Emergency Risk (Should work - Fast Path)
```
Query: "I have chest pain and trouble breathing"
Expected: Emergency guidance
Logs: 
  [Risk Agent] urgency level: EMERGENCY
  [LLM Agent] skipping model call
```

---

## Common Issues

### Issue: LLM still returning None

**Check 1: Bedrock Model Name**
```bash
# In .env, verify model name matches what's available in your region
# Common models:
# - anthropic.claude-3-sonnet-20240229-v1:0
# - anthropic.claude-v2
# - meta.llama2-70b-chat-v1
```

**Check 2: AWS Credentials**
```bash
# Test AWS credentials
aws sts get-caller-identity

# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

**Check 3: OpenAI Base URL**
```bash
# Should be:
OPENAI_BASE_URL=https://bedrock-runtime.us-east-1.amazonaws.com/v1

# NOT:
# OPENAI_BASE_URL=https://api.openai.com/v1  (This is OpenAI, not Bedrock)
```

### Issue: Knowledge Agent not finding PDFs

**Solution:**
```bash
# Create knowledge directory if missing
mkdir -p backend/knowledge

# Add sample PDFs (you can create simple text PDFs for testing)
# Or use the existing ones from the repo
```

### Issue: Database errors

**Solution:**
```bash
# Create data directory
mkdir -p backend/data

# Remove old database if corrupted
rm backend/data/user_history.db

# Restart backend (will recreate database)
```

---

## Debug Mode

To see more detailed logs, set log level to DEBUG:

```python
# In backend/main.py, change:
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

---

## Next Steps

1. ✅ Restart backend with fixes
2. ✅ Test all 4 example queries
3. ✅ Verify logs show correct behavior
4. ✅ Check that LLM responses are generated
5. ✅ Verify knowledge retrieval works
6. ✅ Ready for demo video recording!

---

## Still Having Issues?

Copy and paste your terminal output showing:
1. Backend startup logs
2. Query processing logs
3. Any error messages

This will help diagnose remaining issues.
