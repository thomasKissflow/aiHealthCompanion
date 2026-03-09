# Quick Start Guide - Frontend

## Prerequisites

1. Backend server must be running on `http://localhost:8000`
2. Node.js 16+ installed

## Start the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at: `http://localhost:5173`

## Testing the Application

1. Open your browser to `http://localhost:5173`
2. Click the **"Connect Backend"** button
3. Once connected, try the example queries:
   - **"Hello"** - Fast path greeting
   - **"I have a headache and nausea"** - Symptom check with knowledge retrieval
   - **"I'm feeling really stressed with work"** - Mental health support
   - **"I have chest pain and trouble breathing"** - Risk escalation

## What You'll See

### UI Elements

- **Header**: "AI Health Companion" title with warm orange gradient
- **Conversation Window**: Scrollable message area with:
  - User messages (right-aligned, orange gradient)
  - AI messages (left-aligned, white background)
  - System messages (centered, light background)
  - Typing indicator (animated dots when AI is thinking)
- **Example Queries**: Quick test buttons (appears after connection)
- **Controls**: 
  - Connect Backend button (green when connected)
  - Mute button (toggles voice input)

### Message Metadata

Each AI response shows badges indicating:
- **Intent**: The classified intent type
- **Fast Path**: Response used template (no LLM)
- **Cached**: Response served from cache
- **LLM**: Response required LLM call

### Color Scheme

- Warm oranges and peaches
- Clean white backgrounds
- Smooth gradients and shadows
- Minimal, modern design

## Troubleshooting

### "Failed to connect to backend"

- Ensure backend is running: `cd backend && python main.py`
- Check backend is on port 8000: `curl http://localhost:8000/health`

### Port 5173 already in use

- Stop other Vite dev servers
- Or change port: `npm run dev -- --port 3000`

### Blank screen

- Check browser console for errors (F12)
- Ensure all dependencies installed: `npm install`
- Try clearing cache: `npm run dev -- --force`

## Development Tips

### Hot Module Replacement (HMR)

Vite provides instant updates when you edit files:
- Edit `src/App.jsx` - UI updates immediately
- Edit `src/App.css` - Styles update immediately
- No page refresh needed!

### Browser DevTools

Open DevTools (F12) to see:
- Network requests to backend
- Console logs for debugging
- React component tree (with React DevTools extension)

### Code Structure

```
frontend/
├── src/
│   ├── App.jsx       # Main component
│   ├── App.css       # Component styles
│   ├── main.jsx      # Entry point
│   └── index.css     # Global styles
├── public/           # Static assets
├── index.html        # HTML template
└── package.json      # Dependencies
```

## Next Steps

1. **Test all example queries** to see different response types
2. **Check the metadata badges** to understand the optimization
3. **Monitor the console** to see backend logs
4. **Try the mute button** to test voice control (UI only for now)

## Production Build

To build for production:

```bash
npm run build
```

Output will be in `dist/` directory. Serve with:

```bash
npm run preview
```

Or deploy to any static hosting service (Vercel, Netlify, etc.)
