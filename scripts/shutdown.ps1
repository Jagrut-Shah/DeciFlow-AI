# Shutdown script for DeciFlow AI
# This script terminates all processes running on the default ports for frontend (3000) and backend (8000)

Write-Host "Initiating DeciFlow AI System Shutdown..." -ForegroundColor Cyan

# Function to kill process on a port
function Stop-PortProcess($port) {
    $processId = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1
    if ($processId) {
        $processName = (Get-Process -Id $processId).Name
        Write-Host "Stopping $processName on port $port (PID: $processId)..." -ForegroundColor Yellow
        Stop-Process -Id $processId -Force
        Write-Host "Port $port cleared." -ForegroundColor Green
    } else {
        Write-Host "No process found on port $port." -ForegroundColor Gray
    }
}

# Clear Frontend
Stop-PortProcess 3000

# Clear Backend
Stop-PortProcess 8000

# Additional cleanup for common names
Write-Host "Performing additional cleanup for 'node' and 'python' background tasks..." -ForegroundColor Cyan
Get-Process | Where-Object { $_.Name -match "node|python" -and $_.MainWindowTitle -eq "" } | ForEach-Object {
    # Only kill if it's likely part of this project (optional, can be more aggressive)
    # Write-Host "Force closing background process: $($_.Name)" -ForegroundColor Gray
    # Stop-Process -Id $_.Id -Force
}

Write-Host "System shutdown complete." -ForegroundColor Green
