# 主权 AI-06 公众号制作清单（内部）

母稿：`006-formal-corpus.md`  
粘贴用纯文本：可对照本篇逐段复制（与 05 同版式，无 Markdown 表）。

## 元信息

| 项 | 建议 |
|----|------|
| 标题 | 主权 AI-06：本机浏览器问答——127.0.0.1 上的小界面 |
| 摘要 | Phase 1 加 FastAPI 页与 eval 七题回归；仅本机 8787，数据仍不出 Deploy。 |
| 封面 | `assets/sovereign-ai-06-cover-v1.jpg`（与 03–05 同系列风） |

## 配图（生成稿路径均在 Cursor assets）

| 图 | 文件 | 可实拍替换 |
|----|------|------------|
| 封面 | sovereign-ai-06-cover-v1.jpg | 左 CLI + 右浏览器 |
| 图1 | sovereign-ai-06-fig1.jpg | 对照表 |
| 图2 | sovereign-ai-06-fig2.jpg | serve.cmd + 127.0.0.1:8787 |
| 图3 | sovereign-ai-06-fig3.jpg | runbook 排障表或 curl health |
| 图4 | sovereign-ai-06-fig4.jpg | eval.ps1 7/7 PASS |
| 图5 | sovereign-ai-06-fig5.jpg | 浏览器答案+引用 |

发表前：Deploy `git pull` → `pip` fastapi/uvicorn（若未装）→ `serve.cmd` 截图；`eval.ps1` 实拍优先。

## 脱敏

- 仅 127.0.0.1:8787，无 0.0.0.0、无内网 IP  
- 引用行可打码 `data\raw` 完整路径，保留 `#小节`  
- 04 plan 真文件名打码

## 发表前勾选

- [ ] health + 浏览器一问 + eval 7/7（Deploy 实拍图更佳）  
- [ ] 文末 GitHub 链接一次  
- [ ] 预告 07 eval 维护节奏  