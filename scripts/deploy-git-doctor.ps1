# Diagnose Deploy git pull to GitHub (HTTPS 443). Run from repo root.
# Usage:  cd E:\sovereign-ai-repo; .\scripts\deploy-git-doctor.ps1
# Optional fixes:  .\scripts\deploy-git-doctor.ps1 -ApplyFixes

param(
    [switch]$ApplyFixes
)

$ErrorActionPreference = "Continue"
$RepoRoot = if ($PSScriptRoot) { Join-Path $PSScriptRoot ".." } else { Get-Location }
Set-Location $RepoRoot

Write-Host "=== sovereign-ai deploy git doctor ===" -ForegroundColor Cyan
Write-Host "Repo: $(Get-Location)"

function Show-ProxyConfig {
    Write-Host "`n--- git proxy (all levels) ---" -ForegroundColor Yellow
    git config --list --show-origin 2>$null | Select-String -Pattern "proxy" -CaseSensitive:$false
    foreach ($level in @("system", "global", "local")) {
        $h = git config --$level --get http.proxy 2>$null
        $s = git config --$level --get https.proxy 2>$null
        if ($h -or $s) { Write-Host "  $level http.proxy=$h https.proxy=$s" }
    }
    Write-Host "  Env HTTP_PROXY=$env:HTTP_PROXY"
    Write-Host "  Env HTTPS_PROXY=$env:HTTPS_PROXY"
}

function Test-GitHubTcp {
    Write-Host "`n--- TCP 443 (Test-NetConnection) ---" -ForegroundColor Yellow
    $t = Test-NetConnection github.com -Port 443 -WarningAction SilentlyContinue
    Write-Host "  TcpTestSucceeded: $($t.TcpTestSucceeded)"
}

function Test-CurlGitHub {
    Write-Host "`n--- curl HEAD https://github.com ---" -ForegroundColor Yellow
    & curl.exe -I --max-time 20 https://github.com 2>&1 | Select-Object -First 5
}

function Test-GitLsRemote {
    Write-Host "`n--- git ls-remote (same stack as pull) ---" -ForegroundColor Yellow
    $url = git remote get-url origin 2>$null
    Write-Host "  origin: $url"
    git ls-remote origin HEAD 2>&1 | Select-Object -First 3
}

Show-ProxyConfig
Test-GitHubTcp
Test-CurlGitHub
Test-GitLsRemote

if ($ApplyFixes) {
    Write-Host "`n--- applying common HTTPS fixes ---" -ForegroundColor Green
    git config --global --unset http.proxy 2>$null
    git config --global --unset https.proxy 2>$null
    git config --local --unset http.proxy 2>$null
    git config --local --unset https.proxy 2>$null
    git config --global http.version HTTP/1.1
    git config --global http.sslBackend schannel
    Write-Host "  Set http.version=HTTP/1.1, sslBackend=schannel; cleared proxy."
    Write-Host "`nRetry:"
    git pull
} else {
    Write-Host "`n--- next steps ---" -ForegroundColor Cyan
    Write-Host "  1) If TcpTestSucceeded=True but git fails:  .\scripts\deploy-git-doctor.ps1 -ApplyFixes"
    Write-Host "  2) Still fails: switch origin to SSH (see docs/runbook.md § Git pull fails)"
    Write-Host "  3) Emergency: copy from WSL  /mnt/e/sovereign-ai-repo  after git pull in ~/sovereign-ai"
}
