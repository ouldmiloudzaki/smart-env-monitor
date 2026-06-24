# Smart Environmental Monitor — one-command launcher (Windows / PowerShell)
# Creates a virtualenv on first run, installs deps, then starts the server.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$venv = Join-Path $root ".venv"

if (-not (Test-Path $venv)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv $venv
}

$python = Join-Path $venv "Scripts\python.exe"

Write-Host "Installing dependencies..." -ForegroundColor Cyan
& $python -m pip install --quiet --upgrade pip
& $python -m pip install --quiet -r (Join-Path $root "backend\requirements.txt")

Write-Host "Starting server at http://127.0.0.1:8000 ..." -ForegroundColor Green
Set-Location (Join-Path $root "backend")
& $python -m uvicorn app:app --host 127.0.0.1 --port 8000
