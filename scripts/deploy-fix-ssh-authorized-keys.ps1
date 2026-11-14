# Run on DEPLOY as user bryan (Admin OK). Fixes Windows OpenSSH pubkey ACL + admin keys file.
#   powershell -ExecutionPolicy Bypass -File .\scripts\deploy-fix-ssh-authorized-keys.ps1

$ErrorActionPreference = "Stop"
$sshDir = Join-Path $env:USERPROFILE ".ssh"
$auth = Join-Path $sshDir "authorized_keys"
$adminAuth = "C:\ProgramData\ssh\administrators_authorized_keys"

New-Item -ItemType Directory -Force -Path $sshDir | Out-Null
if (-not (Test-Path $auth)) {
    New-Item -ItemType File -Path $auth | Out-Null
    Write-Host "Created empty $auth - paste your .pub line, then run this script again."
    exit 1
}

# Standard user authorized_keys ACL (required by Windows sshd)
icacls $sshDir /inheritance:r | Out-Null
icacls $sshDir /grant "SYSTEM:(OI)(CI)(F)" | Out-Null
icacls $sshDir /grant "$($env:USERNAME):(OI)(CI)(F)" | Out-Null

icacls $auth /inheritance:r | Out-Null
icacls $auth /grant "SYSTEM:(F)" | Out-Null
icacls $auth /grant "BUILTIN\Administrators:(F)" | Out-Null
icacls $auth /grant "$($env:USERNAME):(R)" | Out-Null

Write-Host "Fixed ACL on $sshDir and $auth"

# If bryan is in Administrators, also install pubkey copy for admin authorized_keys
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)
if ($isAdmin) {
    $programDataSsh = "C:\ProgramData\ssh"
    if (-not (Test-Path $programDataSsh)) { New-Item -ItemType Directory -Path $programDataSsh -Force | Out-Null }
    Copy-Item -Force $auth $adminAuth
    icacls $adminAuth /inheritance:r | Out-Null
    icacls $adminAuth /grant "SYSTEM:(F)" | Out-Null
    icacls $adminAuth /grant "BUILTIN\Administrators:(F)" | Out-Null
    Write-Host "Copied keys to $adminAuth (required when login user is Administrator)"
}

Write-Host "Pubkey lines in $auth :"
Get-Content $auth
Write-Host "Done. From dev PC: ssh -v deploy"