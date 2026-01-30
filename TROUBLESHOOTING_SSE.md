# 🔧 Troubleshooting SSE Real-Time Progress

## Issue: Progress feed shows "🔄 Live Progress" but no events appear

### Quick Fixes

#### 1. Restart the Backend Server

The SSE endpoint needs the latest code. Restart your backend:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
cd backend
uvicorn app.main:app --reload
```

#### 2. Check Browser Console

Open browser DevTools (F12) and check the Console tab. You should see:
```
SSE connection opened
SSE message received: {"type":"started",...}
SSE message received: {"type":"sources",...}
...
```

If you see errors, they'll tell you what's wrong.

#### 3. Test SSE Endpoint Directly

Open this URL in your browser:
```
http://localhost:8000/api/scraper/scrape/test-stream
```

You should see:
```
data: {"type":"test","message":"Test message 1"}

data: {"type":"test","message":"Test message 2"}

...
```

If this doesn't work, SSE isn't configured properly.

#### 4. Check Network Tab

In browser DevTools, go to Network tab:
1. Click "Start Scraping"
2. Look for request to `/api/scraper/scrape/stream`
3. Check if it's pending (good) or failed (bad)
4. Click on it to see response

#### 5. Verify Backend is Running

Make sure backend is running on port 8000:
```bash
curl http://localhost:8000/api/scraper/sources
```

Should return JSON with sources.

---

## Common Issues

### Issue 1: CORS Error

**Symptom:** Console shows CORS error

**Fix:** Make sure backend CORS is configured for `http://localhost:3000`

Check `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 2: Database Connection Error

**Symptom:** Error message about database

**Fix:** Run database migration:
```bash
cd backend
python migrate_db.py
```

### Issue 3: Import Errors

**Symptom:** Backend won't start, import errors

**Fix:** Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Issue 4: Port Already in Use

**Symptom:** Backend won't start, "Address already in use"

**Fix:** Kill existing process:
```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

---

## Debug Mode

### Enable Verbose Logging

Add this to see what's happening:

**Backend** (`backend/app/routes/scraper.py`):
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def event_generator():
    logger.debug("Starting event generator")
    yield f"data: {json.dumps({'type': 'started', ...})}\n\n"
    logger.debug("Sent started event")
    ...
```

**Frontend** (already added):
```typescript
console.log('SSE connection opened');
console.log('SSE message received:', event.data);
```

---

## Manual Test

### Test with curl

```bash
curl -N http://localhost:8000/api/scraper/scrape/stream?limit_per_source=5
```

You should see events streaming:
```
data: {"type":"started","message":"Starting scraper...","total_sources":3}

data: {"type":"sources","sources":["ted_eu","sam_gov","uk_contracts_finder"]}

data: {"type":"scraping","source":"ted_eu","message":"Scraping TED..."}

...
```

If this works but browser doesn't, it's a frontend issue.

---

## Fallback: Use Old Endpoint

If SSE still doesn't work, you can fall back to the synchronous endpoint:

**Frontend** (`Scraper.tsx`):
```typescript
const handleScrape = async () => {
  setIsScraping(true);
  try {
    const res = await fetch(`/api/scraper/scrape/live?limit_per_source=${limitPerSource}`, {
      method: 'POST'
    });
    const data = await res.json();
    setResults(data.results);
    setSummary({
      total_saved: data.results.reduce((sum, r) => sum + r.contracts_saved, 0),
      sources_completed: data.results.length
    });
  } catch (err) {
    setError(err.message);
  } finally {
    setIsScraping(false);
  }
};
```

This won't show real-time progress but will work reliably.

---

## Still Not Working?

### Check These:

1. ✅ Backend running on port 8000?
2. ✅ Frontend running on port 3000?
3. ✅ No errors in backend terminal?
4. ✅ No errors in browser console?
5. ✅ Database file exists (`contracts.db`)?
6. ✅ Dependencies installed?

### Get Help:

Run this diagnostic:
```bash
cd backend
python -c "
import sys
print('Python version:', sys.version)
try:
    import fastapi
    print('FastAPI version:', fastapi.__version__)
except:
    print('FastAPI not installed!')
try:
    import sqlalchemy
    print('SQLAlchemy version:', sqlalchemy.__version__)
except:
    print('SQLAlchemy not installed!')
"
```

---

## Quick Fix Script

Save this as `fix_sse.sh`:

```bash
#!/bin/bash

echo "🔧 Fixing SSE issues..."

# Kill existing backend
echo "Stopping existing backend..."
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Reinstall dependencies
echo "Reinstalling dependencies..."
cd backend
pip install -r requirements.txt

# Migrate database
echo "Migrating database..."
python migrate_db.py

# Start backend
echo "Starting backend..."
uvicorn app.main:app --reload &

echo "✅ Done! Wait 5 seconds then try again."
```

Run it:
```bash
chmod +x fix_sse.sh
./fix_sse.sh
```

---

## Expected Behavior

When working correctly, you should see:

1. Click "🚀 Start Scraping"
2. Button changes to "Scraping..." with spinner
3. "🔄 Live Progress" section appears
4. Events stream in real-time:
   - 🚀 Starting scraper...
   - 📊 Sources: ted_eu, sam_gov, uk_contracts_finder
   - 🔍 Scraping TED EU...
   - ✅ ted_eu: Found 5, Saved 5 (0.5s)
   - 🔍 Scraping SAM.gov...
   - ✅ sam_gov: Found 5, Saved 5 (0.5s)
   - 🔍 Scraping UK Finder...
   - ✅ uk_contracts_finder: Found 3, Saved 3 (0.3s)
5. Final summary appears
6. Button returns to "🚀 Start Scraping"

---

**If you're still stuck, check the browser console - it will tell you exactly what's wrong!**
