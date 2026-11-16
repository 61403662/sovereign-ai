# Deploy-only checklist (Bryan PC · 192.168.2.45)

Dev PC (ghjv84) is configured separately. You only need this on **Deploy**.

## 1. sshd running

```powershell
Get-Service sshd
```

## 2. Self-test (must pass before blaming dev PC)

```powershell
ssh -v bryan@127.0.0.1
ssh -v bryan@192.168.2.45
```

Both should show `Remote protocol version`. If `192.168.2.45` fails but `127.0.0.1` works → firewall / LAN binding.

## 3. Firewall (Admin)

```powershell
New-NetFirewallRule -Name "OpenSSH-Server-In-TCP-sshd" `
  -DisplayName "OpenSSH Server sshd.exe" `
  -Enabled True -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22 `
  -Program "$env:Windir\System32\OpenSSH\sshd.exe" `
  -Profile Private,Domain
Restart-Service sshd
```

WiFi network profile must be **Private** (`Get-NetConnectionProfile`).

## 4. Repair + keys (repo)

```powershell
cd E:\sovereign-ai-repo
git pull
powershell -ExecutionPolicy Bypass -File .\scripts\deploy-repair-sshd.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\deploy-fix-ssh-authorized-keys.ps1
```

`authorized_keys` must contain dev pubkey line from ghjv84 (see dev script output).

## 5. Optional: reinstall OpenSSH Server

Settings → Optional features → OpenSSH Server → reinstall → `Restart-Service sshd`.

## 6. Tell dev when ready

When `ssh -v bryan@192.168.2.45` works on Deploy, dev runs:

`powershell -File .\scripts\dev-test-deploy-connection.ps1`