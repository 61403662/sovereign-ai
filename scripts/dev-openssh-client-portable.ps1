# DEV PC: use same OpenSSH build as Deploy (e.g. 10.4), without installing sshd service.
# 1) Copy OpenSSH-Win64.zip contents to $dest (or set $dest after unzip).
# 2) Run this script (Admin only if you install under Program Files).
param(
    [string]$dest = "$env:USERPROFILE\OpenSSH"
)

if (-not (Test-Path "$dest\ssh.exe")) {
    $nested = Get-ChildItem $dest -Directory -ErrorAction SilentlyContinue |
        Where-Object { Test-Path (Join-Path $_.FullName "ssh.exe") } | Select-Object -First 1
    if ($nested) { Copy-Item "$($nested.FullName)\*" $dest -Force }
}
if (-not (Test-Path "$dest\ssh.exe")) {
    Write-Host "Missing $dest\ssh.exe — unzip OpenSSH-Win64.zip into $dest (or run C:\Users\ghjv84\install-openssh-client.ps1)"
    exit 1
}

$shim = Join-Path $env:USERPROFILE "ssh-deploy.cmd"
@"
@echo off
"%USERPROFILE%\OpenSSH\ssh.exe" -F "%USERPROFILE%\.ssh\config" deploy-direct %*
"@ | Set-Content -Path $shim -Encoding ascii

Write-Host "Portable client OK."
Write-Host "  & '$dest\ssh.exe' -V"
Write-Host "  & '$dest\ssh.exe' -i `$env:USERPROFILE\.ssh\id_ed25519_deploy bryan@10.10.10.2 hostname"
Write-Host "  Or: $shim hostname"