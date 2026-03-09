import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isThinking, setIsThinking] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [isListening, setIsListening] = useState(false)
  const [recognition, setRecognition] = useState(null)
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const [audioChunks, setAudioChunks] = useState([])
  const messagesEndRef = useRef(null)
  const backendUrl = 'http://localhost:8000'

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const connectBackend = async () => {
    try {
      // Test backend connection
      const response = await fetch(`${backendUrl}/health`)
      if (response.ok) {
        setIsConnected(true)
        setMessages(prev => [...prev, {
          role: 'system',
          content: 'Connected! Click the Speak button to use voice input.'
        }])
      } else {
        throw new Error('Backend not responding')
      }
    } catch (error) {
      console.error('Connection error:', error)
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Failed to connect to backend. Please ensure the backend is running on port 8000.'
      }])
    }
  }

  const sendQuery = async (queryText) => {
    if (!isConnected) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Please connect to backend first'
      }])
      return
    }

    // Add user message
    setMessages(prev => [...prev, {
      role: 'user',
      content: queryText
    }])

    // Show thinking indicator
    setIsThinking(true)

    try {
      const response = await fetch(`${backendUrl}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: queryText,
          session_id: sessionId,
          user_id: 'demo_user'
        })
      })

      if (!response.ok) {
        throw new Error('Query failed')
      }

      const data = await response.json()
      
      // Update session ID
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id)
      }

      // Hide thinking indicator
      setIsThinking(false)

      // Show immediate feedback if provided
      if (data.immediate_feedback) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.immediate_feedback,
          isImmediate: true
        }])
        // Brief delay before showing full response
        await new Promise(resolve => setTimeout(resolve, 500))
      }

      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        metadata: {
          intent: data.intent,
          usedFastPath: data.used_fast_path,
          cacheHit: data.cache_hit,
          usedLLM: data.used_llm
        }
      }])

      // Synthesize and play voice response
      if (data.response) {
        try {
          await fetch(`${backendUrl}/api/voice/synthesize`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              text: data.response
            })
          })
        } catch (voiceError) {
          console.error('Voice synthesis error:', voiceError)
          // Continue even if voice fails
        }
      }

    } catch (error) {
      console.error('Query error:', error)
      setIsThinking(false)
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Error processing query. Please try again.'
      }])
    }
  }

  const toggleMute = () => {
    const newMutedState = !isMuted
    setIsMuted(newMutedState)
    
    if (newMutedState) {
      // Mute - stop recognition
      if (recognition) {
        try {
          recognition.stop()
        } catch (e) {
          console.log('Recognition stop error:', e)
        }
        setIsListening(false)
      }
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Voice input muted'
      }])
    } else {
      // Unmute - start recognition
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Voice input active - Click the microphone button and speak!'
      }])
    }
  }

  const startListening = () => {
    if (!isConnected) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Please connect to backend first'
      }])
      return
    }

    if (isMuted) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Please unmute voice input first'
      }])
      return
    }

    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Voice recognition not supported. Please use Chrome or Edge.'
      }])
      return
    }

    const recognitionInstance = new SpeechRecognition()
    recognitionInstance.continuous = false
    recognitionInstance.interimResults = false
    recognitionInstance.lang = 'en-US'

    recognitionInstance.onstart = () => {
      console.log('🎤 Listening started')
      setIsListening(true)
    }

    recognitionInstance.onresult = async (event) => {
      const transcript = event.results[0][0].transcript
      console.log('Recognized:', transcript)
      setIsListening(false)
      
      // Process the recognized speech
      await sendQuery(transcript)
    }

    recognitionInstance.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setIsListening(false)
      
      if (event.error !== 'no-speech' && event.error !== 'aborted') {
        setMessages(prev => [...prev, {
          role: 'system',
          content: `Voice error: ${event.error}`
        }])
      }
    }

    recognitionInstance.onend = () => {
      console.log('🎤 Listening ended')
      setIsListening(false)
    }

    try {
      recognitionInstance.start()
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Listening... Speak now!'
      }])
    } catch (e) {
      console.error('Failed to start recognition:', e)
      setIsListening(false)
    }
  }

  // Example queries for demo
  const exampleQueries = [
    "Hello",
    "I have a headache and nausea",
    "I'm feeling really stressed with work",
    "I have chest pain and trouble breathing"
  ]

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Health Companion</h1>
      </header>

      <div className="conversation-window">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>Welcome to AI Health Companion</h2>
            <p>Connect to the backend to start your health conversation</p>
            <div className="glowing-orb-container">
              <div className="glowing-orb">
                <div className="orb-core"></div>
                <div className="orb-ring orb-ring-1"></div>
                <div className="orb-ring orb-ring-2"></div>
                <div className="orb-ring orb-ring-3"></div>
              </div>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.role}`}
          >
            <div className={`message-bubble ${message.isImmediate ? 'immediate' : ''}`}>
              {message.content}
              {message.metadata && (
                <div className="message-metadata">
                  <span className="metadata-badge">{message.metadata.intent}</span>
                  {message.metadata.usedFastPath && (
                    <span className="metadata-badge fast">Fast Path</span>
                  )}
                  {message.metadata.cacheHit && (
                    <span className="metadata-badge cache">Cached</span>
                  )}
                  {message.metadata.usedLLM && (
                    <span className="metadata-badge llm">LLM</span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isThinking && (
          <div className="message assistant">
            <div className="message-bubble thinking">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {isConnected && messages.length > 0 && (
        <div className="example-queries">
          <p>Try these example queries:</p>
          <div className="query-buttons">
            {exampleQueries.map((query, index) => (
              <button
                key={index}
                className="query-button"
                onClick={() => sendQuery(query)}
                disabled={isThinking}
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="controls">
        <button
          className={`control-button ${isConnected ? 'connected' : ''}`}
          onClick={connectBackend}
          disabled={isConnected}
        >
          {isConnected ? '✓ Connected' : 'Connect Backend'}
        </button>
        
        <button
          className={`control-button mic-button ${isListening ? 'listening' : ''}`}
          onClick={startListening}
          disabled={!isConnected || isMuted || isListening}
        >
          {isListening ? 'Listening...' : 'Speak'}
        </button>
        
        <button
          className={`control-button mute-button ${isMuted ? 'muted' : ''}`}
          onClick={toggleMute}
          disabled={!isConnected}
        >
          {isMuted ? 'Unmute Voice' : 'Voice Active'}
        </button>
      </div>
    </div>
  )
}

export default App
