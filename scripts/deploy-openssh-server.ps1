# One-time: enable OpenSSH Server on Deploy Windows.
# MUST: Right-click PowerShell -> Run as administrator (管理员), then:
#   cd E:\sovereign-ai-repo
#   powershell -ExecutionPolicy Bypass -File .\scripts\deploy-openssh-server.ps1
#
# If DISM fails, use Settings GUI (see docs/deploy-ssh-wsl-setup.md).

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

Write-Host "=== Install / start OpenSSH Server ===" -ForegroundColor Cyan

if (-not (Test-IsAdmin)) {
    Write-Host "ERROR: Not running as Administrator. Close and open PowerShell as Admin." -ForegroundColor Red
    Write-Host "GUI alternative: Settings -> Apps -> Optional features -> Add OpenSSH Server" -ForegroundColor Yellow
    exit 1
}

$sshd = Get-Service sshd -ErrorAction SilentlyContinue
if ($sshd -and $SkipInstall) {
    Write-Host "SkipInstall: using existing sshd."
} elseif (-not $SkipInstall) {
    $installed = $false
    try {
        $cap = Get-WindowsCapability -Online | Where-Object Name -like "OpenSSH.Server*"
        Write-Host "Capability state:" $cap.State
        if ($cap.State -eq "Installed") {
            $installed = $true
        } else {
            Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
            $installed = $true
        }
    } catch {
        Write-Host "Get-WindowsCapability / Add-WindowsCapability failed:" $_.Exception.Message -ForegroundColor Yellow
        Write-Host "Trying dism.exe ..." -ForegroundColor Yellow
        $dism = & dism.exe /Online /Add-Capability /CapabilityName:OpenSSH.Server~~~~0.0.1.0 2>&1
        $dism | ForEach-Object { Write-Host $_ }
        if ($LASTEXITCODE -eq 0) { $installed = $true }
    }
    if (-not $installed) {
        Write-Host ""
        Write-Host "Install via Settings:" -ForegroundColor Yellow
        Write-Host "  设置 -> 应用 -> 可选功能 -> 添加功能 -> OpenSSH 服务器"
        Write-Host "Then re-run:  .\scripts\deploy-openssh-server.ps1 -SkipInstall"
        exit 1
    }
}

Start-Service sshd -ErrorAction SilentlyContinue
Set-Service -Name sshd -StartupType Automatic -ErrorAction SilentlyContinue

$rule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
if ($rule) {
    Write-Host "Firewall rule OpenSSH-Server-In-TCP: present"
} else {
    Write-Host "Tip: allow TCP 22 on Private network in Windows Firewall if ssh fails."
}

$sshd = Get-Service sshd -ErrorAction SilentlyContinue
if (-not $sshd) {
    Write-Host "ERROR: sshd service not found. Install OpenSSH Server optional feature first." -ForegroundColor Red
    exit 1
}
Write-Host "sshd status:" $sshd.Status

Write-Host ""
Write-Host "LAN IPv4 (HostName in WSL ~/.ssh/config):"
Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -notlike "127.*" } |
    ForEach-Object { Write-Host "  $($_.IPAddress)  ($($_.InterfaceAlias))" }

Write-Host ""
Write-Host "Next: paste WSL id_ed25519_deploy.pub into:"
Write-Host "  $env:USERPROFILE\.ssh\authorized_keys"
Write-Host "Then from WSL: ssh deploy"