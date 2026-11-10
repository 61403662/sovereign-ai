# 主权 AI-01：环境构建（journal 占位）

公众号正文在本地撰写；入库前请做 **脱敏**（无内网 IP、无真实用户名路径）。

## 本篇要点

- Dev（WSL）写代码，Deploy（Windows + Ollama）跑模型与私有数据，GitHub 只同步代码与样例。
- Deploy：清 C 盘空间、`OLLAMA_MODELS` 指向大容量盘、拉取 7B 对话 + embed 模型、`models.yaml` 定档 B（8GB VRAM）。
- Dev：`git`、`gh`、Python；可不装 Ollama。

## 插图

发表用图见 Cursor 项目 `assets/` 下四张 JPG；图注说明见手记插图清单。

## 下一篇预告

Step 5 后：本仓库公开链接；Phase 1  ingest + 最小 RAG API。
