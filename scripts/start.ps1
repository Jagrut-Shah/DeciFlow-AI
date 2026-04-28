# Startup script for DeciFlow AI
# This script starts the backend and frontend in separate windows

Write-Host "Initializing DeciFlow AI Full-Stack Environment..." -ForegroundColor Cyan

# Start Backend
Write-Host "Launching Backend (FastAPI) on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn app.main:app --reload --port 8000" -WindowStyle Normal

# Wait a bit for backend to initialize
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Launching Frontend (Next.js) on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Normal

Write-Host "Both services are launching in separate windows." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Gray
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Gray
