# Dev → Deploy SSH（网线 10.10.10.x）

## When to stop fighting GitHub `ssh` on dev

- Home Wi‑Fi / corp router may block LAN SSH.
- Company dev PC may ship **OpenSSH 9.5**; symptom: `kex_exchange_identification: Connection closed`.
- **Deploy** upgraded to **Win32-OpenSSH 10.4** under `C:\Program Files\OpenSSH` is enough for the server.

## Recommended daily workflow (no LAN SSH)

1. **Dev**: `git push` to GitHub.
2. **Deploy**: `git pull` in `E:\sovereign-ai-repo`.

## If you keep a direct cable (10.10.10.1 ↔ 10.10.10.2)

### Deploy

- `sshd` **Running**, `C:\Program Files\OpenSSH\sshd.exe`
- `deploy-fix-ssh-authorized-keys.ps1`
- No global `GSSAPIAuthentication` in `sshd_config` (OpenSSH 9.x+)

### Dev — match client version

Do **not** rely on `C:\Windows\System32\OpenSSH\ssh.exe` (9.5) if KEX keeps closing.

1. Download the **same** [OpenSSH-Win64.zip](https://github.com/PowerShell/Win32-OpenSSH/releases) used on Deploy.
2. Unzip to `%USERPROFILE%\OpenSSH` (no `install-sshd.ps1` on dev).
3. Test:

   ```powershell
   & "$env:USERPROFILE\OpenSSH\ssh.exe" -i $env:USERPROFILE\.ssh\id_ed25519_deploy bryan@10.10.10.2 hostname
   ```

4. Optional: `scripts/dev-openssh-client-portable.ps1` after unzip.

### `~/.ssh/config`

```
Host deploy-direct
  HostName 10.10.10.2
  User bryan
  IdentityFile ...
  IdentitiesOnly yes
```

Use portable ssh via full path or `ssh-deploy.cmd`.