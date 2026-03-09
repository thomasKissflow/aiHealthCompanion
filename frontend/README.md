# AI Health Companion - Frontend

A beautiful, minimal React frontend for the AI Health Companion voice-first conversational AI system.

## Features

- **Modern UI**: Clean, minimal design with warm colors (soft oranges, peaches, warm grays)
- **Conversation Window**: Message bubbles for user and AI messages
- **AI Thinking Indicator**: Animated typing indicator during processing
- **Backend Connection**: Connect button to establish connection with backend
- **Mute Control**: Toggle voice input on/off
- **Real-time Updates**: WebSocket-ready for voice streaming
- **Example Queries**: Quick test buttons for demo purposes
- **Metadata Display**: Shows intent classification, fast path usage, cache hits, and LLM calls

## Design Aesthetic

- Warm color palette with gradients
- Smooth animations and transitions
- Responsive design for mobile and desktop
- Accessible and user-friendly interface
- Message bubbles with distinct styling for user/assistant/system messages

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend server running on `http://localhost:8000`

### Installation

Dependencies are already installed during Vite setup. If you need to reinstall:

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Usage

1. **Start the Backend**: Ensure the backend server is running on port 8000
2. **Open the Frontend**: Navigate to `http://localhost:5173`
3. **Connect**: Click the "Connect Backend" button
4. **Test Queries**: Use the example query buttons to test the system:
   - "Hello" - Tests greeting (fast path)
   - "I have a headache and nausea" - Tests symptom check with knowledge retrieval
   - "I'm feeling really stressed with work" - Tests mental health support
   - "I have chest pain and trouble breathing" - Tests risk escalation

## Architecture

### Components

- **App.jsx**: Main application component
  - Connection management
  - Message state management
  - Query processing
  - UI rendering

### State Management

- `messages`: Array of conversation messages
- `isConnected`: Backend connection status
- `isMuted`: Voice input mute status
- `isThinking`: AI processing indicator
- `sessionId`: Current session identifier

### API Integration

The frontend communicates with the backend via:

- **REST API**: `/api/query` endpoint for text queries
- **Health Check**: `/health` endpoint for connection testing
- **WebSocket** (future): For real-time voice streaming

### Message Types

- **user**: User input messages (right-aligned, warm gradient)
- **assistant**: AI responses (left-aligned, white background)
- **system**: System notifications (centered, light background)

### Metadata Display

Each AI response shows:
- **Intent**: Classified intent (greeting, symptom_check, etc.)
- **Fast Path**: Indicates template-based response
- **Cached**: Indicates response served from cache
- **LLM**: Indicates LLM was invoked

## Styling

### Color Palette

- Primary: `#ff9a76` to `#ff7f5c` (warm orange gradient)
- Background: `#fff5f0` to `#ffe8dc` (warm cream gradient)
- Text: `#333` (dark gray)
- Accent: `#ff7f5c` (warm orange)

### Typography

- Font: System font stack (San Francisco, Segoe UI, Roboto, etc.)
- Header: 1.8rem, weight 600
- Body: 1rem, line-height 1.5
- Small: 0.875rem

### Animations

- **fadeIn**: Message appearance (0.3s ease-in)
- **bounce**: Typing indicator dots (1.4s infinite)
- **hover**: Button lift effect (translateY -2px)

## Requirements Mapping

This frontend implements the following requirements:

- **Requirement 20.1**: "AI Health Companion" title display
- **Requirement 20.2**: Conversation window with message bubbles
- **Requirement 20.3**: Warm colors and minimal design
- **Requirement 20.4**: React + Vite implementation
- **Requirement 21.1**: Mute button
- **Requirement 21.2**: Mute toggle functionality
- **Requirement 21.3**: Stop/resume listening
- **Requirement 21.4**: Connect Backend button
- **Requirement 21.5**: Backend connection logic
- **Requirement 22.1**: Animated typing indicator
- **Requirement 22.2**: Show indicator during processing
- **Requirement 22.3**: Hide indicator when AI responds

## Future Enhancements

- WebSocket integration for real-time voice streaming
- WebRTC for browser-based audio capture
- Voice visualization (waveform/spectrum)
- Conversation history persistence
- User authentication
- Multi-language support
- Accessibility improvements (ARIA labels, keyboard navigation)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

Part of the AI Health Companion project.
