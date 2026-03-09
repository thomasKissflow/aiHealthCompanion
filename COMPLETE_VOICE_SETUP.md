# Complete Voice Setup - Full Conversational AI

## 🎯 What You'll Get

✅ **Voice Input**: Speak and AI understands you (Web Speech API)  
✅ **Voice Output**: AI speaks back to you (Amazon Polly)  
✅ **Agent Routing**: Automatically routes to correct agent based on what you say  
✅ **User History**: Loads data from `user_history.csv`  
✅ **Medical Knowledge**: Loads data from `medical_knowledge.pdf`  
✅ **Interruption**: Stop AI mid-sentence when you speak  

---

## 🚀 Complete Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd backend
source venv/bin/activate
pip install sounddevice numpy
```

### Step 2: Load Initial Data

```bash
# This loads user_history.csv and medical_knowledge.pdf
python load_initial_data.py
```

**Expected output:**
```
INFO:__main__:=== Loading Initial Data ===
INFO:__main__:Loading user history from user_history.csv...
INFO:__main__:Loaded history for user 1 (Thomas)
INFO:__main__:Loaded history for user 2 (Tana)
INFO:__main__:✓ Loaded 2 user history records
INFO:__main__:Loading medical knowledge from medical_knowledge.pdf...
INFO:knowledge_agent:[Knowledge Agent] Processing medical_knowledge.pdf...
INFO:__main__:✓ Medical knowledge loaded successfully
INFO:__main__:=== Initial Data Loading Complete ===
```

### Step 3: Restart Backend

```bash
python main.py
```

**Look for:**
```
INFO:__main__:[Startup] Loading medical_knowledge.pdf from root directory
INFO:knowledge_agent:[Knowledge Agent] Successfully loaded X chunks into knowledge base
INFO:voice_interface:Voice Interface initialized
INFO:__main__:✓ All components initialized successfully
```

### Step 4: Restart Frontend

```bash
# In frontend terminal
cd frontend
npm run dev
```

### Step 5: Test Full Voice Conversation

1. Open http://localhost:5173
2. Click **"Connect Backend"**
3. You'll see: **"🎤 Listening... Speak now!"**
4. **SPEAK:** "Hello"
5. **AI RESPONDS:** You'll hear the greeting
6. **SPEAK:** "I have a headache"
7. **AI RESPONDS:** Medical guidance with voice
8. **SPEAK:** "I'm feeling stressed"
9. **AI RESPONDS:** Mental health support with voice

---

## 🎤 How Voice Works Now

### Voice Input (Your Speech → Text)

```
You speak into microphone
    ↓
Browser Web Speech API captures audio
    ↓
Converts to text automatically
    ↓
Sends text to backend /api/query
    ↓
Backend processes through agents
```

### Voice Output (AI Response → Speech)

```
Backend generates text response
    ↓
Frontend receives response
    ↓
Calls /api/voice/synthesize
    ↓
Amazon Polly converts to speech
    ↓
You hear the AI speaking
```

### Agent Routing (Automatic)

```
Your speech: "I have a headache"
    ↓
Intent Classifier: SYMPTOM_CHECK
    ↓
Routes to:
  - Knowledge Agent (medical_knowledge.pdf)
  - User History Agent (user_history.csv)
  - LLM Agent (Bedrock)
    ↓
Generates personalized response
    ↓
Speaks back to you
```

---

## 📊 What Data Is Used

### user_history.csv
```
User 1 (Thomas):
- Known conditions: Migraines, stress headaches
- Mental health: Anxiety during high workload
- History: Headaches during stressful work weeks

User 2 (Tana):
- Known conditions: Seasonal allergies
- Mental health: Academic pressure stress
- History: Sneezing and headaches during seasonal changes
```

**How it's used:**
- When you say "I have a headache", system checks your history
- Responds: "I see from your history you've experienced migraines before..."
- Personalizes advice based on your known conditions

### medical_knowledge.pdf
```
Contains medical reference information about:
- Common symptoms
- Conditions
- When to seek care
- General health guidance
```

**How it's used:**
- When you ask about symptoms, retrieves relevant medical info
- Provides evidence-based guidance
- Never diagnoses, just provides information

---

## 🎬 Demo Script with Full Voice

### Conversation 1: Greeting
```
YOU (speak): "Hello"
AI (speaks): "Hi there, I'm glad you reached out. How are you feeling today?"
```

### Conversation 2: Symptom Check with History
```
YOU (speak): "I have a headache and I'm feeling nauseous"
AI (speaks): "I understand you're experiencing a headache and nausea. 
             I see from your history that you've had migraines before, 
             especially during stressful periods. [medical guidance from PDF]"
```

### Conversation 3: Mental Health Support
```
YOU (speak): "I'm feeling really stressed with work"
AI (speaks): "I hear that you're feeling stressed with work. I know from 
             our previous conversations that you sometimes experience anxiety 
             during high workload periods. Would you like to try a breathing 
             exercise?"
```

### Conversation 4: Emergency Risk
```
YOU (speak): "I have chest pain and trouble breathing"
AI (speaks): "Chest pain combined with difficulty breathing can sometimes 
             indicate a serious medical issue. I cannot provide medical advice, 
             but those symptoms may require immediate medical attention..."
```

---

## 🔧 Troubleshooting

### Voice Input Not Working

**Check 1: Browser Support**
- Use Chrome or Edge (best support)
- Safari has limited support
- Firefox may not work

**Check 2: Microphone Permission**
- Browser will ask for microphone permission
- Click "Allow"
- Check browser settings if blocked

**Check 3: Console Errors**
- Press F12 to open console
- Look for speech recognition errors
- Copy and paste any errors

### Voice Output Not Working

**Check 1: System Audio**
```bash
# Test if audio works
say "test"  # macOS
```

**Check 2: Backend Logs**
- Look for: `[Voice API] Synthesizing: ...`
- Should see Polly API calls

**Check 3: sounddevice**
```bash
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

### Data Not Loading

**Check 1: Files Exist**
```bash
ls -la user_history.csv medical_knowledge.pdf
```

**Check 2: Run Data Loader**
```bash
cd backend
python load_initial_data.py
```

**Check 3: Database Created**
```bash
ls -la backend/data/user_history.db
```

---

## ✅ Success Checklist

- [ ] Installed sounddevice and numpy
- [ ] Ran load_initial_data.py successfully
- [ ] Backend shows "Voice Interface initialized"
- [ ] Backend shows "Successfully loaded X chunks"
- [ ] Frontend shows "🎤 Listening... Speak now!"
- [ ] Can speak and see transcription in UI
- [ ] AI responds with voice
- [ ] Agent routing works (check backend logs)
- [ ] User history is referenced in responses
- [ ] Medical knowledge is used in responses

---

## 🎯 Testing Each Component

### Test 1: Voice Input
```
Speak: "Hello"
Expected: See "Hello" appear as user message
Backend log: [Query] Classified intent: greeting
```

### Test 2: Voice Output
```
After AI responds, you should HEAR the voice
Backend log: [Voice API] Synthesizing: ...
```

### Test 3: Agent Routing
```
Speak: "I have a headache"
Backend log: 
  [Query] Classified intent: symptom_check
  [Knowledge Agent] retrieving medical context
  [History Agent] retrieving user history
  [LLM Agent] invoking bedrock
```

### Test 4: User History
```
Speak: "I have a headache"
AI should mention: "I see from your history..."
Backend log: [History Agent] retrieved previous context
```

### Test 5: Medical Knowledge
```
Speak: "What causes headaches?"
AI should provide medical information
Backend log: [Knowledge Agent] Retrieved 3 chunks
```

---

## 🚀 You're Ready!

Once all tests pass:

✅ Full voice conversation working  
✅ Agent routing automatic  
✅ User history personalization  
✅ Medical knowledge integration  
✅ Interruption handling  
✅ Ready for demo video!  

---

## 📹 Record Your Demo

Show:
1. **Voice Input**: Speak naturally
2. **Agent Routing**: Different intents route correctly
3. **Personalization**: AI references your history
4. **Medical Knowledge**: AI provides informed guidance
5. **Voice Output**: Natural speech responses
6. **Interruption**: Stop AI mid-sentence
7. **Metrics**: Show 80% LLM reduction

**Your conversational AI health companion is complete!** 🎉
