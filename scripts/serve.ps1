$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

& .\.venv\Scripts\python.exe -m sovereign_ai.serve @args