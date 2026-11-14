# One-time: enable OpenSSH Server on Deploy Windows (run as Administrator).
# Usage: Right-click PowerShell -> Run as administrator
#        cd E:\sovereign-ai-repo; powershell -ExecutionPolicy Bypass -File .\scripts\deploy-openssh-server.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Install / start OpenSSH Server ===" -ForegroundColor Cyan

$cap = Get-WindowsCapability -Online | Where-Object Name -like "OpenSSH.Server*"
Write-Host "Capability state:" $cap.State
if ($cap.State -ne "Installed") {
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
}

Start-Service sshd
Set-Service -Name sshd -StartupType Automatic

$fw = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
if ($fw) {
    Write-Host "Firewall rule OpenSSH-Server-In-TCP exists."
} else {
    Write-Host "If connection fails, allow TCP 22 for Private profile in Windows Firewall."
}

Write-Host ""
Write-Host "sshd status:" (Get-Service sshd).Status
Write-Host ""
Write-Host "LAN IPv4 addresses (use one as HostName in WSL ~/.ssh/config):"
Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -notlike "127.*" -and $_.PrefixOrigin -ne "WellKnown" } |
    ForEach-Object { Write-Host "  $($_.IPAddress)  ($($_.InterfaceAlias))" }

$auth = Join-Path $env:USERPROFILE ".ssh\authorized_keys"
Write-Host ""
Write-Host "Next: paste WSL public key into:" $auth
Write-Host "Then from WSL: ssh deploy"