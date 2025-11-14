#!/bin/bash

# MindCraftr API Testing Script

BASE_URL="http://localhost:5001"

echo "🧪 Testing MindCraftr API Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test health check
echo "1️⃣  Health Check: GET /"
echo "────────────────────────────────────────────────────────────────────"
curl -s $BASE_URL/ | python3 -m json.tool
echo ""
echo ""

# Test dashboard stats
echo "2️⃣  Dashboard Stats: GET /api/v1/dashboard/stats"
echo "────────────────────────────────────────────────────────────────────"
curl -s $BASE_URL/api/v1/dashboard/stats | python3 -m json.tool
echo ""
echo ""

# Test recommendations
echo "3️⃣  Recommendations: GET /api/v1/dashboard/recommendations"
echo "────────────────────────────────────────────────────────────────────"
curl -s $BASE_URL/api/v1/dashboard/recommendations | python3 -m json.tool
echo ""
echo ""

# Test topic details
echo "4️⃣  Topic Details: GET /api/v1/topics/1/details"
echo "────────────────────────────────────────────────────────────────────"
curl -s $BASE_URL/api/v1/topics/1/details | python3 -m json.tool
echo ""
echo ""

# Test flashcards
echo "5️⃣  Flashcards: GET /api/v1/flashcards"
echo "────────────────────────────────────────────────────────────────────"
curl -s $BASE_URL/api/v1/flashcards | python3 -m json.tool
echo ""
echo ""

# Test profile stats
echo "6️⃣  Profile Stats: GET /api/v1/profile/stats"
echo "────────────────────────────────────────────────────────────────────"
curl -s $BASE_URL/api/v1/profile/stats | python3 -m json.tool
echo ""
echo ""

# Test profile mastery
echo "7️⃣  Profile Mastery: GET /api/v1/profile/mastery"
echo "────────────────────────────────────────────────────────────────────"
curl -s $BASE_URL/api/v1/profile/mastery | python3 -m json.tool | head -30
echo "... (truncated)"
echo ""
echo ""

# Test presets
echo "8️⃣  Presets: GET /api/v1/presets"
echo "────────────────────────────────────────────────────────────────────"
curl -s $BASE_URL/api/v1/presets | python3 -m json.tool
echo ""
echo ""

# Test 404
echo "9️⃣  Test 404: GET /api/v1/topics/999/details"
echo "────────────────────────────────────────────────────────────────────"
curl -s $BASE_URL/api/v1/topics/999/details | python3 -m json.tool
echo ""
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All endpoint tests completed!"
echo ""
echo "💡 Tip: Check the server terminal to see detailed logs for each request"

