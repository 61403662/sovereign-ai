# Deploy runbook (Windows)

Operations on the **deploy** machine. Code syncs from GitHub only—never push private `data/` to the remote.

## One-time layout

| Path | Purpose |
|------|---------|
| `E:\ollama\models` | Ollama weights (`OLLAMA_MODELS` user env) |
| `E:\sovereign-ai\` | Git clone of this repo |
| `E:\sovereign-ai\data\raw\` | Private documents (gitignored) |
| `E:\sovereign-ai\config\models.yaml` | Local config (copy from `models.example.yaml`) |

## Update code (`deploy-pull`)

PowerShell:

```powershell
cd E:\sovereign-ai
git pull
```

## Ollama smoke

```powershell
ollama list
curl http://127.0.0.1:11434
```

Chat:

```powershell
ollama run qwen2.5:7b-instruct-q4_K_M
```

Embed API returns vectors (not chat text):

```powershell
ollama run nomic-embed-text "hello"
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
