$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
& .\.venv\Scripts\python.exe -m sovereign_ai.eval eval\clarify_trigger.example.jsonl @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }