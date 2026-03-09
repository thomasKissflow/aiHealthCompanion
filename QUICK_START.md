# AI Health Companion - Quick Start Guide

## 🚀 Running the Full Stack Application

This guide will help you run both the backend and frontend for manual testing and demo video recording.

---

## Prerequisites

✅ Python 3.8+ with virtual environment  
✅ Node.js 16+ and npm  
✅ AWS credentials configured in `.env`  
✅ Backend dependencies installed  
✅ Frontend dependencies installed  

---

## Step 1: Start the Backend Server

Open a terminal and run:

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI server
python main.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify Backend is Running:**
```bash
# In a new terminal
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "AI Health Companion",
  "environment": "development",
  "components": {
    "intent_classifier": true,
    "response_cache": true,
    "supervisor_agent": true,
    "metrics_tracker": true
  }
}
```

---

## Step 2: Start the Frontend Development Server

Open a **NEW terminal** (keep backend running) and run:

```bash
# Navigate to frontend directory
cd frontend

# Start Vite development server
npm run dev
```

**Expected Output:**
```
  VITE v7.3.1  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## Step 3: Open the Application

1. Open your browser to: **http://localhost:5173**
2. You should see the AI Health Companion interface with:
   - Orange gradient header with "AI Health Companion" title
   - Welcome message
   - "Connect Backend" button at the bottom
   - "Mute" button (disabled until connected)

---

## Step 4: Test the Demo Script

### 4.1 Connect to Backend

1. Click the **"Connect Backend"** button
2. You should see:
   - Button changes to "✓ Connected" (green)
   - System message: "Connected to AI Health Companion"
   - System message: "Voice interface ready..."
   - Four example query buttons appear

### 4.2 Test Demo Scenarios

Click each example query button to test different flows:

#### **Test 1: Greeting (Fast Path)**
Click: **"Hello"**

**Expected:**
- Fast response (<500ms)
- Varied greeting like "Hi there, I'm glad you reached out. How are you feeling today?"
- Badges: `greeting` `Fast Path`
- **Backend logs should show:**
  ```
  [Query] Classified intent: greeting
  [LLM Agent] skipping model call
  ```

---

#### **Test 2: Symptom Check (Knowledge + LLM)**
Click: **"I have a headache and nausea"**

**Expected:**
- Thinking indicator appears (three bouncing dots)
- Immediate feedback: "Let me check that for you" (italic, light background)
- Then full response with medical context
- Badges: `symptom_check` `LLM`
- **Backend logs should show:**
  ```
  [Query] Classified intent: symptom_check
  [Immediate Feedback] Let me check that for you
  [Knowledge Agent] retrieving medical context
  [History Agent] retrieving user history
  [LLM Agent] invoking bedrock
  ```

---

#### **Test 3: Mental Health Support**
Click: **"I'm feeling really stressed with work"**

**Expected:**
- Thinking indicator appears
- Empathetic response offering support
- May offer breathing exercises
- Badges: `mental_health` `LLM`
- **Backend logs should show:**
  ```
  [Query] Classified intent: mental_health
  [Mental Health Agent] activated
  [LLM Agent] invoking bedrock
  ```

---

#### **Test 4: Emergency Risk Classification (Fast Path)**
Click: **"I have chest pain and trouble breathing"**

**Expected:**
- Fast response with urgent guidance
- Template response about seeking immediate medical attention
- Badges: `risk_symptom` `Fast Path`
- **Backend logs should show:**
  ```
  [Query] Classified intent: risk_symptom
  [Risk Agent] urgency level: EMERGENCY
  [LLM Agent] skipping model call
  ```

---

## Step 5: Monitor Backend Logs

Watch the backend terminal for detailed logs showing:
- Intent classification
- Agent routing decisions
- Cache hits/misses
- LLM invocations
- Response times

**Example log output:**
```
INFO:     127.0.0.1:52891 - "POST /api/query HTTP/1.1" 200 OK
[Query] Classified intent: greeting (confidence: 0.95)
[LLM Agent] skipping model call
[Metrics] Query #1 - Fast Path: 1, Cache Hits: 0, LLM Calls: 0
```

---

## Step 6: Check Optimization Metrics

Open a new terminal and run:

```bash
curl http://localhost:8000/api/metrics
```

**Expected output:**
```json
{
  "total_queries": 4,
  "fast_path_queries": 2,
  "cache_hits": 0,
  "cache_misses": 2,
  "llm_calls": 2,
  "cache_hit_rate": 0.0,
  "llm_reduction": 50.0
}
```

This shows:
- 50% of queries used fast path (no LLM)
- 50% required LLM
- Cache will improve with repeated queries

---

## Demo Video Script Testing

### Full Demo Flow

Test this sequence for your demo video:

1. **Open app** → Show clean UI
2. **Click "Connect Backend"** → Show connection
3. **Say/Click "Hello"** → Show fast greeting (no LLM)
4. **Say/Click "I have a headache and nausea"** → Show symptom check with thinking indicator
5. **Say/Click "I'm feeling stressed"** → Show mental health support
6. **Say/Click "I have chest pain"** → Show emergency risk detection
7. **Show backend logs** → Demonstrate optimization (fast path, LLM skip)
8. **Show metrics endpoint** → Demonstrate 85% LLM reduction target

### What to Highlight in Demo

✅ **Fast Path Optimization**: Greetings and risk symptoms bypass LLM  
✅ **Immediate Feedback**: "Let me check that for you" while processing  
✅ **Agent Routing**: Different intents route to specialized agents  
✅ **Beautiful UI**: Warm colors, smooth animations, clean design  
✅ **Metadata Display**: Shows optimization details (fast path, cache, LLM)  
✅ **Terminal Logs**: Comprehensive logging of all operations  

---

## Troubleshooting

### Backend Issues

**Problem: Backend won't start**
```bash
# Check Python version
python --version  # Should be 3.8+

# Verify virtual environment
which python  # Should point to venv/bin/python

# Check .env file exists
ls -la .env

# Check AWS credentials
cat .env | grep AWS
```

**Problem: Port 8000 already in use**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or change port in main.py
# Change: uvicorn.run(app, host="0.0.0.0", port=8000)
# To: uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Problem: LLM calls failing**
- Check `OPENAI_API_KEY` in `.env`
- Check `OPENAI_BASE_URL` in `.env`
- Verify AWS Bedrock access
- Check AWS credentials

---

### Frontend Issues

**Problem: Can't connect to backend**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check browser console for errors (F12)
# Look for CORS or network errors
```

**Problem: Port 5173 already in use**
```bash
# Kill existing Vite server
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 3000
```

**Problem: Example queries not working**
- Check browser console (F12) for errors
- Verify backend connection status
- Check network tab for failed requests

---

### Network Issues

**Problem: CORS errors in browser**
- Backend CORS is configured for `*` in development
- Should work automatically
- If issues persist, check backend logs

**Problem: Slow responses**
- Check backend logs for performance
- Verify AWS service latency
- Check network tab in browser DevTools

---

## Testing Checklist

Before recording your demo video, verify:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can connect from frontend to backend
- [ ] Greeting query works (fast path)
- [ ] Symptom check query works (LLM)
- [ ] Mental health query works
- [ ] Emergency risk query works
- [ ] Thinking indicator appears and disappears
- [ ] Metadata badges display correctly
- [ ] Backend logs show correct intent classification
- [ ] Backend logs show LLM skip for fast path
- [ ] Backend logs show LLM invocation for complex queries
- [ ] No console errors in browser
- [ ] Metrics endpoint returns data

---

## Next Steps

Once manual testing is complete:

1. ✅ **Record demo video** with working application
2. ✅ **Deploy to production** (Vercel/Render)
3. ✅ **Generate public URLs** for judges
4. ✅ **Create deployment documentation**

---

## Support

If you encounter issues:

1. Check backend terminal for error logs
2. Check browser console (F12) for frontend errors
3. Verify `.env` file has all required variables
4. Check this guide's troubleshooting section
5. Review `FRONTEND_INTEGRATION_GUIDE.md` for detailed info

---

## Success! 🎉

If you can complete all tests in the checklist, your application is ready for:
- Demo video recording
- Production deployment
- Judge testing

**Your AI Health Companion is working!**
