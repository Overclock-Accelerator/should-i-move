# Should I Move? - API Guide

This guide explains how to use the FastAPI server for the "Should I Move?" agent system.

## Overview

The API provides endpoints to submit move analysis requests and retrieve results. The analysis runs asynchronously using multiple AI agents that research costs, sentiment, and migration experiences.

## Running Locally

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add:
- `OPENAI_API_KEY`: Your OpenAI API key
- `FIRECRAWL_API_KEY`: Your Firecrawl API key (for web scraping)

### 3. Start the Server

```bash
python api.py
```

Or using uvicorn directly:

```bash
uvicorn api:app --reload --port 8000
```

The server will be available at `http://localhost:8000`

### 4. Test the API

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## API Endpoints

### `POST /analyze`

Submit a move analysis request.

**Request Body:**
```json
{
  "current_city": "New York City",
  "desired_city": "Austin",
  "annual_income": 85000,
  "monthly_expenses": 3500,
  "city_preferences": ["good weather", "tech industry", "arts scene"],
  "current_city_likes": ["great public transit", "diverse food options"],
  "current_city_dislikes": ["high cost of living", "harsh winters"]
}
```

**Response (202 Accepted):**
```json
{
  "analysis_id": "analysis_20260211_143022_123456",
  "status": "pending",
  "message": "Analysis request received and queued for processing",
  "estimated_completion_time": "2-5 minutes"
}
```

### `GET /analysis/{analysis_id}`

Check the status and retrieve results of an analysis.

**Response (Processing):**
```json
{
  "analysis_id": "analysis_20260211_143022_123456",
  "status": "processing",
  "message": "Analysis in progress...",
  "result": null,
  "error": null
}
```

**Response (Completed):**
```json
{
  "analysis_id": "analysis_20260211_143022_123456",
  "status": "completed",
  "message": "Analysis completed successfully",
  "result": {
    "recommendation": "Recommend moving with moderate preparation",
    "confidence_level": "High",
    "key_supporting_factors": [...],
    "key_concerns": [...],
    "cost_analysis_report": "...",
    "sentiment_analysis_report": "...",
    "migration_analysis_report": "...",
    "featured_migration_quotes": [...],
    "next_steps": [...],
    "detailed_justification": "..."
  },
  "error": null
}
```

### `DELETE /analysis/{analysis_id}`

Delete an analysis record from memory.

**Response:**
```json
{
  "message": "Analysis 'analysis_20260211_143022_123456' deleted successfully",
  "deleted_at": "2026-02-11T14:35:22.123456"
}
```

### `GET /health`

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-11T14:30:22.123456"
}
```

## Example Usage with cURL

### Submit an analysis request:

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "current_city": "New York City",
    "desired_city": "Austin",
    "annual_income": 85000,
    "monthly_expenses": 3500,
    "city_preferences": ["good weather", "tech industry"],
    "current_city_likes": ["great public transit"],
    "current_city_dislikes": ["high cost of living"]
  }'
```

### Check status:

```bash
curl "http://localhost:8000/analysis/analysis_20260211_143022_123456"
```

## Example Usage with Python

```python
import requests
import time

# Submit analysis request
response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "current_city": "New York City",
        "desired_city": "Austin",
        "annual_income": 85000,
        "monthly_expenses": 3500,
        "city_preferences": ["good weather", "tech industry"],
        "current_city_likes": ["great public transit"],
        "current_city_dislikes": ["high cost of living"]
    }
)

analysis_id = response.json()["analysis_id"]
print(f"Analysis ID: {analysis_id}")

# Poll for results
while True:
    status_response = requests.get(
        f"http://localhost:8000/analysis/{analysis_id}"
    )
    data = status_response.json()
    
    print(f"Status: {data['status']}")
    
    if data["status"] == "completed":
        print("Analysis complete!")
        print(data["result"])
        break
    elif data["status"] == "failed":
        print(f"Analysis failed: {data['error']}")
        break
    
    time.sleep(10)  # Wait 10 seconds before checking again
```

## Deploying to Railway

### 1. Prerequisites

- Railway account (https://railway.app)
- GitHub repository with your code
- Environment variables configured

### 2. Deployment Steps

1. **Push your code to GitHub**

2. **Create a new project on Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure environment variables**
   - In Railway dashboard, go to your project
   - Click on "Variables"
   - Add the following variables:
     - `OPENAI_API_KEY`
     - `FIRECRAWL_API_KEY`

4. **Deploy**
   - Railway will automatically detect `railway.toml` and use it for deployment
   - The build will install dependencies from `requirements.txt`
   - The server will start with the command specified in `railway.toml`

5. **Access your API**
   - Railway will provide a public URL (e.g., `https://your-app.railway.app`)
   - Your API will be available at that URL
   - Test it: `https://your-app.railway.app/health`

### 3. Monitoring

- Check logs in Railway dashboard
- Health check endpoint: `/health`
- Railway will automatically restart the service if it crashes

## Production Considerations

### 1. **Database Storage**
Currently, analysis results are stored in memory. For production:
- Use Redis for caching results
- Use PostgreSQL for persistent storage
- Consider a message queue (Celery, RabbitMQ) for long-running tasks

### 2. **Rate Limiting**
Add rate limiting to prevent abuse:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/analyze")
@limiter.limit("5/minute")
async def analyze_move(...):
    ...
```

### 3. **Authentication**
Add API key authentication:
```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
```

### 4. **CORS Configuration**
Update CORS settings to only allow your frontend domain:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. **Logging**
Add structured logging for better debugging:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Troubleshooting

### Port Issues
If you get a "port already in use" error:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Module Import Errors
Ensure you're using the correct module name:
- File is named `api.py`
- Import as: `from agno_coordinator import ...`
- Note: Python converts hyphens to underscores in imports

### Railway Deployment Fails
- Check Railway logs for error messages
- Verify all environment variables are set
- Ensure `requirements.txt` has all dependencies
- Check that `railway.toml` is in the root directory
