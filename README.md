# sovereign-ai

Personal **sovereign AI** stack: keep inference and private data on machines you control, while sharing **code and samples** on GitHub.

## What this repo is

- A greenfield project for **local RAG**, SQL-grounded Q&A, and optional fine-tuning—starting from **Ollama on a Windows deploy machine** and **development on WSL**.
- **Not** a hosted SaaS: default APIs bind to `127.0.0.1`.

## Dev vs deploy

| Role | Typical host | Responsibilities |
|------|----------------|------------------|
| **Dev** | WSL2 | Edit code, tests, CI, docs/journal |
| **Deploy** | Windows + NVIDIA GPU | Ollama, models, `data/`, vector DB |
| **GitHub** | Remote | Source, examples, runbooks—**no private BOM/docs** |

```
Dev (WSL)  --push-->  GitHub  --pull-->  Deploy (Windows)
                              x
                         (no private data)
```

Private files stay on Deploy under `data/` and `storage/` (gitignored).

## Quick start (deploy)

1. Install [Ollama](https://ollama.com/download) and set user env `OLLAMA_MODELS` to a disk with space (e.g. `E:\ollama\models`).
2. Pull models from `config/models.example.yaml` (Tier B: 8GB VRAM).
3. Copy `config/models.example.yaml` → `config/models.yaml` and adjust if needed.
4. Follow [`docs/runbook.md`](docs/runbook.md) for day-to-day pull and smoke checks.

## Quick start (dev)

```bash
git clone https://github.com/<you>/sovereign-ai.git
cd sovereign-ai
python3 -m venv .venv && source .venv/bin/activate
# Phase 1+ will add pip install -e .
```

You can develop without a local Ollama (mocks in tests).

## Config

- Committed: `config/models.example.yaml`, `config/rag.yaml`
- Local only: `config/models.yaml` (gitignored)

## License

MIT—see [LICENSE](LICENSE). Contributions welcome via [CONTRIBUTING.md](CONTRIBUTING.md).

## Journal

Learning notes for the public series live under `docs/journal/` (sanitized, no internal IPs or customer data).
