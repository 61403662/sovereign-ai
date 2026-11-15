# Deploy (Admin). OpenSSH 9.x rejects global GSSAPIAuthentication — remove it so sshd can start.
$ErrorActionPreference = "Stop"
$cfg = "C:\ProgramData\ssh\sshd_config"
$sshd = if (Test-Path "C:\Program Files\OpenSSH\sshd.exe") {
    "C:\Program Files\OpenSSH\sshd.exe"
} else {
    "C:\Windows\System32\OpenSSH\sshd.exe"
}
$lines = Get-Content $cfg | Where-Object { $_ -notmatch '^\s*GSSAPIAuthentication\s' }
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($cfg, ($lines -join "`r`n") + "`r`n", $utf8NoBom)
& $sshd -t -f $cfg
Restart-Service sshd
Get-Service sshd | Format-Table Name, Status
Write-Host "Removed GSSAPIAuthentication from global sshd_config."