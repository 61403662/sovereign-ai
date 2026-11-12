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
git pull
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

Ingest strips a leading YAML `---` frontmatter (Cursor `.plan.md` todos) before chunking so body headings are retrieved, not metadata.

Ingest (build vectors; use `--reset` to rebuild collection):

```powershell
.\scripts\ingest.ps1 --reset
```

Ask (must show **引用来源** at end; default `cite_k: 1` in `config/rag.yaml` — only top hit, same file as rank-1):


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

## Deploy acceptance checklist (after `git pull`)

- [ ] `git status` clean (except untracked `models.yaml`, `data/raw`, `storage`)
- [ ] `pip install -r requirements.txt` if requirements changed
- [ ] `.\scripts\ingest.ps1 --reset` succeeds
- [ ] `.\scripts\ask.ps1` returns answer + 引用来源 for a sample question
