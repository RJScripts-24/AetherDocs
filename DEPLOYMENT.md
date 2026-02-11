# 🚀 Deployment Guide: AetherDocs

This guide explains how to deploy **AetherDocs** with a Render backend and a Vercel frontend.

---

## 1. Backend Deployment (Render)

Render will host our FastAPI server, the Celery background worker, and a Redis instance. This configuration uses a **native Python environment** (no Docker).

### Prerequisites
- A [Render](https://render.com/) account.
- Your project pushed to a GitHub/GitLab repository.

### Option A: Blueprint (Easiest)
We have included a `render.yaml` in the root directory configured for native Python.
1. Go to **Dashboard** -> **Blueprints**.
2. Connect your repository.
3. Render will automatically detect the `render.yaml` and prompt you for the `GROQ_API_KEY`.
4. Click **Apply**.

### Option B: Manual Setup
If you prefer manual setup, create three services:

#### 1. Redis (Free Plan)
- **Service Type**: Redis
- **Name**: `aetherdocs-cache`

#### 2. Web Service (FastAPI)
- **Name**: `aetherdocs-api`
- **Environment**: `Python 3`
- **Root Directory**: `backend`
- **Build Command**: `./render-build.sh`
- **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
- **Environment Variables**:
    - `REDIS_URL`: (Internal Redis URL from the Redis service)
    - `GROQ_API_KEY`: `your_key_here`
    - `BACKEND_CORS_ORIGINS`: `https://your-frontend-url.vercel.app`
    - `PATH`: `/opt/render/ffmpeg_bin:/usr/local/bin:/usr/bin:/bin`

#### 3. Background Worker (Celery)
- **Name**: `aetherdocs-worker`
- **Environment**: `Python 3`
- **Root Directory**: `backend`
- **Build Command**: `./render-build.sh`
- **Start Command**: `celery -A worker worker --loglevel=info`
- **Environment Variables**:
    - `REDIS_URL`: (Internal Redis URL)
    - `GROQ_API_KEY`: `your_key_here`
    - `PATH`: `/opt/render/ffmpeg_bin:/usr/local/bin:/usr/bin:/bin`

---

## 2. Frontend Deployment (Vercel)
(The frontend deployment remains the same as it is already "normally" deployed as a static Vite site).

### Prerequisites
- A [Vercel](https://vercel.com/) account.

### Steps
1. Click **New Project** in Vercel.
2. Select your repository.
3. In the **Root Directory** setting, select `frontend`.
4. **Framework Preset**: Vite.
5. **Environment Variables**:
    - `VITE_API_URL`: `https://your-render-api-url.onrender.com`
6. Click **Deploy**.

---

## 3. Important Notes

### ⚠️ Persistence (ChromaDB)
Render's free tier Web Services do not support persistent disks. This means your uploaded documents and processed "Common Books" will be lost whenever the server restarts or redeploys. For production use, consider:
- Upgrading to a paid Render tier to use **Persistent Disks**.
- Using a cloud vector database (like Pinecone or MongoDB Atlas Vector Search).

### ⚠️ Cold Starts
The Render free tier puts services to sleep after inactivity. The first request to the API might take 30+ seconds to respond.

### ⚠️ Performance
AI transcription and synthesis are CPU-heavy. The free tier may time out on large files. For the best experience, use a plan with at least 2GB of RAM.
