$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
& .\.venv\Scripts\python.exe -m sovereign_ai.bom --import-csv --reset @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }