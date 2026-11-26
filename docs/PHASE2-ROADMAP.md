# Phase 2 roadmap — structured data + unified ask

Phase 2 is **not** “CSV support”. CSV is one **ingest** path into the same SQLite BOM store. The goal: **one `ask` entry**, reliable **SQL for numbers**, **RAG for documents**, regression via **eval-all**.

## Pillars (status)

| Pillar | Status | Notes |
|--------|--------|-------|
| **A. Schema & SQL core** | done | `schema/fan_bom.sql`, read-only queries, XF-120/200 |
| **B. Unified routing** | done + evolving | `[route: rag\|sql]`; mixed 检验+材料费 → SQL when price intent wins (**WeChat 10**) |
| **C. Data ingest** | done | `bom-init` (SQL seed), `bom-import` (sample CSV), `bom-import-private`, `SOVEREIGN_BOM_CSV_DIR` |
| **D. Natural language (SQL)** | done | `sql_nl_format`, `sql-nl-compare`; eval forces template |
| **E. Regression** | done | `eval-all` 7+6 (13 total), `expected_route`, `expected_contains_any` |
| **F. Local UI** | partial | `serve` shows `route`; SQL returns `intent` + `data` in JSON |
| **G. Multi-model / queries** | in progress | list models, XF-200 in eval; more intents as needed |
| **H. Enterprise connectors** | planned | read-only ODBC/API, no write-back; still single ask |
| **I. Hybrid / compound answers** | planned | e.g. “依据 SOP 能否让步 + BOM 价差” (RAG + SQL in one turn) |

## What we explicitly do *not* do in Phase 2 (yet)

- No cloud LLM for BOM numbers  
- No git push of `data/private/` or `storage/`  
- No replacement of Jenkins/COOP production DB  
- No automatic ERP sync (only manual import or future read-only connector)

## Deploy rhythm (after any Phase 2 change)

```powershell
git pull
# RAG changed:
.\scripts\ingest.cmd --reset   # if data\raw changed
# BOM changed:
.\scripts\bom-import-private.cmd   # or bom-init / bom-import
.\scripts\eval-all.cmd
.\scripts\ask.cmd "<one sql + one rag question>"
```

## Series mapping (WeChat)

| Article | Phase 2 focus |
|---------|----------------|
| 07 | Routing, two data sources, eval 7+6 |
| 08 | `sql_nl_format` (presentation, not口径) |
| 09 | Private CSV ingest (subset of pillar C) |
| 10 | Mixed **routing** (检验+材料费), fan eval L6, not compound answer |
| 11 | Local UI/API: `serve`, `intent` + `data` on SQL (pillar F) |
| 12+ | Compound RAG+SQL (pillar I), connectors (H) |