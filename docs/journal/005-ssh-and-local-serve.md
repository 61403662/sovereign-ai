# 主权 AI-05：SSH 与远程运维——先稳 pull，再 Tun 本机问答

（公众号草稿 · 脱敏后发表；06 写浏览器 UI 细节，本篇可含 serve 预览）

## 开篇

04 把正式 plan 问答跑通，但 Deploy 上 **HTTPS git pull** 仍可能超时，问答修正是 **git pull 之后才生效**。04 文末预告：先 **SSH / 远程**，再 **客户端**。

这一篇做两件事：

1. **Git 改 SSH**，少跟 443 赌运气。  
2. **（可选）** Windows 开 OpenSSH，WSL 一条 `ssh deploy` 远程 `pull` / `ask`；为 06 的 **`ssh -L` 隧道** 铺路。

## 一、为什么 05 在 06 前面

| 没有 SSH | 有了 SSH |
|----------|----------|
| pull 失败时问答还是旧 rerank | pull 稳定，04 里代码修法能跟上 |
| 只能坐在 Deploy 前敲 PowerShell | WSL 远程维护 Deploy |
| 06 API 只能本机浏览器开 | 笔记本浏览器经隧道访问 `127.0.0.1:8787` |

## 二、GitHub：Deploy 上 Git 走 SSH

【图1：ssh-keygen → GitHub 添加公钥 → git remote -v 显示 git@github.com】

要点（跟做清单）：

1. Deploy：`ssh-keygen -t ed25519` 专用 key（可 `id_ed25519_github`）  
2. 公钥贴到 GitHub → SSH keys  
3. `ssh -T git@github.com`  
4. `git remote set-url origin git@github.com:61403662/sovereign-ai.git`  
5. `git pull` + `git log -1`

与 **PowerShell 禁止 .ps1** 无关；doctor 仍用 `.cmd`。

## 三、连 Deploy 机器（可选）

【图2：WSL ~/.ssh/config Host deploy】

- Admin 开 **OpenSSH Server**，`sshd` 自动启动  
- WSL：`Host deploy` + 内网 IP（示例见 `docs/ssh-wsl-config.example`）  
- 验收：`ssh deploy 'hostname'` 或远程一条 `git pull`

远程 ask 示例（打码路径）：

`ssh deploy 'cd /d E:\…\sovereign-ai-repo && .venv\Scripts\python.exe -m sovereign_ai.ask "…"'`

## 四、本机 Web 问答（预告 06，可先试）

仓库已提供 **`python -m sovereign_ai.serve`**，只监听 **127.0.0.1:8787**。

Deploy：

```
pip install -e ".[serve]"
scripts\serve.cmd
```

浏览器打开 `http://127.0.0.1:8787`。

WSL 隧道（Deploy 上先启动 serve）：

`ssh -N -L 8787:127.0.0.1:8787 deploy`

然后在 WSL/本机浏览器访问 `http://127.0.0.1:8787`。**数据与 chroma 仍在 Deploy**。

## 五、本篇结果

- [ ] origin 为 `git@github.com:…` 且 pull 成功  
- [ ] （可选）WSL `ssh deploy` 能远程 pull 或 ask  
- [ ] （可选）serve + 隧道打开问答页  

## 六、下一篇（06）

单页体验、截图、安全边界（不接公网）；eval 更后。

公开仓库 + `docs/runbook.md` § SSH / Local ask UI。