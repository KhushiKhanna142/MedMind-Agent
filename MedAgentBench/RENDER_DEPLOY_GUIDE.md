# 🚀 Deploying MedAgentBench to Render

## Step 1: Push Changes to GitHub
I have already created the necessary configuration files (`render.yaml` and updated `api_requirements.txt`). I will push these to your GitHub repository in the next step.

## Step 2: Connect to Render

1. Go to [dashboard.render.com](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Click **"Build and deploy from a Git repository"**
4. Connect your GitHub account if you haven't already
5. Select your repo: **`KhushiKhanna142/-MedAgentBench`**

## Step 3: Configure Service

Render might auto-detect the configuration, but verify these settings:

- **Name**: `medagentbench-api` (or whatever you prefer)
- **Region**: Choose closest to you (e.g., Singapore, Oregon)
- **Branch**: `main`
- **Root Directory**: `.` (leave empty)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r api_requirements.txt`
- **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

## Step 4: Environment Variables (Optional)

If you have API keys (like OpenAI or Vertex AI credentials), add them under **"Environment"**:
- Key: `GOOGLE_APPLICATION_CREDENTIALS_JSON` (if using Vertex AI)
- Value: (Paste your JSON content)

## Step 5: Deploy

Click **"Create Web Service"**. Render will start building your app. It usually takes 2-3 minutes.

Once done, you'll get a URL like: `https://medagentbench.onrender.com`

## 🔗 Accessing Your API

- **Swagger UI**: `https://YOUR-APP-URL.onrender.com/docs`
- **Health Check**: `https://YOUR-APP-URL.onrender.com/health`

---

**Status**: ✅ Configuration files created. Ready to push to GitHub!
