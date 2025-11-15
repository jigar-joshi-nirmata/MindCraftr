#!/bin/bash

# Test the Generate Test API endpoint

BASE_URL="http://localhost:5001"

echo "🧪 Testing Test Generation API Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Custom Exam with Syllabus
echo "1️⃣  Test: Custom Exam (Objective, with Syllabus)"
echo "────────────────────────────────────────────────────────────────────"
curl -X POST $BASE_URL/api/v1/tests/generate \
  -H "Content-Type: application/json" \
  -d '{
    "examType": "custom",
    "examName": "React Advanced Concepts",
    "numQuestions": 20,
    "questionFormat": "objective",
    "syllabusContent": "React Hooks, Context API, useEffect, useState, Custom Hooks, Performance Optimization, Memoization, useMemo, useCallback",
    "difficulty": "hard"
  }' | python3 -m json.tool
echo ""
echo ""

# Test 2: Custom Exam without Syllabus
echo "2️⃣  Test: Custom Exam (Subjective, no Syllabus)"
echo "────────────────────────────────────────────────────────────────────"
curl -X POST $BASE_URL/api/v1/tests/generate \
  -H "Content-Type: application/json" \
  -d '{
    "examType": "custom",
    "examName": "Python Fundamentals",
    "numQuestions": 15,
    "questionFormat": "subjective",
    "difficulty": "easy"
  }' | python3 -m json.tool
echo ""
echo ""

# Test 3: Preset Exam - GRE
echo "3️⃣  Test: Preset Exam (GRE - Quick)"
echo "────────────────────────────────────────────────────────────────────"
curl -X POST $BASE_URL/api/v1/tests/generate \
  -H "Content-Type: application/json" \
  -d '{
    "examType": "GRE",
    "difficulty": "standard",
    "presetDuration": "quick"
  }' | python3 -m json.tool
echo ""
echo ""

# Test 4: Preset Exam - SAT
echo "4️⃣  Test: Preset Exam (SAT - Endurance)"
echo "────────────────────────────────────────────────────────────────────"
curl -X POST $BASE_URL/api/v1/tests/generate \
  -H "Content-Type: application/json" \
  -d '{
    "examType": "SAT",
    "difficulty": "hard",
    "presetDuration": "endurance"
  }' | python3 -m json.tool
echo ""
echo ""

# Test 5: Custom with long syllabus
echo "5️⃣  Test: Custom Exam (with Long Syllabus Content)"
echo "────────────────────────────────────────────────────────────────────"
curl -X POST $BASE_URL/api/v1/tests/generate \
  -H "Content-Type: application/json" \
  -d '{
    "examType": "custom",
    "examName": "Full Stack Development",
    "numQuestions": 50,
    "questionFormat": "objective",
    "syllabusContent": "HTML5, CSS3, JavaScript ES6+, React.js, Node.js, Express.js, MongoDB, PostgreSQL, REST APIs, GraphQL, Authentication, JWT, OAuth, Deployment, Docker, Kubernetes, CI/CD, Git, Testing with Jest, React Testing Library, Integration Tests, Unit Tests, E2E Testing, Performance Optimization, Security Best Practices, CORS, XSS Prevention, SQL Injection Prevention, Environment Variables, Error Handling, Logging, Monitoring",
    "difficulty": "standard"
  }' | python3 -m json.tool
echo ""
echo ""

# Test 6: Error case - No payload
echo "6️⃣  Test: Error Handling (Empty Payload)"
echo "────────────────────────────────────────────────────────────────────"
curl -X POST $BASE_URL/api/v1/tests/generate \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
echo ""
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All test generation endpoint tests completed!"
echo ""
echo "💡 Tip: Check the server terminal to see detailed logging of each request"

