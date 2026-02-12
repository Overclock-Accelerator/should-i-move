# Getting Started with the API

Quick reference guide for using the "Should I Move?" API.

## What We Built

You now have a **FastAPI server** that wraps your multi-agent system. This allows:

- ✅ **POST requests** to trigger move analyses
- ✅ **Asynchronous processing** of long-running agent tasks
- ✅ **Status polling** to check progress
- ✅ **JSON responses** with structured recommendations
- ✅ **Railway deployment** for production hosting

## File Overview

| File | Purpose |
|------|---------|
| `api.py` | FastAPI server with REST endpoints |
| `agno_coordinator.py` | Updated with non-interactive analysis function |
| `test_api.py` | Test script to verify API works |
| `requirements.txt` | Updated with FastAPI and uvicorn |
| `railway.toml` | Railway deployment configuration |
| `.env.example` | Template for environment variables |
| `API_GUIDE.md` | Complete API usage documentation |
| `DEPLOYMENT.md` | Step-by-step Railway deployment guide |

## Test Locally in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
Ensure your `.env` file has:
```env
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
```

### Step 3: Run & Test
Terminal 1 - Start server:
```bash
python api.py
```

Terminal 2 - Run tests:
```bash
python test_api.py
```

Or visit: http://localhost:8000/docs

## Deploy to Railway in 5 Steps

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add FastAPI server"
git push origin main
```

### Step 2: Create Railway Project
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### Step 3: Add Environment Variables
In Railway dashboard → Variables tab:
- `OPENAI_API_KEY`
- `FIRECRAWL_API_KEY`

### Step 4: Deploy
Railway deploys automatically. Wait for build to complete.

### Step 5: Test
```bash
# Replace with your Railway URL
python test_api.py https://your-app.railway.app
```

## API Endpoints

### POST /analyze
Submit analysis request → Get analysis ID

### GET /analysis/{id}
Check status → Get results when complete

### GET /health
Health check for monitoring

### DELETE /analysis/{id}
Clean up completed analysis

## Example Request

```json
POST /analyze
{
  "current_city": "San Francisco",
  "desired_city": "Austin",
  "annual_income": 120000,
  "monthly_expenses": 4500,
  "city_preferences": ["tech jobs", "lower cost", "warm weather"],
  "current_city_likes": ["tech scene", "food"],
  "current_city_dislikes": ["expensive", "traffic"]
}
```

## Example Response

```json
{
  "analysis_id": "analysis_20260211_143022_123456",
  "status": "pending",
  "message": "Analysis request received",
  "estimated_completion_time": "2-5 minutes"
}
```

Poll for results:
```bash
GET /analysis/analysis_20260211_143022_123456
```

When completed:
```json
{
  "status": "completed",
  "result": {
    "recommendation": "Recommend moving with preparation",
    "confidence_level": "High",
    "key_supporting_factors": [...],
    "cost_analysis_report": "...",
    "sentiment_analysis_report": "...",
    "migration_analysis_report": "...",
    "next_steps": [...]
  }
}
```

## Workflow

```
1. Client sends POST /analyze
           ↓
2. Server queues analysis (returns ID)
           ↓
3. Client polls GET /analysis/{id}
           ↓
4. Server processes with agents
           ↓
5. Client receives completed result
```

## Next Steps

- **Local Testing**: Run `python test_api.py`
- **Read Docs**: Check `API_GUIDE.md` for detailed usage
- **Deploy**: Follow `DEPLOYMENT.md` for Railway setup
- **Integrate**: Use the API in your frontend application

## Need Help?

- 📖 Full API docs: http://localhost:8000/docs
- 📘 Usage guide: `API_GUIDE.md`
- 🚀 Deployment: `DEPLOYMENT.md`
- 🐛 Issues: Check Railway logs or run with `--reload` for debugging

## Still Using CLI?

The original interactive CLI still works:
```bash
python agno_coordinator.py
```

Both CLI and API modes use the same agent system!
