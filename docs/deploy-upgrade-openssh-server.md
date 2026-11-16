# Upgrade OpenSSH Server on Deploy (fix dev client 9.5 ↔ server 8.1)

Dev PC may ship **OpenSSH 9.5**; Windows optional **OpenSSH Server** is often **8.1**. Symptom from dev:

- `kex_exchange_identification: Connection closed by remote host`
- or `banner exchange` timeout

On Deploy, `ssh -vv bryan@10.10.10.2` works — server is fine for 8.1 clients.

## Recommended: install latest Win32-OpenSSH

1. Download latest **OpenSSH-Win64.zip** from [PowerShell/Win32-OpenSSH releases](https://github.com/PowerShell/Win32-OpenSSH/releases).
2. Admin PowerShell (Backup config first):

   ```powershell
   Copy-Item C:\ProgramData\ssh\sshd_config C:\ProgramData\ssh\sshd_config.bak
   Stop-Service sshd
   # Extract zip; run install-sshd.ps1 from extracted folder (see release README)
   Restart-Service sshd
   ssh -V   # on server: sshd should report 9.x
   ```

3. Re-run `scripts/deploy-fix-sshd-config-encoding.ps1` and `deploy-fix-ssh-authorized-keys.ps1`.

4. From dev: `ssh deploy-direct hostname`

## Until upgraded

Dev `~/.ssh/config` `deploy-direct` may set `KexAlgorithms` / `HostKeyAlgorithms` for 8.1. Still flaky if corp endpoint filters SSH — use **git push / Deploy pull**.