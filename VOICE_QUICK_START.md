# Voice Quick Start - Get Voice Working NOW

## 🎯 Goal
Get voice output (Polly) working so your AI speaks to you!

---

## ⚡ 3-Step Quick Start

### Step 1: Install Audio Dependencies (30 seconds)

```bash
cd backend
source venv/bin/activate
pip install sounddevice numpy
```

### Step 2: Restart Backend (10 seconds)

```bash
# Stop current backend (Ctrl+C)
python main.py
```

**Look for this line:**
```
INFO:voice_interface:Voice Interface initialized
```

### Step 3: Test Voice (10 seconds)

```bash
# In a new terminal
curl -X POST http://localhost:8000/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, I am your AI Health Companion. How are you feeling today?"}'
```

**YOU SHOULD HEAR THE VOICE!** 🔊

---

## ✅ If You Hear the Voice

**Congratulations!** Voice is working. Now update your frontend to call this endpoint after each AI response.

### Frontend Change Needed:

In `frontend/src/App.jsx`, after getting response, add:

```javascript
// After receiving AI response
const data = await response.json()

// Add this: Synthesize and play voice
if (data.response) {
  try {
    await fetch(`${backendUrl}/api/voice/synthesize`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text: data.response})
    })
  } catch (error) {
    console.log('Voice synthesis failed:', error)
  }
}
```

---

## ❌ If You Don't Hear Voice

### Check 1: System Audio
```bash
# macOS
say "test"

# Linux
espeak "test"
```

If you don't hear anything, check your system audio settings.

### Check 2: Audio Devices
```python
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

Should list your audio devices. If error, sounddevice isn't installed correctly.

### Check 3: AWS Polly Access
```bash
aws polly synthesize-speech \
  --text "test" \
  --output-format mp3 \
  --voice-id Joanna \
  --region us-east-1 \
  test.mp3

# Then play the file
open test.mp3  # macOS
xdg-open test.mp3  # Linux
```

If this works, Polly access is fine.

---

## 🎤 Voice Input (Transcribe) - Optional

For voice input, easiest approach is Web Speech API in frontend:

```javascript
// Add to frontend
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)()
recognition.continuous = true
recognition.interimResults = false

recognition.onresult = (event) => {
  const transcript = event.results[event.results.length-1][0].transcript
  console.log('User said:', transcript)
  // Send to backend via /api/query
  sendQuery(transcript)
}

recognition.start()
```

This uses browser's built-in speech recognition (works in Chrome/Edge).

---

## 🎬 Demo with Voice

### Test Flow:

1. Open frontend: http://localhost:5173
2. Click "Connect Backend"
3. Click "Hello"
4. **YOU SHOULD HEAR:** "Hi there, I'm glad you reached out..."
5. Click "I have a headache"
6. **YOU SHOULD HEAR:** Medical guidance in natural voice
7. While AI is speaking, test interruption:
   - Call: `curl -X POST http://localhost:8000/api/voice/stop`
   - Voice should stop immediately

---

## 📊 What You'll Demonstrate

✅ **Text Input** → User types or speaks  
✅ **AI Processing** → Fast path or LLM  
✅ **Voice Output** → Natural speech via Polly  
✅ **Interruption** → Stop AI mid-sentence  
✅ **Conversation** → Back-and-forth interaction  

---

## 🚀 Priority Actions

1. **NOW:** Install sounddevice/numpy
2. **NOW:** Restart backend
3. **NOW:** Test voice with curl command
4. **NEXT:** Update frontend to call /api/voice/synthesize
5. **OPTIONAL:** Add Web Speech API for voice input

---

## 💡 Pro Tips

- **Voice Quality:** Polly Neural voices sound more natural (already configured)
- **Interruption:** Essential for natural conversation - already implemented
- **Latency:** Direct streaming = 100-200ms (6x faster than file-based)
- **Demo:** Even text input + voice output is impressive!

---

## ✨ Success Criteria

- [ ] Installed sounddevice and numpy
- [ ] Backend shows "Voice Interface initialized"
- [ ] Curl command produces audible speech
- [ ] Frontend calls voice synthesis endpoint
- [ ] Can hear AI responses through speakers
- [ ] Can interrupt AI mid-speech
- [ ] Ready for demo video!

---

## 🆘 Still Stuck?

Copy and paste:
1. Output of: `pip list | grep sound`
2. Output of: `python3 -c "import sounddevice; print('OK')"`
3. Any error messages from the curl test

I'll help debug!
