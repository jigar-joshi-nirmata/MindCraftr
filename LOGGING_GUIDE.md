# MindCraftr Backend Logging Guide

## Overview

The backend now includes comprehensive logging to help you debug and monitor API requests and responses.

## What's Being Logged

### 🔹 Request Information (Before Each Request)
- HTTP Method and Path (e.g., `GET /api/v1/dashboard/stats`)
- Origin header (to verify CORS)
- User-Agent
- Query parameters (if any)

### 🔹 Database Operations (During Each Endpoint)
- User ID being queried
- Number of records found
- Specific data being retrieved

### 🔹 Response Information (After Each Request)
- HTTP Status Code
- CORS headers being sent
- Data being returned

### 🔹 Error Information
- Stack traces for unexpected errors
- 404 errors for missing resources
- Warning messages for empty data

## Log Format

Each log entry includes:
```
2025-11-14 10:30:45 - __main__ - INFO - Message
```

- **Timestamp**: When the event occurred
- **Module**: Which Python module (usually `__main__`)
- **Level**: INFO, WARNING, ERROR, DEBUG
- **Message**: The actual log message

## Example Log Output

When the frontend calls `/api/v1/dashboard/stats`, you'll see:

```
================================================================================
📥 Incoming Request: GET /api/v1/dashboard/stats
   Origin: http://localhost:3000
   User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...
🔍 Fetching dashboard stats for user_id: 1
   DB Result: tests_taken=3, avg_score=84.0, high_score=95, questions=50
   ✅ Returning stats: {'testsTaken': 3, 'averageScore': 84, 'highestScore': 95, 'questionsAnswered': 50}
📤 Response Status: 200
   CORS Headers: Access-Control-Allow-Origin = *
================================================================================
```

## Emojis for Quick Scanning

- 📥 Incoming request
- 📤 Outgoing response
- 🔍 Database query starting
- ✅ Success
- ⚠️  Warning
- ❌ Error
- 🏠 Health check
- 🚀 Server starting
- 📍 Server address
- 🔓 CORS status

## How to Use Logs for Debugging

### 1. **Check if Requests Are Reaching the Server**
Look for the `📥 Incoming Request` lines. If you don't see them, the frontend isn't connecting to the backend.

### 2. **Verify CORS Headers**
Check for `Access-Control-Allow-Origin = *` in the response. If it says "NOT SET", CORS isn't working.

### 3. **Check Database Queries**
Look at the `DB Result` lines to see what data is being retrieved. If it shows 0 records, the database might be empty.

### 4. **Identify Errors**
Search for `❌` or `⚠️` symbols to quickly find problems.

### 5. **Monitor Performance**
Compare request and response timestamps to see how long each endpoint takes.

## Disabling/Reducing Logs

If logs are too verbose, you can change the logging level in `server.py`:

```python
# Change this line:
logging.basicConfig(level=logging.DEBUG, ...)

# To:
logging.basicConfig(level=logging.INFO, ...)  # Less verbose
# or
logging.basicConfig(level=logging.WARNING, ...)  # Only warnings and errors
```

## Common Log Patterns

### ✅ Successful Request
```
📥 Incoming Request: GET /api/v1/flashcards
🔍 Fetching flashcards for user_id: 1
   DB Result: Found 3 flashcards
   ✅ Returning 3 flashcards
📤 Response Status: 200
```

### ⚠️ Warning (No Data Found)
```
📥 Incoming Request: GET /api/v1/dashboard/stats
🔍 Fetching dashboard stats for user_id: 1
   ⚠️  No test results found, returning N/A values
📤 Response Status: 200
```

### ❌ Error (404 Not Found)
```
📥 Incoming Request: GET /api/v1/topics/999/details
🔍 Fetching topic details for topic_id: 999, user_id: 1
   ⚠️  Topic 999 not found
📤 Response Status: 404
```

### ❌ Unexpected Error
```
📥 Incoming Request: GET /api/v1/some-endpoint
❌ Unexpected error: [Error details with full stack trace]
📤 Response Status: 500
```

## Tips

1. **Keep Terminal Visible**: When testing, keep the server terminal visible to see real-time logs
2. **Use Search**: In your terminal, use Cmd+F (Mac) or Ctrl+F (Windows/Linux) to search for specific terms
3. **Check Timestamps**: Verify requests are current and not old cached logs
4. **Clear Screen**: Run `clear` in the terminal before testing to start fresh

## Server Startup Logs

When you start the server with `python3 server.py`, you should see:

```
🚀 Starting MindCraftr API server...
📍 Server will run on http://localhost:5000
🔓 CORS is enabled for all origins
 * Serving Flask app 'server'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

If you don't see these startup logs, there might be an import error or Python version issue.

