#!/bin/bash

# AI Health Companion - Backend Startup Script

echo "🚀 Starting AI Health Companion Backend..."
echo ""

# Check if venv exists
if [ ! -d "backend/venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it first: cd backend && python3 -m venv venv"
    exit 1
fi

# Activate venv and run
cd backend
source venv/bin/activate

echo "✓ Virtual environment activated"
echo "✓ Starting FastAPI server on http://0.0.0.0:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================"
echo ""

python main.py
