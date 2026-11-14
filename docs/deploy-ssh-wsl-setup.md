# WSL → Deploy SSH 实操（跟着做）

两套 SSH 不要混：**Deploy→GitHub**（拉代码）和 **WSL→Deploy**（远程敲命令）。

## A. Deploy（管理员 PowerShell，一次）

**必须「以管理员身份运行」PowerShell**（窗口标题含 Administrator）。普通窗口里 `Get-WindowsCapability` 会报错。

```powershell
cd E:\sovereign-ai-repo
git pull
powershell -ExecutionPolicy Bypass -File .\scripts\deploy-openssh-server.ps1
```

若 DISM/能力安装失败，用图形界面安装（无需 DISM）：

1. **设置** → **应用** → **可选功能**（或「已安装的应用」→ **可选功能**）
2. **添加功能** → 搜 **OpenSSH 服务器** → 安装
3. 再执行（只启动服务）：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy-openssh-server.ps1 -SkipInstall
```

记下脚本打印的 **IPv4**（例如 `192.168.x.x`）。

把 **WSL 开发机** 上的公钥（`id_ed25519_deploy.pub` 整行）写入：

`C:\Users\<你的Windows用户>\.ssh\authorized_keys`

```powershell
mkdir $env:USERPROFILE\.ssh -Force
notepad $env:USERPROFILE\.ssh\authorized_keys
```

粘贴后保存。可选收紧权限：

```powershell
icacls $env:USERPROFILE\.ssh\authorized_keys /inheritance:r
icacls $env:USERPROFILE\.ssh\authorized_keys /grant:r "$($env:USERNAME):(R)"
```

## B. WSL（开发机，一次）

公钥若没有：

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_deploy -N "" -C "wsl-to-deploy"
```

`~/.ssh/config`：

```sshconfig
Host deploy
  HostName 192.168.x.x
  User bryan
  IdentityFile ~/.ssh/id_ed25519_deploy
  IdentitiesOnly yes
```

`HostName`、`User` 换成你的 Deploy IP 和 Windows 登录名。

## C. 验收

```bash
ping -c 2 192.168.x.x
ssh deploy
```

登录后 `exit`。远程一条命令：

```bash
ssh deploy 'cd /d E:\sovereign-ai-repo && git pull && git log -1 --oneline'
```

## D. 隧道 + 网页问答

Deploy 上先 `.\scripts\serve.cmd`，WSL 另一终端：

```bash
ssh -N -L 8787:127.0.0.1:8787 deploy
```

浏览器：`http://127.0.0.1:8787`