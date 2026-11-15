# Run on Deploy (Admin). Removes UTF-8 BOM from sshd_config (breaks Windows sshd / kex).
$ErrorActionPreference = "Stop"
$cfg = "C:\ProgramData\ssh\sshd_config"
$text = Get-Content -Path $cfg -Raw
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($cfg, $text, $utf8NoBom)
& C:\Windows\System32\OpenSSH\sshd.exe -t
Restart-Service sshd
Write-Host "sshd_config saved as UTF-8 without BOM. Test: ssh from dev deploy-direct"