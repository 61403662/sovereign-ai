# Enable OpenSSH Server on Deploy (run as Administrator).
#   cd E:\sovereign-ai-repo
#   powershell -ExecutionPolicy Bypass -File .\scripts\deploy-openssh-server.ps1

param(
    [switch]$SkipInstall
)

$ErrorActionPreference = "Continue"

function Test-IsAdmin {
    $p = New-Object Security.Principal.WindowsPrincipal(
        [Security.Principal.WindowsIdentity]::GetCurrent()
    )
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

Write-Host "=== OpenSSH Server setup ===" -ForegroundColor Cyan

if (-not (Test-IsAdmin)) {
    Write-Host "ERROR: Run PowerShell as Administrator." -ForegroundColor Red
    exit 1
}

$capName = "OpenSSH.Server~~~~0.0.1.0"

if (-not $SkipInstall) {
    $installed = $false
    try {
        $cap = Get-WindowsCapability -Online | Where-Object Name -like "OpenSSH.Server*"
        Write-Host "Capability state:" $cap.State
        if ($cap.State -eq "Installed") {
            $installed = $true
        } else {
            Add-WindowsCapability -Online -Name $capName
            $installed = $true
        }
    } catch {
        Write-Host "DISM cmdlet failed:" $_.Exception.Message
        & dism.exe /Online /Add-Capability /CapabilityName:$capName
        if ($LASTEXITCODE -eq 0) { $installed = $true }
    }
    if (-not $installed) {
        Write-Host "Install OpenSSH Server via Settings - Optional features - Add a feature."
        Write-Host "Then run: deploy-openssh-server.ps1 -SkipInstall"
        exit 1
    }
} else {
    Write-Host "SkipInstall: only start sshd."
}

$svc = Get-Service sshd -ErrorAction SilentlyContinue
if (-not $svc) {
    Write-Host "ERROR: sshd service missing. Install OpenSSH Server first." -ForegroundColor Red
    exit 1
}

Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
Write-Host "sshd status:" (Get-Service sshd).Status

Write-Host ""
Write-Host "IPv4 for WSL HostName:"
ipconfig | findstr /i "IPv4"

Write-Host ""
Write-Host "Add WSL public key to:"
Write-Host "$env:USERPROFILE\.ssh\authorized_keys"