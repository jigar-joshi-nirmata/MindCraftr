# MindCraftr Backend - Quick Reference Card

## 🚀 One-Line Commands

```bash
# Start the backend server
./start_server.sh

# Test all API endpoints
./test_api.sh

# Reset database
python seed.py
```

## 📡 API Base URL

**Local Development**: `http://localhost:5001/api/v1`

## 🔌 All API Endpoints

| Endpoint | Returns |
|----------|---------|
| `GET /` | Health check |
| `GET /api/v1/dashboard/stats` | `{testsTaken, averageScore, highestScore, questionsAnswered}` |
| `GET /api/v1/dashboard/recommendations` | `[{id, title, summary}, ...]` |
| `GET /api/v1/topics/:id/details` | `{id, title, summary, keyConcepts[], commonPitfalls[], example{}}` |
| `GET /api/v1/flashcards` | `[{id, front, back}, ...]` |
| `GET /api/v1/profile/stats` | `{totalStudyTime, testsCompleted, highestScore, achievements}` |
| `GET /api/v1/profile/mastery` | `[{topic, mastery}, ...]` |
| `GET /api/v1/presets` | `[{id, name, description}, ...]` |

## 📝 Quick Test Examples

```bash
# Health check
curl http://localhost:5001/

# Get dashboard stats
curl http://localhost:5001/api/v1/dashboard/stats | python3 -m json.tool

# Get flashcards
curl http://localhost:5001/api/v1/flashcards | python3 -m json.tool
```

## 🗄️ Database Info

- **File**: `mindcraftr.db` (SQLite)
- **Tables**: users, test_results, recommended_topics, flashcards, topic_mastery
- **Default User ID**: 1 (Jane Doe)
- **Reset**: `rm mindcraftr.db && python seed.py`

## 🔧 Update Frontend API

Edit `frontend/services/api.ts` line 3:

```typescript
// Change this:
const API_BASE_URL = 'https://10d126a81553.ngrok-free.app/api/v1';

// To this:
const API_BASE_URL = 'http://localhost:5001/api/v1';
```

## 📊 Log Symbols

- 📥 Incoming request
- 📤 Outgoing response
- 🔍 Database query
- ✅ Success
- ⚠️ Warning
- ❌ Error

## 🐛 Common Issues

### Port 5000 Already Used
✅ Fixed! We use port 5001 instead

### Flask Not Found
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### CORS Error
✅ Already configured! Check server logs to verify `Access-Control-Allow-Origin = *`

### Frontend Not Connecting
1. Check backend is running: `curl http://localhost:5001/`
2. Update `frontend/services/api.ts` with correct URL
3. Check browser console for errors

## 📂 Project Structure

```
MindCraftr/
├── database.py          # Database functions
├── seed.py             # Database initialization
├── server.py           # Flask API with logging
├── requirements.txt    # Python dependencies
├── start_server.sh     # Start script
├── test_api.sh         # Test script
├── mindcraftr.db       # SQLite database
├── venv/               # Virtual environment (ignored by git)
└── frontend/           # React frontend
```

## 🎯 Typical Workflow

1. **First Time Setup**:
```bash
./start_server.sh  # Creates venv, installs deps, starts server
```

2. **Update Frontend**:
```bash
cd frontend
# Edit services/api.ts to point to http://localhost:5001/api/v1
npm run dev
```

3. **Test Everything**:
```bash
./test_api.sh
```

4. **Monitor Requests**:
Watch the server terminal for detailed logs

## 📚 Documentation Files

- `README.md` - Complete setup guide
- `LOGGING_GUIDE.md` - Logging details
- `FRONTEND_INTEGRATION.md` - Frontend connection guide
- `SETUP_COMPLETE.md` - Success summary
- `QUICK_REFERENCE.md` - This file!

---

**Pro Tip**: Keep the server terminal visible while developing to see real-time API logs! 🎯

