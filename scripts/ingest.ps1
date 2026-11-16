# Run from repo root on Deploy (Windows)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Error "Missing .venv — see docs/runbook.md Phase 1 setup"
}
.\.venv\Scripts\Activate.ps1
# Do not pip install on every run — rebuilding chroma-hnswlib needs MSVC on Windows.
python -c "import chromadb" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "chromadb missing; install once per runbook Phase 1 (Python 3.12, binary wheels)."
    python -m pip install --only-binary :all: numpy httpx PyYAML 2>$null
    python -m pip install --only-binary :all: "chromadb>=0.5.23,<0.6"
    python -m pip install -r requirements.txt
}
python -m sovereign_ai.ingest @args
