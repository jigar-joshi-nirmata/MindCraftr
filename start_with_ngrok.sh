#!/bin/bash

# MindCraftr - Start Backend with ngrok

echo "🚀 Starting MindCraftr Backend with ngrok Tunnel"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed!"
    echo ""
    echo "Install ngrok:"
    echo "  1. Visit: https://ngrok.com/download"
    echo "  2. Or use homebrew: brew install ngrok/ngrok/ngrok"
    echo ""
    exit 1
fi

# Start the Flask server in the background
echo "📡 Starting Flask server on port 5001..."
./start_server.sh > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if server started successfully
if ! curl -s http://localhost:5001/ > /dev/null; then
    echo "❌ Failed to start Flask server"
    echo "Check server.log for details"
    exit 1
fi

echo "✅ Flask server running (PID: $SERVER_PID)"
echo ""

# Start ngrok
echo "🌐 Starting ngrok tunnel..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  IMPORTANT: Copy the ngrok HTTPS URL below"
echo ""
echo "Then update frontend/services/api.ts:"
echo "  const API_BASE_URL = 'https://YOUR-NGROK-URL.ngrok-free.app/api/v1';"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start ngrok (this will run in foreground)
ngrok http 5001

# When ngrok is stopped, kill the server
echo ""
echo "🛑 Stopping Flask server..."
kill $SERVER_PID
echo "✅ Cleanup complete"

