# Repair Windows OpenSSH sshd when clients see:
#   kex_exchange_identification: Connection closed by remote host
# Run on DEPLOY as Administrator.

$ErrorActionPreference = "Continue"
$sshData = "C:\ProgramData\ssh"

Write-Host "=== sshd repair ===" -ForegroundColor Cyan
Write-Host "sshd:" (Get-Service sshd).Status

if (-not (Test-Path $sshData)) {
    Write-Host "Missing $sshData - reinstall OpenSSH Server optional feature."
    exit 1
}

Push-Location $sshData
# Regenerate host keys if missing (idempotent)
& ssh-keygen.exe -A 2>&1 | ForEach-Object { Write-Host $_ }
Pop-Location

# Host key ACL (sshd may drop connections if too permissive)
Get-ChildItem $sshData\ssh_host_* -ErrorAction SilentlyContinue | ForEach-Object {
    icacls $_.FullName /inheritance:r 2>$null | Out-Null
    icacls $_.FullName /grant "SYSTEM:(R)" 2>$null | Out-Null
    icacls $_.FullName /grant "BUILTIN\Administrators:(R)" 2>$null | Out-Null
}

$sshdCfg = Join-Path $sshData "sshd_config"
if (Test-Path $sshdCfg) {
    $test = & C:\Windows\System32\OpenSSH\sshd.exe -t -f $sshdCfg 2>&1
    Write-Host "sshd -t:" $test
}

Restart-Service sshd
Start-Sleep -Seconds 2
Write-Host "sshd after restart:" (Get-Service sshd).Status

Write-Host ""
Write-Host "Test ON DEPLOY (same machine):"
Write-Host "  ssh -v bryan@127.0.0.1"
Write-Host "If localhost works but LAN client fails, check firewall profile Private."
Write-Host ""
Write-Host "Recent OpenSSH events:"
Get-WinEvent -LogName "OpenSSH/Operational" -MaxEvents 5 -ErrorAction SilentlyContinue |
    ForEach-Object { Write-Host $_.TimeCreated $_.Message }