# Deployment Guide - Should I Move?

This guide walks through deploying the "Should I Move?" API to Railway.

## Quick Start Checklist

- [ ] Code pushed to GitHub
- [ ] `.env` file configured locally (not committed to git)
- [ ] Railway account created
- [ ] OpenAI API key ready
- [ ] Firecrawl API key ready

## Pre-Deployment: Local Testing

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
```

**Important:** Never commit `.env` to git. Make sure it's in `.gitignore`.

### 3. Test Locally

Start the server:

```bash
python api.py
```

In another terminal, run the test script:

```bash
python test_api.py
```

Or visit the interactive docs:
- Open browser to http://localhost:8000/docs
- Try the `/analyze` endpoint with sample data

## Deploy to Railway

### Step 1: Prepare Your Repository

1. **Ensure all required files are in your repo:**
   - `api.py` - FastAPI application
   - `agno_coordinator.py` - Agent coordinator with non-interactive function
   - `requirements.txt` - Python dependencies
   - `railway.toml` - Railway configuration
   - `.env.example` - Environment variable template
   - All `sub_agents/` files

2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Add FastAPI server for Railway deployment"
   git push origin main
   ```

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Sign up or log in
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Authorize Railway to access your GitHub account
6. Select your `should-i-move` repository

### Step 3: Configure Environment Variables

1. In Railway dashboard, click on your deployed service
2. Go to the **"Variables"** tab
3. Click **"Add Variable"**
4. Add the following variables one by one:

   ```
   OPENAI_API_KEY = your_openai_api_key_here
   FIRECRAWL_API_KEY = your_firecrawl_api_key_here
   ```

5. Click **"Deploy"** if not already deploying

### Step 4: Verify Deployment

1. Railway will provide a public URL (e.g., `https://should-i-move-production.up.railway.app`)
2. Copy this URL
3. Test the health endpoint:
   ```bash
   curl https://your-url.railway.app/health
   ```
4. Visit the API docs:
   ```
   https://your-url.railway.app/docs
   ```

### Step 5: Test the Deployed API

Run the test script against your Railway deployment:

```bash
python test_api.py https://your-url.railway.app
```

## Railway Configuration Explained

The `railway.toml` file tells Railway how to deploy your app:

```toml
[build]
builder = "NIXPACKS"  # Railway's automatic builder

[deploy]
startCommand = "uvicorn api:app --host 0.0.0.0 --port $PORT"  # Start command
healthcheckPath = "/health"  # Health check endpoint
healthcheckTimeout = 300  # Wait up to 5 minutes for first health check
restartPolicyType = "ON_FAILURE"  # Auto-restart if crashes
restartPolicyMaxRetries = 10  # Retry up to 10 times
```

Railway automatically:
- Detects `requirements.txt` and installs dependencies
- Sets the `PORT` environment variable
- Handles SSL/TLS certificates
- Provides logging and monitoring

## Monitoring Your Deployment

### Check Logs

1. Go to Railway dashboard
2. Click on your service
3. View **"Logs"** tab to see real-time logs

### Monitor Health

Use the health check endpoint:

```bash
curl https://your-url.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-11T14:30:22.123456"
}
```

### Check Active Analyses

Railway doesn't have a built-in dashboard for this. Consider adding:

```python
@app.get("/admin/analyses")
async def list_analyses():
    """List all active analyses (add authentication in production!)"""
    return {
        "total": len(analysis_results),
        "analyses": [
            {
                "id": aid,
                "status": data["status"],
                "created_at": data["created_at"]
            }
            for aid, data in analysis_results.items()
        ]
    }
```

## Troubleshooting

### Deployment Fails

**Problem:** Build fails during deployment

**Solutions:**
1. Check Railway logs for specific error
2. Verify `requirements.txt` has all dependencies
3. Ensure `railway.toml` is in root directory
4. Check that Python version is compatible (Railway uses latest by default)

### Application Crashes

**Problem:** App starts but crashes immediately

**Solutions:**
1. Check Railway logs for error messages
2. Verify environment variables are set correctly
3. Test locally first with same environment variables
4. Check for missing dependencies

### Timeouts

**Problem:** Requests timeout or return 504

**Solutions:**
1. Agent analysis can take 2-5 minutes - this is normal
2. Consider implementing webhooks instead of polling
3. Increase Railway's timeout settings if needed
4. Use Railway's background jobs feature for long-running tasks

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'agno_coordinator'`

**Solutions:**
1. Ensure the file is named `agno_coordinator.py` (with underscore, not hyphen)
2. Python cannot import modules with hyphens in filenames
3. The import statement should be `from agno_coordinator import ...`

### Environment Variables Not Working

**Problem:** API keys not found

**Solutions:**
1. Verify variables are set in Railway dashboard (not `.env` file)
2. Check spelling matches exactly
3. Redeploy after adding variables
4. Use `os.getenv()` with defaults for debugging:
   ```python
   api_key = os.getenv("OPENAI_API_KEY", "NOT_SET")
   print(f"API Key: {api_key[:10]}...")  # Print first 10 chars
   ```

## Production Best Practices

### 1. Add Database Storage

Replace in-memory `analysis_results` dictionary with Redis or PostgreSQL:

```python
# Install: pip install redis
import redis

redis_client = redis.from_url(os.getenv("REDIS_URL"))

# Store result
redis_client.setex(
    f"analysis:{analysis_id}",
    3600,  # Expire after 1 hour
    json.dumps(result)
)
```

Railway provides Redis add-on in marketplace.

### 2. Add Authentication

Protect your API with API keys:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    valid_key = os.getenv("API_KEY")
    if api_key != valid_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.post("/analyze")
async def analyze_move(
    request: AnalysisRequest,
    api_key: str = Depends(verify_api_key)
):
    # ... rest of the code
```

### 3. Add Rate Limiting

Prevent abuse with rate limits:

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("5/minute")
async def analyze_move(...):
    # ... rest of the code
```

### 4. Add Webhook Support

Instead of polling, support webhooks:

```python
class AnalysisRequest(BaseModel):
    # ... existing fields ...
    webhook_url: Optional[str] = None

async def run_analysis(analysis_id: str, user_profile: UserProfile, webhook_url: Optional[str]):
    try:
        recommendation = analyze_move_non_interactive(user_profile)
        # ... save results ...
        
        # Send webhook if provided
        if webhook_url:
            requests.post(webhook_url, json={
                "analysis_id": analysis_id,
                "status": "completed",
                "result": recommendation.model_dump()
            })
    except Exception as e:
        # ... handle error ...
```

### 5. Add Monitoring

Use Railway's built-in metrics or add external monitoring:

```bash
pip install sentry-sdk
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
)
```

## Cost Considerations

### Railway Costs
- Free tier: $5/month credit
- Hobby plan: $5/month
- Pro plan: $20/month
- Additional usage: Pay as you go

### API Costs
- **OpenAI**: GPT-4o-mini is cost-effective for this use case
  - Each analysis uses multiple calls to the API
  - Estimate: $0.10-0.50 per analysis
- **Firecrawl**: Web scraping API
  - Free tier available
  - Pay per request after free tier

### Optimization Tips
1. Cache common queries (city data doesn't change often)
2. Use GPT-4o-mini instead of GPT-4 for cost savings
3. Limit concurrent analyses to control costs
4. Add usage quotas per user/API key

## Scaling

### Vertical Scaling (Railway)
- Increase memory allocation
- Upgrade to Pro plan for better performance

### Horizontal Scaling
For high traffic, consider:
1. **Message Queue**: Use Celery + Redis for background tasks
2. **Load Balancer**: Railway Pro supports multiple instances
3. **Database**: Move from in-memory to PostgreSQL/Redis
4. **CDN**: Cache static content and API responses

## Support

### Getting Help
- Railway docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- FastAPI docs: https://fastapi.tiangolo.com

### Common Resources
- Railway status: https://status.railway.app
- OpenAI status: https://status.openai.com
- Project logs: Railway dashboard → Logs tab
