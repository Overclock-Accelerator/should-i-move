# Reddit Integration Setup Guide

## Problem
The Migration Researcher agent is showing:
```
"reddit_insights_included": false,
"redditor_perspectives": "I attempted to fetch Reddit threads but API access failed..."
```

This means the Reddit API credentials are not properly configured.

## Solution: Set Up Reddit API Credentials

### Step 1: Create a Reddit Application

1. Go to https://www.reddit.com/prefs/apps
2. Log in to your Reddit account (or create one if needed)
3. Scroll down and click **"create another app..."** or **"create app"**
4. Fill out the form:
   - **name**: `should-i-move-app` (or any name you like)
   - **App type**: Select **"script"**
   - **description**: `City migration research tool` (optional)
   - **about url**: Leave blank
   - **redirect uri**: `http://localhost:8080` (required even though we won't use it)
5. Click **"create app"**

### Step 2: Get Your Credentials

After creating the app, you'll see:
- **Client ID**: A string under "personal use script" (looks like: `abc123XYZ456`)
- **Client Secret**: Labeled as "secret" (looks like: `xyz789ABC123def456`)

### Step 3: Add Credentials to .env File

Create or edit the `.env` file in your project root:

```bash
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=ShouldIMoveApp/1.0 by YourRedditUsername

# Your existing credentials
OPENAI_API_KEY=your_openai_key_here
FIRECRAWL_API_KEY=your_firecrawl_key_here
```

**Important Notes:**
- Replace `your_client_id_here` with your actual client ID
- Replace `your_client_secret_here` with your actual client secret
- Replace `YourRedditUsername` with your Reddit username
- The `REDDIT_USER_AGENT` format should be: `AppName/Version by Username`

### Step 4: Install Required Package

Make sure you have the `praw` package installed:

```bash
pip install praw
```

### Step 5: Test Your Setup

Run the debug script to verify everything works:

```bash
python debug_reddit_tools.py
```

This will test:
1. ✅ Environment variables are set
2. ✅ PRAW library is installed
3. ✅ Reddit API connection works
4. ✅ Reddit search functionality works
5. ✅ Agno RedditTools integration works
6. ✅ Agent can use Reddit tools

## Expected Output

If everything is working, you should see:
```
Results: 6/6 tests passed
✅ All tests passed! Reddit integration is working correctly.
```

## Troubleshooting

### "praw library not installed"
```bash
pip install praw
```

### "REDDIT_CLIENT_ID is NOT SET"
- Check that your `.env` file exists in the project root
- Check that there are no quotes around the values
- Check that there are no extra spaces
- Make sure you restart your terminal/IDE after editing `.env`

### "Failed to connect to Reddit API"
- Verify your credentials are correct
- Check that your Reddit account is in good standing
- Try creating a new Reddit app

### "Invalid credentials"
- Double-check you copied the client ID and secret correctly
- The client ID is the shorter string under "personal use script"
- The client secret is the longer string labeled "secret"

## After Setup

Once your credentials are working, run your main script again:

```bash
python 02-agno-coordination.py
```

The Migration Researcher should now successfully fetch Reddit discussions and you'll see:
```
"reddit_insights_included": true,
"redditor_perspectives": "Based on Reddit discussions, Redditors say..."
```

## Reddit API Limits

- Reddit's free API allows ~60 requests per minute
- This is plenty for the Should I Move? app
- The agent will automatically handle rate limiting

