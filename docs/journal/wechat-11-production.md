# 主权 AI-11 公众号制作清单（内部）

母稿：`011-formal-corpus.md`

## 元信息

| 项 | 建议 |
|----|------|
| 标题 | 主权 AI-11：浏览器里还能看见「查库意图」 |
| 摘要 | 06 小页接 Phase 2；SQL 问返 route/intent/data；仍只监听 127.0.0.1。 |
| 封面 | `assets/sovereign-ai-11-cover-v1.jpg`（已生成） |

## 核心信息

- **本篇做**：`serve` + `/api/ask` JSON 里的 **`intent` / `data`**，页上 **`路由 · intent`**。  
- **本篇不做**：复合答（12+）；不绑 `0.0.0.0`、不加登录。

## 配图（已生成 + 实拍）

| 图 | 文件 | 建议 |
|----|------|------|
| 封面 | sovereign-ai-11-cover-v1.jpg | 推文头图 |
| 图1 | sovereign-ai-11-fig1.jpg | §一 |
| 图2 | sovereign-ai-11-fig2.jpg | §二 intent |
| 图3 | deploy-ai-11-rag-browser.png | **实拍优先** |
| 图4 | deploy-ai-11-sql-browser.jpg | **实拍优先** |
| 图5 | sovereign-ai-11-fig5.jpg 或 deploy-ai-11-eval-13-13.jpg | 复合答 / eval |

## 实拍优先（Deploy 已齐）

| 图位 | 文件（建议） | 内容 |
|------|----------------|------|
| 图3/4 RAG | `deploy-ai-11-rag-browser.png` | `路由: rag` + 5 件 + md 引用 |
| 图3/4 SQL | `deploy-ai-11-sql-browser.jpg` | `路由: sql · intent: estimate_cost` + 26.7 明细 |
| 回归 | `deploy-ai-11-eval-13-13.jpg` | `=== total 13/13 passed ===` |
| health | PowerShell 用 `Invoke-RestMethod http://127.0.0.1:8787/health`（`curl` 可能绑到 Invoke-WebRequest） |

## 跟做最短路径

```powershell
git pull
.\scripts\serve.cmd
# 浏览器 127.0.0.1:8787 — 两问
curl -s http://127.0.0.1:8787/health
.\scripts\eval-all.cmd
```

## 发表前勾选

- [ ] 与 06 衔接（不重复讲 SSH/隧道长文）  
- [ ] 写清 composite 未做  
- [ ] 截图无内网主机名  