# 主权 AI-03：最小 RAG，回答带上出处（草稿）

发表前脱敏；配图建议：ingest 进度、ask 输出含「引用来源」。

## 开篇

01 环境、02 GitHub 与 Deploy clone。本篇：一篇样例 md → Chroma → 提问 → **引用段落**。

## 流程

1. `data/samples/…` 复制到 Deploy `data/raw/`
2. `python -m sovereign_ai.ingest --reset`
3. `python -m sovereign_ai.ask "…"`

## 技术点（简述）

- 嵌入：`nomic-embed-text`（Ollama `/api/embeddings`）
- 对话：`qwen2.5:7b-instruct-q4_K_M`
- 向量库：`storage/chroma`（不进 Git）

## 本篇结果（发表时填写）

- [ ] ingest 条数
- [ ] 样例问答截图（打码路径/token）

## 下一篇预告

Phase 2：小风扇 BOM SQLite + 路由（算价走 SQL，规范走 RAG）。
