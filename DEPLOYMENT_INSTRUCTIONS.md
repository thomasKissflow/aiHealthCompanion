# Deployment Instructions

## Overview
- Backend: Deploy to Render (FastAPI)
- Frontend: Deploy to Vercel (React)
- Goal: Get public URLs for demo access

---

## Part 1: Deploy Backend to Render

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub account
3. Verify email

### Step 2: Prepare Backend for Deployment

Create `render.yaml` in project root:
```yaml
services:
  - type: web
    name: ai-health-companion-backend
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: AWS_ACCESS_KEY_ID
        sync: false
      - key: AWS_SECRET_ACCESS_KEY
        sync: false
      - key: AWS_REGION
        value: us-east-1
      - key: OPENAI_API_KEY
        sync: false
      - key: OPENAI_BASE_URL
        value: https://bedrock-runtime.us-east-1.amazonaws.com/v1
      - key: ENVIRONMENT
        value: production
      - key: LOG_LEVEL
        value: INFO
```

### Step 3: Deploy to Render
1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository
5. Configure:
   - Name: `ai-health-companion-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables:
   - `AWS_ACCESS_KEY_ID` = (your AWS key)
   - `AWS_SECRET_ACCESS_KEY` = (your AWS secret)
   - `AWS_REGION` = us-east-1
   - `OPENAI_API_KEY` = (your Bedrock key)
   - `OPENAI_BASE_URL` = https://bedrock-runtime.us-east-1.amazonaws.com/v1
7. Click "Create Web Service"
8. Wait for deployment (5-10 minutes)

### Step 4: Get Backend URL
- After deployment, you'll get a URL like: `https://ai-health-companion-backend.onrender.com`
- Test it: `https://your-backend-url.onrender.com/health`

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub account
3. Verify email

### Step 2: Create Basic Frontend

Create `frontend/package.json`:
```json
{
  "name": "ai-health-companion-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }
}
```

Create `frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Health Companion</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

Create `frontend/src/main.jsx`:
```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

Create `frontend/src/App.jsx`:
```jsx
import React, { useState, useEffect } from 'react'

function App() {
  const [health, setHealth] = useState(null)
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

  useEffect(() => {
    fetch(`${backendUrl}/health`)
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(err => console.error(err))
  }, [])

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>AI Health Companion</h1>
      <p>Voice-first conversational AI for health guidance</p>
      {health && (
        <div>
          <h2>Backend Status</h2>
          <pre>{JSON.stringify(health, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}

export default App
```

Create `frontend/vite.config.js`:
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

Create `vercel.json` in project root:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "frontend/dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### Step 4: Deploy to Vercel
1. Go to Vercel Dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - Framework Preset: `Vite`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Add Environment Variable:
   - `VITE_BACKEND_URL` = (your Render backend URL)
6. Click "Deploy"
7. Wait for deployment (2-3 minutes)

### Step 5: Get Frontend URL
- After deployment, you'll get a URL like: `https://ai-health-companion.vercel.app`
- Test it in browser

---

## Part 3: Test Public URLs

### Test Backend
```bash
curl https://your-backend-url.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Health Companion",
  "environment": "production"
}
```

### Test Frontend
1. Open `https://your-frontend-url.vercel.app` in browser
2. Should see "AI Health Companion" page
3. Should see backend health status

---

## Troubleshooting

### Backend Issues
- Check Render logs for errors
- Verify environment variables are set
- Check AWS credentials are correct
- Ensure port is set to `$PORT` (Render provides this)

### Frontend Issues
- Check Vercel logs for build errors
- Verify `VITE_BACKEND_URL` is set correctly
- Check CORS is enabled in backend
- Test backend URL directly first

### CORS Issues
If frontend can't connect to backend, update `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Final Checklist

- [ ] Backend deployed to Render
- [ ] Backend health endpoint working
- [ ] Frontend deployed to Vercel
- [ ] Frontend loads in browser
- [ ] Frontend can connect to backend
- [ ] Public URLs documented
- [ ] URLs shared for demo access

---

## Public URLs Template

After deployment, document your URLs:

```
Backend URL: https://ai-health-companion-backend.onrender.com
Frontend URL: https://ai-health-companion.vercel.app

Health Check: https://ai-health-companion-backend.onrender.com/health
API Docs: https://ai-health-companion-backend.onrender.com/docs
```

Share these URLs for demo access!
