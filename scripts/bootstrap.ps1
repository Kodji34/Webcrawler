$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$venvPath = Join-Path $repoRoot ".venv"
$pythonExe = Join-Path $venvPath "Scripts\\python.exe"

Set-Location $repoRoot

if (-not (Test-Path $pythonExe)) {
    Write-Host "Creating Python virtual environment..."
    python -m venv $venvPath
}

Write-Host "Installing Python dependencies..."
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -e ".[dev]"

Write-Host "Installing frontend dependencies..."
npm install --prefix frontend
