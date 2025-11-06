# Quick Fix: Reddit 401 Error

## The Problem
Your Reddit app was created as a **"web app"** but needs to be a **"script"** for read-only API access.

## The Solution (5 minutes)

### Step 1: Delete Old App
1. Go to: https://www.reddit.com/prefs/apps
2. Find your current app (might be called "YourApp" or similar)
3. Click **"delete app"** and confirm

### Step 2: Create New Script App
1. Still on https://www.reddit.com/prefs/apps
2. Click **"create another app"** or **"create app"**
3. Fill out:
   ```
   name: should-i-move
   
   App type: ● script  ← SELECT THIS ONE (not "web app")
   
   description: (leave blank or add anything)
   
   about url: (leave blank)
   
   redirect uri: http://localhost:8080
   ```
4. Click **"create app"**

### Step 3: Copy New Credentials

After creating, you'll see something like:

```
should-i-move
personal use script
mh_bF3MQa1b2c3d4e    ← This is your CLIENT_ID

secret
o1Jh8PL2xyz789abc    ← This is your CLIENT_SECRET (click "show" if hidden)
```

### Step 4: Update .env File

Open your `.env` file and update these lines:

```bash
REDDIT_CLIENT_ID=mh_bF3MQa1b2c3d4e
REDDIT_CLIENT_SECRET=o1Jh8PL2xyz789abc
REDDIT_USER_AGENT=ShouldIMoveApp/1.0 by YourRedditUsername
```

**Important:** Replace with YOUR actual values!

### Step 5: Test Again

```bash
python debug_reddit_tools.py
```

You should now see:
```
✅ PASS  Reddit Search
```

### Step 6: Run Your App

```bash
python 02-agno-coordination.py
```

The Migration Researcher will now successfully fetch Reddit discussions! 🎉

---

## Why This Happens

Reddit has different app types:
- **"web app"** - For websites with user login flows
- **"script"** - For personal scripts and read-only access ← **You need this one**

The credentials from a "web app" won't work for read-only API calls, which is why you get a 401 error.

