# Frontend Integration Guide

## Current Frontend API Configuration

Your frontend is currently configured to use:
```typescript
const API_BASE_URL = 'https://10d126a81553.ngrok-free.app/api/v1';
```

Location: `frontend/services/api.ts` (line 3)

## 🔧 Integration Options

### Option 1: Local Development (Recommended for Development)

Update `frontend/services/api.ts` to point to your local server:

```typescript
const API_BASE_URL = 'http://localhost:5001/api/v1';
```

**Pros:**
- Fastest response times
- No internet required
- Easy debugging with server logs
- Free

**Cons:**
- Only works on your machine

### Option 2: Use ngrok (For Remote Access or Deployment)

Keep using ngrok to expose your local server to the internet.

**Step 1**: Start your Flask server
```bash
./start_server.sh
```

**Step 2**: In a new terminal, expose it with ngrok
```bash
ngrok http 5001
```

**Step 3**: Update `frontend/services/api.ts` with the new ngrok URL
```typescript
const API_BASE_URL = 'https://YOUR-NGROK-URL.ngrok-free.app/api/v1';
```

**Pros:**
- Access from anywhere
- Share with team members
- Test on mobile devices

**Cons:**
- Requires internet
- URL changes when ngrok restarts
- Free tier has limitations

## 🎯 Quick Setup for Local Development

1. **Update Frontend API Config**:

```bash
cd frontend
# Edit services/api.ts line 3 to:
# const API_BASE_URL = 'http://localhost:5001/api/v1';
```

2. **Start the Backend**:

```bash
# In the root directory
./start_server.sh
```

3. **Start the Frontend** (in a new terminal):

```bash
cd frontend
npm install  # if not already done
npm run dev
```

4. **Open Browser**:

Visit `http://localhost:5173` (or whatever port Vite uses)

## 🔍 Verify Connection

Once both servers are running, check:

1. **Backend Health Check**:
```bash
curl http://localhost:5001/
# Should return: {"message": "MindCraftr API is running!", "version": "1.0.0"}
```

2. **Test API Endpoint**:
```bash
curl http://localhost:5001/api/v1/dashboard/stats
# Should return test statistics
```

3. **Check Frontend Console**:
Open browser DevTools → Network tab → You should see successful API calls with status 200

4. **Check CORS**:
In the Network tab, look for response headers:
- `access-control-allow-origin: *` should be present

## 🐛 Troubleshooting CORS Issues

If you see CORS errors in the browser console:

### ✅ What to Check

1. **Server Logs**: Look for the request in the backend terminal
   - If you see `📥 Incoming Request`, the frontend IS reaching the backend
   - If you DON'T see it, check the API_BASE_URL in your frontend

2. **CORS Headers**: In the backend logs, look for:
   ```
   📤 Response Status: 200
      CORS Headers: Access-Control-Allow-Origin = *
   ```
   - If it says `NOT SET`, there's a problem with Flask-CORS installation

3. **URL Mismatch**: Make sure:
   - Backend is running on `http://localhost:5001`
   - Frontend `api.ts` points to `http://localhost:5001/api/v1`
   - URLs match exactly (check for typos, http vs https, port numbers)

### 🔄 Reset Steps

If still having issues:

```bash
# 1. Stop backend (Ctrl+C)

# 2. Reset virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# 3. Reinstall dependencies
pip install -r requirements.txt

# 4. Restart server
python server.py
```

## 📊 Expected Log Output

When the frontend makes a request, you should see:

```
================================================================================
📥 Incoming Request: GET /api/v1/dashboard/stats
   Origin: http://localhost:5173
   User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...
🔍 Fetching dashboard stats for user_id: 1
   DB Result: tests_taken=3, avg_score=84.0, high_score=95, questions=50
   ✅ Returning stats: {'testsTaken': 3, 'averageScore': 84, ...}
📤 Response Status: 200
   CORS Headers: Access-Control-Allow-Origin = *
================================================================================
```

## 🎨 Frontend API File Structure

Your frontend already has perfect API integration:

```
frontend/services/
├── api.ts           ← Main API calls (UPDATE THIS FILE)
├── geminiService.ts ← AI service
└── testService.ts   ← Test logic
```

All API functions in `api.ts` are correctly formatted:
- ✅ `getDashboardStats()`
- ✅ `getRecommendedTopics()`
- ✅ `getTopicDetails(topicId)`
- ✅ `getFlashcards()`
- ✅ `getProfileStats()`
- ✅ `getTopicMastery()`
- ✅ `getExamPresets()`

**Just update the `API_BASE_URL` constant and you're done!**

## 🚀 Production Deployment

For production, you'll want to:

1. Deploy backend to a cloud service (Heroku, Railway, Render, etc.)
2. Get a permanent URL
3. Update `API_BASE_URL` in frontend
4. Deploy frontend (Vercel, Netlify, etc.)

But for hackathon/development, local or ngrok works perfectly!

---

**Need help?** Check the server logs - they'll tell you exactly what's happening with each request! 📊

