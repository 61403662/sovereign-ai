# Pull latest code on Deploy. On failure, run deploy-git-doctor.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

git pull
if ($LASTEXITCODE -ne 0) {
    Write-Host "`ngit pull failed. Run:  .\scripts\deploy-git-doctor.ps1 -ApplyFixes" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "OK. Current:" (git log -1 --oneline)
