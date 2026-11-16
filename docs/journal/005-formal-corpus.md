# 主权 AI-05：Deploy 用 SSH——先稳 pull，再连机器与打隧道

发表前脱敏：内网 IP、主机名、Windows 用户名、公司 VPN 产品名一律打码；`git remote -v` 截图可保留 `git@github.com`，勿露 Deploy 局域网地址。

## 开篇

04 把正式 plan 搬进本机 `data\raw`，问答对错高度依赖 **仓库里的 Python 是不是最新**。我在 Deploy 上踩过一种恨人的组合：`Test-NetConnection github.com -Port 443` **成功**，`git pull` 却 **二十秒超时**——代码还是旧的，rerank 修了也白修。

03、04 的 ingest / ask / chroma 都在 **Deploy 本机**；**GitHub 只同步代码**，不进私有语料。本篇只做 **运维链路**：让 **pull 稳定**，并（可选）让 **开发机 WSL 能远程维护 Deploy**，给下一篇 **本机浏览器问答 + 隧道** 铺路。

**两条 SSH 不要混：** 连 **github.com** 拉代码，和连 **家里 Deploy 的 Windows**，是两套密钥、两个 Host，互不替代。

---

## 一、为什么 05 在 06 前面

【图1 下正文】

| 没有稳 pull / 远程维护 | 有了之后 |
|------------------------|----------|
| HTTPS 443 时好时坏，问答仍是旧 rerank | `git pull` 可预期，04 排障表里的「先 pull」才靠谱 |
| 只能坐在 Deploy 前改代码、跑 ingest | WSL 可远程一条 `git pull` 或 `python -m sovereign_ai.ask` |
| 06 的页面只能 Deploy 本机浏览器开 | 笔记本可用 **`ssh -L`** 访问 Deploy 上的 `127.0.0.1:8787`（06 细写） |

Web 界面不 magic：**后端还是 ask**；**pull 不稳，UI 也是旧逻辑**。

---

## 二、主线：Deploy 上 Git 改走 GitHub SSH

【图2 下正文】

在 **Deploy 的 PowerShell** 里一次性配置（专用 key，与登录 Windows 的 key 分开亦可）：

```powershell
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ed25519_github -N '""'
Get-Content $env:USERPROFILE\.ssh\id_ed25519_github.pub
```

1. 复制 `.pub` 全文 → GitHub **Settings → SSH and GPG keys → New SSH key**（Deploy 机器专用，可命名 `deploy-sovereign-ai`）。
2. 首次探测：

```powershell
ssh -T git@github.com
```

提示 `yes` 后继续，看到 *successfully authenticated* 一类信息即可（GitHub 不分配 shell 是正常的）。

3. 改 remote 并验收：

```powershell
cd D:\你的仓库\sovereign-ai-repo
git remote set-url origin git@github.com:你的用户名/sovereign-ai.git
git remote -v
git pull
git log -1 --oneline
```

**跟做勾选：** `origin` 两行都是 `git@github.com:…`，`pull` 无超时。

这与 Windows **「禁止运行 .ps1」** 无关：那是 ExecutionPolicy；Git SSH 走 `ssh.exe`，**doctor 脚本仍用 `.cmd` 包装**（见下节）。

---

## 三、HTTPS 仍卡时：doctor 与应急同步

【图3 下正文】

SSH 配好前，或个别网络仍要 HTTPS，仓库有 **`scripts\deploy-git-doctor.cmd`**（读环境、代理、试 pull；可加 `-ApplyFixes` 切 HTTP/1.1、schannel 等）。

```powershell
cd D:\你的仓库\sovereign-ai-repo
.\scripts\deploy-git-doctor.cmd
.\scripts\deploy-git-doctor.cmd -ApplyFixes
```

| 现象 | 人话 | 建议 |
|------|------|------|
| 443 **TcpTest 成功**，`git pull` **超时** | libcurl/代理/HTTP2，不是「断网」 | 间隔重试；doctor；**中长期改 SSH origin** |
| 双击 `.ps1` 被策略拦截 | 默认 ExecutionPolicy | 用 **`.cmd`** 或 `powershell -ExecutionPolicy Bypass -File …` |
| 两种协议都暂时不行 | 少见，但会发生 | **Dev WSL `git pull` + 拷贝目录**到 Deploy（**不覆盖** `data\raw`、`storage`），见 runbook Step C |

无论哪条路：**`git pull` 不会删掉** 你的 `data\raw` 和 `storage\chroma`；怕的是 **拉不下新代码**，问答还在用旧 `ask`。

---

## 四、可选：WSL 连 Deploy 这台 Windows

【图4 下正文】

**目的：** 人不坐在 Deploy 前，也能 `ssh deploy '…'` 远程 `git pull` / `ask`。**前提：** 家里或办公室局域网能到 Deploy（与连 **github.com** 不是一回事）。

**Deploy 一次性（管理员 PowerShell）：**

```powershell
Get-WindowsCapability -Online | Where-Object Name -like "OpenSSH.Server*"
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

防火墙：专用网络允许 **入站 TCP 22**（按向导或组策略）。

**WSL：** 复制仓库 `docs/ssh-wsl-config.example` 到 `~/.ssh/config`，改 `HostName`（Deploy 局域网 IP）和 `User`（Windows 登录名）：

```sshconfig
Host deploy
  HostName 192.168.x.x
  User YourWindowsUser
  IdentitiesOnly yes
```

公钥写入 Deploy 用户 **`authorized_keys`**（OpenSSH 与「远程桌面」是两套东西）。

验收：

```bash
ssh deploy 'hostname'
ssh deploy 'cd /d D:\你的仓库\sovereign-ai-repo && git pull'
```

远程 ask 示例（路径按你机器改）：

```bash
ssh deploy 'cd /d D:\你的仓库\sovereign-ai-repo && .\.venv\Scripts\python.exe -m sovereign_ai.ask "每批尺寸抽检至少几件？"'
```

### 4.1 家里连不上 Deploy？一句边界

有的路由器 **客户端隔离**，有的环境 **SSH 到内网机被中间设备掐握手**——表现为 TCP 22 能连、**banner / KEX 失败**。这不影响 **GitHub SSH pull**（走 `github.com`）。

务实分工：

- **代码同步：** Deploy 上 `git pull`（GitHub SSH），或 Dev **`git push`** + Deploy pull，**不必**强求 WSL→Deploy。
- **06 浏览器：** 人在 Deploy 前用 **`127.0.0.1:8787`** 即可（下一篇）；隧道是加分项。

文中不展开公司 **COOP 生产机** SSH——那是另一条线，与 sovereign-ai 仓库无关。

---

## 五、为 06 铺路：隧道只转发本机端口

【图5 下正文】

06 会在 Deploy 起 **`serve.cmd`**，只监听 **`127.0.0.1:8787`**（chroma、Ollama 仍在 Deploy）。

若 **第五节 optional 的 `ssh deploy` 已通**，笔记本可本地转发（Deploy 上先跑着 serve）：

```bash
ssh -N -L 8787:127.0.0.1:8787 deploy
```

浏览器访问 **`http://127.0.0.1:8787`**——数据仍不离开 Deploy 磁盘，只是把 **本机回环端口** 映到你笔记本。

没通 SSH 也没关系：**06 整篇可在 Deploy 本机浏览器跟做**；隧道写在 05 只为少重复概念。

---

## 五·排障速查（05 当天常见）

| 现象 | 查什么 |
|------|--------|
| `ssh -T git@github.com` 失败 | 公钥是否贴对账户；公司网是否拦 22 到 GitHub（换 HTTPS+doctor 或手机热点试） |
| `git pull` SSH 仍 Permission denied | Deploy 用的是否为 **GitHub 那把** key；可配置 `~\.ssh\config` 对 `github.com` 指定 `IdentityFile` |
| WSL `ssh deploy` 超时 | IP 是否变、Wi‑Fi 隔离、Deploy 是否睡眠 |
| KEX closed / banner 超时 | 多为 **路径没到真 sshd** 或局域网策略；退回到 **GitHub SSH + 本机操作 Deploy** |
| 远程 `ask` 报 chroma 空 | Deploy 上先 `ingest`，与 SSH 无关 |

---

## 六、本篇验收

- [ ] `git remote -v` 为 `git@github.com:…`，`git pull` 稳定  
- [ ] （推荐）跑过 `deploy-git-doctor.cmd` 知道 HTTPS 备选  
- [ ] （可选）WSL `ssh deploy` 能 `git pull` 或远程 `ask`  
- [ ] （可选）理解 `ssh -L 8787:127.0.0.1:8787` 与 06 的关系  

---

## 七、下一篇预告（06）

**主权 AI-06｜本机浏览器问答**

FastAPI + 单页、`serve.cmd`、`eval` 固定题回归；仍 **127.0.0.1**。细节与截图见 `006-formal-corpus.md`。

---

## 附录：给编辑器的元信息

| 项 | 建议 |
|----|------|
| **标题** | 主权 AI-05：Deploy 用 SSH——先稳 pull，再连机器与打隧道 |
| **摘要（54 字内）** | GitHub 改 SSH origin；doctor 救 HTTPS；可选 WSL 连 Deploy 与 -L 隧道。 |
| **封面文案** | 「443 通 pull 挂 → git@github.com」 |
| **外链** | https://github.com/61403662/sovereign-ai （`docs/runbook.md` § Git pull fails / SSH） |

---

## 配图 shot list

| 编号 | 内容 | 怎么做 |
|------|------|--------|
| 封面 | Git remote SSH vs 黑框 pull 成功 | 终端拼贴 |
| 图1 | 05 在 06 前对照表 | 表格导出 |
| 图2 | `ssh -T` + `git remote -v` + `git pull` | Deploy 实拍，无内网 IP |
| 图3 | `deploy-git-doctor.cmd` 摘要输出 | 打码代理行 |
| 图4 | WSL `Host deploy` + `ssh deploy hostname` | 打码 IP |
| 图5 | 隧道示意图（笔记本→SSH→Deploy 127.0.0.1:8787） | 手绘/PPT，无真实 IP |

---

## 发表前自查

- [ ] 无公司 COOP 节点 IP、无生产主机名  
- [ ] 无 `ghjv84`、无未打码家庭公网细节  
- [ ] 区分 **github.com SSH** 与 **Deploy LAN SSH** 两节标题清晰  
- [ ] 06 的 serve/eval **不重复长步骤**，只预告 + 隧道一句  