# Deployment Guide - Cloud Hosting

## 🚀 Deploy to Render (Free & Easy)

### Prerequisites
- GitHub account
- Git installed on your computer

### Step-by-Step Deployment

#### 1. **Initialize Git Repository** (if not already done)

```bash
cd c:\Users\aksha\backend

# Initialize git
git init

# Create .gitignore
echo "__pycache__/" > .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "logs/" >> .gitignore
echo "test_request.json" >> .gitignore

# Add all files
git add .

# Commit
git commit -m "Initial commit - Simulation Agent API"
```

#### 2. **Push to GitHub**

```bash
# Create a new repository on GitHub (go to github.com/new)
# Name it something like: simulation-agent-api

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/simulation-agent-api.git
git branch -M main
git push -u origin main
```

#### 3. **Deploy on Render**

1. Go to https://render.com and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your `simulation-agent-api` repository
5. Configure the service:

   **Settings:**
   - **Name**: `simulation-agent-api` (or any name you like)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements-api.txt`
   - **Start Command**: `uvicorn src.api.simulation_api:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

6. Click **"Create Web Service"**

#### 4. **Wait for Deployment** (2-3 minutes)

Render will:
- Install dependencies
- Start your API
- Provide you with a URL like: `https://simulation-agent-api.onrender.com`

#### 5. **Test Your Deployed API**

```bash
# Health check
curl https://YOUR-APP-NAME.onrender.com/api/simulation/health

# Or visit in browser
https://YOUR-APP-NAME.onrender.com/docs
```

---

## 🌐 Alternative: Deploy to Railway

### Quick Deploy to Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects Python and deploys!
6. Get your URL from the Railway dashboard

**No configuration needed!** Railway automatically:
- Detects `requirements-api.txt`
- Runs the app
- Provides a public URL

---

## 📱 Alternative: Deploy to Google Cloud Run

### Deploy to Cloud Run (Free Tier)

1. **Install Google Cloud SDK**
2. **Create a Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY . .

CMD ["uvicorn", "src.api.simulation_api:app", "--host", "0.0.0.0", "--port", "8080"]
```

3. **Deploy**:

```bash
gcloud run deploy simulation-agent-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🔗 Share Your API

Once deployed, share with your friend:

**Your API URL**: `https://your-app-name.onrender.com`

**Message Template:**
```
Hey! The Simulation Agent API is live:

🔗 API: https://your-app-name.onrender.com
📚 Docs: https://your-app-name.onrender.com/docs
✅ Health: https://your-app-name.onrender.com/api/simulation/health

Try it out! Full documentation at /docs
```

---

## ⚠️ Important Notes

### Free Tier Limitations

**Render Free Tier:**
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month free

**Railway Free Tier:**
- $5 free credit per month
- No spin-down delay
- Faster than Render

**Google Cloud Run:**
- 2 million requests/month free
- No spin-down on free tier
- Best performance

### Keep Your API Alive

For Render, to prevent spin-down:
1. Use a service like **UptimeRobot** (free)
2. Ping your health endpoint every 10 minutes
3. Or upgrade to paid tier ($7/month)

---

## 🔧 Troubleshooting

### Build Fails
- Check `requirements-api.txt` has all dependencies
- Verify Python version in `runtime.txt`
- Check logs in Render dashboard

### Import Errors
- Ensure all `__init__.py` files are committed
- Verify absolute imports are used

### Port Issues
- Use `$PORT` environment variable (already configured)
- Don't hardcode port 8000

---

## 📊 Monitor Your API

**Render Dashboard:**
- View logs
- Monitor requests
- Check performance
- See deployment history

**Access logs:**
```bash
# In Render dashboard → Logs tab
# Real-time logs of all API requests
```

---

## 🎉 You're Done!

Your API is now live and accessible worldwide! Share the URL with your friend and they can start using it immediately without any setup.
