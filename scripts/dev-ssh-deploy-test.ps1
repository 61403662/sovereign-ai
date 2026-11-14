# Copy to dev PC: same as C:\Users\ghjv84\ssh-deploy-test.ps1
# Repo copy for git pull; optional.
. "$PSScriptRoot\..\ssh-deploy-test.ps1" 2>$null
if (-not $?) {
  Write-Host "Run from dev: C:\Users\ghjv84\ssh-deploy-test.ps1"
}