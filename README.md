# AetherDocs Setup & Execution Guide

This document provides a comprehensive guide on setting up and running the **AetherDocs** project locally. The system is modular, requiring multiple services (Backend, Frontend, Redis, ChromaDB, Celery) to run simultaneously.

---

## 📂 Project Structure Overview

- **`backend/`**: Contains the FastAPI application, Celery tasks, and AI processing logic.
- **`frontend/`**: Contains likely React/Vite-based user interface.
- **`chroma_db/`**: Directory for persistent vector database storage (located inside `backend/`).

---

## 🛠 Prerequisites & Dependencies

Before starting, ensure you have the following installed on your system:

### 1. Core Runtime
- **Python 3.10+**: Required for the backend.
- **Node.js (v18+) & npm**: Required for the frontend.

### 2. Required Services
- **Redis Server**: Required as a message broker for Celery.
  - *Windows*: Install via WSL or use a redis binary for Windows (e.g., Memurai or via Docker).
  - *Linux/Mac*: `sudo apt install redis-server` / `brew install redis`
- **FFmpeg**: Required for audio/video processing (e.g., extracting audio from videos).
  - *Windows*: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add `bin` folder to your system PATH.
  - *Linux/Mac*: `sudo apt install ffmpeg` / `brew install ffmpeg`

---

## 📦 Installation Instructions

### 1. Backend Setup
Open a terminal and navigate to the project directory:

```bash
cd backend
```

Create a virtual environment (optional but recommended):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Frontend Setup
Open a **new** terminal and navigate to the `frontend` directory:

```bash
cd frontend
```

Install Node.js dependencies:
```bash
npm install
```

---

## 🚀 How to Run the Project (Detailed Guide)

**CRITICAL NOTE**: This project creates a complex distributed system. **You MUST open 5 separate terminal windows** to run all components simultaneously. Do not try to run them in the same window.

### Terminal 1: Redis Server
Start your Redis server. This manages the task queue for Celery.

**Command:**
```bash
redis-server
```
*Ensure it is running on the default port `6379`.*

---

### Terminal 2: ChromaDB (Vector Database)
Start the ChromaDB server for vector storage. This handles document embeddings.
Navigate to the `backend` folder first.

**Command:**
```bash
cd backend
chroma run --path ./chroma_db --port 8001
```
*This command starts ChromaDB using the `chroma_db` directory for persistence. We use port 8001 to avoid conflict with the backend API on port 8000.*

**Important**: 
Update your `backend/.env` file to point to this local instance:
```env
CHROMA_HOST=localhost
CHROMA_PORT=8001
```

---

### Terminal 3: Celery Worker (Background Tasks)
Start the Celery worker to handle asynchronous tasks like document processing.
Navigate to the `backend` folder and ensure your virtual environment is activated.

**Command:**
```bash
cd backend
# Windows (Use 'solo' worker pool for Windows compatibility)
celery -A app.celery_app worker --pool=solo --loglevel=info

# Linux/Mac
celery -A app.celery_app worker --loglevel=info
```
*Note: Make sure your Redis server (Terminal 1) is running before starting this.*

---

### Terminal 4: Backend API (FastAPI)
Start the main backend server.
Navigate to the `backend` folder and ensure your virtual environment is activated.

**Command:**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --env-file .env
```
*The backend will be available at `http://localhost:8000`.*

---

### Terminal 5: Frontend Application
Start the frontend development server.
Navigate to the `frontend` folder.

**Command:**
```bash
cd frontend
npm run dev
```
*The frontend will typically run at `http://localhost:5173` or similar.*

---

## 📝 Configuration

- **Environment Variables**: ensure a `.env` file exists in the `backend/` directory with necessary keys (e.g., `GROQ_API_KEY`, `REDIS_URL`, etc.). use `.env.example` as a template.
- **API URL**: If the frontend fails to connect, check `frontend/src/api/config.ts` (or similar) to ensure it points to `http://localhost:8000`.

## ⚠️ Troubleshooting

- **Celery on Windows**: If you see errors about "spawn" or "fork", ensure you use `--pool=solo`.
- **FFmpeg missing**: If audio processing fails, verify FFmpeg is in your system PATH by running `ffmpeg -version` in a terminal.
