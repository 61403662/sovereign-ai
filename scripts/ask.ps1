$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
.\.venv\Scripts\Activate.ps1
python -m sovereign_ai.ask @args
