# Run from repo root on Deploy (Windows)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Error "Missing .venv — see docs/runbook.md Phase 1 setup"
}
.\.venv\Scripts\Activate.ps1
python -m pip install -q -r requirements.txt
python -m sovereign_ai.ingest @args
