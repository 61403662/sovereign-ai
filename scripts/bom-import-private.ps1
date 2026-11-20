$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
$Dir = Join-Path $Root "data\private\fan\csv"
if (-not (Test-Path $Dir)) {
    Write-Error "Missing $Dir — copy CSVs from data\samples\fan\csv and edit (stays gitignored)."
}
& .\.venv\Scripts\python.exe -m sovereign_ai.bom --import-csv $Dir --reset @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }