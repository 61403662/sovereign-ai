# Deploy runbook (Windows)

Operations on the **deploy** machine. Code syncs from GitHub only—never push private `data/` to the remote.

## One-time layout

| Path | Purpose |
|------|---------|
| `E:\ollama\models` | Ollama weights (`OLLAMA_MODELS` user env) |
| `E:\sovereign-ai-repo\` | Git clone of this repo |
| `E:\sovereign-ai-repo\data\raw\` | Private documents (gitignored) |
| `E:\sovereign-ai-repo\storage\chroma\` | Vector index (gitignored) |
| `E:\sovereign-ai-repo\config\models.yaml` | Local config (copy from `models.example.yaml`) |

## Update code (`deploy-pull`)

PowerShell:

```powershell
cd E:\sovereign-ai-repo
.\scripts\deploy-pull.cmd
```

Or `git pull` if scripts are not updated yet.

If `.ps1` is blocked (**禁止运行脚本** / ExecutionPolicy), use the `.cmd` wrappers above (they call PowerShell with `-ExecutionPolicy Bypass` for that process only). Alternatively:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\deploy-git-doctor.ps1
```

## Git pull fails (Deploy · Windows)

**Symptom:** `Test-NetConnection github.com -Port 443` → `TcpTestSucceeded : True`, but `git pull` → `Failed to connect to github.com port 443 after 21000ms`.  
TCP is fine; **Git’s HTTPS (libcurl)** is failing—often proxy leftovers, HTTP/2, or SSL stack—not “GitHub down”.

### Step A — Doctor + safe HTTPS fixes

```powershell
cd E:\sovereign-ai-repo
.\scripts\deploy-git-doctor.cmd          # read-only checks
.\scripts\deploy-git-doctor.cmd -ApplyFixes   # unset proxy, HTTP/1.1, schannel, then pull
```

Manual equivalent:

```powershell
git config --global --unset http.proxy
git config --global --unset https.proxy
git config --local --unset http.proxy
git config --local --unset https.proxy
Remove-Item Env:HTTP_PROXY, Env:HTTPS_PROXY, Env:ALL_PROXY -ErrorAction SilentlyContinue
git config --global http.version HTTP/1.1
git config --global http.sslBackend schannel
git pull
```

Inspect **system** proxy (Admin PowerShell if needed):

```powershell
git config --list --show-origin | findstr /i proxy
git config --system --unset http.proxy
git config --system --unset https.proxy
```

If **Clash/V2Ray is running** and browser needs proxy, set Git to the **current** local port instead of unset:

```powershell
git config --global https.proxy http://127.0.0.1:7890
git config --global http.proxy http://127.0.0.1:7890
```

### Step B — Use SSH (often most stable on Deploy)

One-time on Deploy:

```powershell
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ed25519_github -N '""'
Get-Content $env:USERPROFILE\.ssh\id_ed25519_github.pub
```

Add the public key in GitHub → **Settings → SSH and GPG keys → New SSH key**.

```powershell
ssh -T git@github.com
cd E:\sovereign-ai-repo
git remote set-url origin git@github.com:61403662/sovereign-ai.git
git pull
```

**Verify SSH remote (after `git remote set-url`):**

```powershell
cd E:\sovereign-ai-repo
git remote -v
# origin  git@github.com:61403662/sovereign-ai.git (fetch/push)
git pull
git log -1 --oneline
```

### Step C — Emergency sync without Git on Deploy

When HTTPS/SSH both blocked temporarily, pull on **WSL Dev** and copy into the Deploy tree (`data\raw` and `storage\` are untouched):

```bash
cd ~/sovereign-ai && git pull
rsync -a --exclude data/raw --exclude storage/chroma \
  ~/sovereign-ai/ /mnt/e/sovereign-ai-repo/
```

Or copy only what changed, e.g. `sovereign_ai/ask/runner.py`.

### Step D — More detail for support

```powershell
$env:GIT_CURL_VERBOSE=1
git pull 2>&1 | Select-Object -Last 25
```

## Phase 1 — Python venv (one-time)

1. Install [Python **3.12** (64-bit)](https://www.python.org/downloads/windows/) (check **Add python.exe to PATH**).  
   **Avoid 3.13+ on Deploy** for now: `chromadb` / `numpy` may try to compile from source without Visual Studio.
2. From repo root:

```powershell
cd E:\sovereign-ai-repo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
pip install -e .
```

If `pip install -r requirements.txt` fails on **numpy** / **Meson** / **VS compiler**, your Python is too new (e.g. 3.15) or pip is building from source. Either install **Python 3.12** and recreate `.venv`, or (3.12 venv only) preinstall wheels:

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary :all: numpy httpx PyYAML
.\.venv\Scripts\python.exe -m pip install --only-binary :all: "chromadb>=0.5.23,<0.6"
.\.venv\Scripts\python.exe -m pip install -e .
```

3. Verify: `python -m sovereign_ai.ingest --help`

## Phase 1 — Sample RAG workflow

Copy the public sample into private raw (or add your own `.md`):

```powershell
copy data\samples\incoming-inspection-sample.md data\raw\
```

Ingest strips a leading YAML `---` frontmatter (Cursor `.plan.md` todos) before chunking so body headings are retrieved, not metadata. Each chunk prefixes the document/section title in the indexed text so natural-language questions hit the right section.

Ingest (build vectors; use `--reset` to rebuild collection):

```powershell
.\scripts\ingest.ps1 --reset
```

Ask lightly re-ranks hits when the question mentions 后端/前端/测试 (maps to `Backend Plan`, etc.). Must show **引用来源** at end; default `cite_k: 1` — only top hit after re-rank, same file as rank-1:


```powershell
.\scripts\ask.ps1 "每批尺寸抽检至少几件？"
```

Expect an answer citing `data/raw/incoming-inspection-sample.md` and section headings.

## Ollama smoke

```powershell
ollama list
curl http://127.0.0.1:11434
```

Chat:

```powershell
ollama run qwen2.5:7b-instruct-q4_K_M
```

Embed API (vectors, not chat):

```powershell
curl http://127.0.0.1:11434/api/embeddings -d "{\"model\":\"nomic-embed-text\",\"prompt\":\"hello\"}"
```

## Models config

If `config\models.yaml` is missing:

```powershell
copy config\models.example.yaml config\models.yaml
```

Edit only when changing tags or `ollama_base_url`.

## Security

- Keep Ollama on **127.0.0.1** unless you knowingly expose LAN for debugging.
- Back up `data/` and `storage/` locally; they are not on GitHub.

## SSH — GitHub from Deploy (summary)

| Step | Action |
|------|--------|
| 1 | `ssh-keygen -t ed25519 -f %USERPROFILE%\.ssh\id_ed25519_github` (empty passphrase ok on single-user Deploy) |
| 2 | Copy `.pub` → GitHub **Settings → SSH and GPG keys** |
| 3 | `ssh -T git@github.com` (first time: type `yes`) |
| 4 | `git remote set-url origin git@github.com:61403662/sovereign-ai.git` |
| 5 | `git pull` |

HTTPS doctor (`.cmd`) remains valid; SSH is optional but often more stable than HTTPS 443.

## SSH — Windows OpenSSH Server (WSL → Deploy)

Use when you want to **remote `pull` / `ask` from WSL** without sitting at the Deploy PC.

**One-time on Deploy (Admin PowerShell):**

```powershell
Get-WindowsCapability -Online | Where-Object Name -like "OpenSSH.Server*"
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
# Firewall: allow TCP 22 for Private network if prompted
```

**One-time on WSL** (`~/.ssh/config` — copy from `docs/ssh-wsl-config.example`, edit `HostName` / `User`):

```sshconfig
Host deploy
  HostName 192.168.x.x
  User YourWindowsUser
```

**Remote ask (example):**

```bash
ssh deploy 'cd /d E:\sovereign-ai-repo && .\.venv\Scripts\python.exe -m sovereign_ai.ask "你的问题"'
```

`git pull` over SSH to **GitHub** is separate from logging into **Deploy**; both use SSH keys but different hosts (`github.com` vs your LAN IP).

## Local ask UI (`127.0.0.1` only)

For **06** browser Q&A on Deploy (no public internet). Requires Ollama + indexed chroma.

```powershell
cd E:\sovereign-ai-repo
git pull
```

If **`ingest` / `ask` already work**, do **not** reinstall chromadb. Only add HTTP deps (avoids MSVC / `chroma-hnswlib` build):

```powershell
.\.venv\Scripts\python.exe -m pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.32.0"
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
.\scripts\serve.cmd
```

Fresh venv only: use Python **3.12**, then `pip install -r requirements.txt`, `pip install -e .`, then the two `fastapi`/`uvicorn` lines above—not `pip install -e ".[serve]"` on Windows unless you have **Build Tools**.

```powershell
.\scripts\serve.cmd
```

Open `http://127.0.0.1:8787`. **Do not** bind `0.0.0.0` without a deliberate LAN policy.

**From WSL (notebook) via tunnel** (after `Host deploy` works):

```bash
ssh -N -L 8787:127.0.0.1:8787 deploy
# Another terminal or browser on WSL: http://127.0.0.1:8787
```

Start `python -m sovereign_ai.serve` on Deploy first.

### Serve page loads but “提问” fails

1. **Leave the `serve.cmd` window open** while using the browser; closing it kills the API.
2. URL must be **`http://127.0.0.1:8787/`** (same host as uvicorn), not a saved HTML file or IDE preview on another port.
3. On Deploy, confirm CLI still works:

```powershell
.\.venv\Scripts\python.exe -m sovereign_ai.ask "测试"
ollama list
```

4. Test API directly:

```powershell
curl http://127.0.0.1:8787/health
curl -X POST http://127.0.0.1:8787/api/ask -H "Content-Type: application/json" -d "{\"question\":\"测试\"}"
```

5. After `git pull`, restart `serve.cmd` (static `index.html` is read from disk on each full page load).

## Deploy acceptance checklist (after `git pull`)

- [ ] `git status` clean (except untracked `models.yaml`, `data/raw`, `storage`)
- [ ] `pip install -r requirements.txt` if requirements changed
- [ ] `.\scripts\ingest.ps1 --reset` succeeds
- [ ] `.\scripts\ask.ps1` returns answer + 引用来源 for a sample question
