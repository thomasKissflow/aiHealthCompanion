# Action Checklist - Get Voice Working NOW

## ✅ Do These 5 Things (In Order)

### 1. Install Audio Dependencies (30 seconds)
```bash
cd backend
source venv/bin/activate
pip install sounddevice numpy
```

### 2. Load Your Data (1 minute)
```bash
# Still in backend directory
python load_initial_data.py
```

**Must see:**
```
✓ Loaded 2 user history records
✓ Medical knowledge loaded successfully
```

### 3. Restart Backend (10 seconds)
```bash
# Stop current backend (Ctrl+C)
python main.py
```

**Must see:**
```
INFO:voice_interface:Voice Interface initialized
INFO:__main__:✓ All components initialized successfully
```

### 4. Restart Frontend (10 seconds)
```bash
# In frontend terminal
# Stop current frontend (Ctrl+C)
cd frontend
npm run dev
```

### 5. Test Voice (2 minutes)

Open http://localhost:5173

1. Click **"Connect Backend"**
2. **Look for:** "🎤 Listening... Speak now!"
3. **SPEAK:** "Hello"
4. **EXPECT:** 
   - See "Hello" appear as your message
   - Hear AI respond with voice
5. **SPEAK:** "I have a headache"
6. **EXPECT:**
   - AI mentions your history
   - Provides medical guidance
   - You HEAR the response

---

## 🎯 What Should Happen

### When You Speak:
- ✅ Your speech appears as text in UI
- ✅ Backend processes through agents
- ✅ AI generates response
- ✅ You HEAR AI speaking back

### Backend Logs Should Show:
```
[Query] Classified intent: symptom_check
[Knowledge Agent] retrieving medical context
[Knowledge Agent] Retrieved 3 chunks
[History Agent] retrieving user history
[LLM Agent] invoking bedrock
[LLM Agent] response received (245 chars)
[Voice API] Synthesizing: ...
```

### Frontend Should Show:
```
System: 🎤 Listening... Speak now!
User: I have a headache
System: 💭 (thinking indicator)
Assistant: I understand you're experiencing a headache...
(+ you HEAR the voice)
```

---

## ❌ If Something Doesn't Work

### Voice Input Not Working?

**Browser Issue:**
- Use Chrome or Edge (not Firefox/Safari)
- Allow microphone permission when prompted
- Check browser console (F12) for errors

**Quick Test:**
```javascript
// Paste in browser console (F12)
const recognition = new webkitSpeechRecognition()
recognition.start()
// If error, browser doesn't support it
```

### Voice Output Not Working?

**Audio Issue:**
```bash
# Test system audio
say "test"  # macOS
espeak "test"  # Linux
```

**Backend Issue:**
```bash
# Test voice endpoint directly
curl -X POST http://localhost:8000/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing voice"}'
# You should HEAR this
```

### Data Not Loading?

**Check files exist:**
```bash
ls -la user_history.csv medical_knowledge.pdf
# Both should be in root directory
```

**Re-run data loader:**
```bash
cd backend
python load_initial_data.py
```

---

## 📋 Quick Verification

Copy this and check each item:

```
□ Installed sounddevice and numpy
□ Ran load_initial_data.py (saw success messages)
□ Backend restarted (saw Voice Interface initialized)
□ Frontend restarted (npm run dev)
□ Opened http://localhost:5173
□ Clicked "Connect Backend"
□ Saw "🎤 Listening... Speak now!"
□ Spoke "Hello" - saw it appear
□ Heard AI respond with voice
□ Spoke "I have a headache" - AI mentioned history
□ Heard AI respond with medical guidance
```

If all checked ✅ → **YOU'RE DONE! Record your demo!**

---

## 🆘 Still Stuck?

Copy and paste these outputs:

1. **Backend startup logs** (from "Initializing..." to "Uvicorn running")
2. **Frontend console** (F12 → Console tab)
3. **Backend logs when you speak** (what happens after you say something)
4. **Any error messages**

I'll help debug immediately!

---

## 🎬 Ready to Demo?

Your AI Health Companion now:
- ✅ Listens to your voice
- ✅ Understands what you say
- ✅ Routes to correct agents
- ✅ Uses your history (user_history.csv)
- ✅ Uses medical knowledge (medical_knowledge.pdf)
- ✅ Speaks back to you naturally
- ✅ Handles interruptions

**Record your demo and show it off!** 🚀
