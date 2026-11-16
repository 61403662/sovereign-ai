$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
& .\.venv\Scripts\python.exe -m sovereign_ai.bom --init --reset
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }