@echo off
SETLOCAL

:: 1. Check for FFmpeg
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] FFmpeg not found! Please install it and add to PATH.
    echo run: winget install Gyan.FFmpeg
    exit /b 1
)

:: 2. Check for Redis (Optional check, hard to verify port without tools)
echo [INFO] Ensure Redis is running on localhost:6379

:: 3. Start Infrastructure (You usually run these in separate terminals)
echo [TIP] You need to run 'chroma run --path ./chroma_db' in another terminal.
echo [TIP] You need to run 'celery -A app.celery_app worker --pool=sole --loglevel=info' in another terminal.

:: 4. Start API
echo [INFO] Starting FastAPI...
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --env-file .env

ENDLOCAL
