# Deploy (Admin): one-shot debug when dev sees "kex_exchange_identification: closed"
# Stops service sshd, runs foreground sshd on port 22 — only ONE dev connection, then exit.
$ErrorActionPreference = "Stop"
Write-Host "Stop service sshd; foreground debug on :22 (Ctrl+C to cancel)"
Stop-Service sshd -Force
& C:\Windows\System32\OpenSSH\sshd.exe -ddd -p 22