$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$pythonExe = Join-Path $repoRoot ".venv\\Scripts\\python.exe"
$frontendUrl = "http://127.0.0.1:5173"

Set-Location $repoRoot

& (Join-Path $PSScriptRoot "bootstrap.ps1")

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Starting PostgreSQL and Redis..."
    docker compose -f "infra/docker-compose.local.yml" up -d
} else {
    Write-Host "Docker not found. PostgreSQL and Redis were not started automatically."
}

$backendCommand = "Set-Location '$repoRoot'; & '$pythonExe' -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000"
$workerCommand = "Set-Location '$repoRoot'; & '$pythonExe' -m celery -A worker.app.celery_app.celery_app worker --loglevel=info --pool=solo"
$frontendCommand = "Set-Location '$repoRoot'; npm run dev --prefix frontend -- --host 127.0.0.1 --port 5173"

Write-Host "Starting FastAPI, Celery worker, and Vite..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand
Start-Process powershell -ArgumentList "-NoExit", "-Command", $workerCommand
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

Start-Sleep -Seconds 6
Start-Process $frontendUrl

Write-Host "PyCrawler Research Studio is opening in your browser at $frontendUrl"
