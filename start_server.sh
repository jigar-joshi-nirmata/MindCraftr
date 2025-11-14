#!/bin/bash

# MindCraftr Backend Startup Script

echo "🚀 Starting MindCraftr Backend Server..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "📥 Checking dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies ready"
echo ""

# Check if database exists
if [ ! -f "mindcraftr.db" ]; then
    echo "🗄️  Database not found. Initializing..."
    python seed.py
    echo ""
fi

# Start the server
echo "🌐 Starting Flask server on http://localhost:5001"
echo "📊 Server logs will appear below..."
echo "⚠️  Press Ctrl+C to stop the server"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""

python server.py

