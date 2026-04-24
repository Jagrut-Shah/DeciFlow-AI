# DeciFlow AI - Platform Launcher
Write-Host "🚀 Launching DeciFlow AI Command Center..." -ForegroundColor Cyan

# 1. Start Backend
Write-Host "📦 Starting FastAPI Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; if (-not (Test-Path .venv)) { python -m venv .venv; .\.venv\Scripts\activate; pip install -r requirements.txt }; .\.venv\Scripts\activate; python -m uvicorn app.main:app --reload --port 8000"

# 2. Start Frontend
Write-Host "🎨 Starting Next.js Premium Frontend..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "✨ Platform initialized!" -ForegroundColor Yellow
Write-Host "Backend: http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:3000"
