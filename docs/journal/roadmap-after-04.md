# 04 发表后的实现与写手记顺序（内部）

## 原则

- **先 SSH，后客户端**：pull 稳、能远程敲命令、能给 localhost API 打隧道，再做 Web 问答。
- **eval 后置**：四类题已手测通过；批量 eval 在 API/SSH 成形后更有用。

## 实现顺序（仓库）

| 步 | 内容 | 产出 |
|----|------|------|
| 1 | Deploy：`git remote` → SSH，`ssh -T git@github.com` | runbook 补充「一步验收」 |
| 2 | Deploy：OpenSSH Server + WSL `~/.ssh/config` Host deploy | `docs/runbook.md` § 远程操作 |
| 3 | 代码：`run_ask()` 返回结构化结果；`sovereign_ai/api` FastAPI `POST /ask`，`127.0.0.1` | `python -m sovereign_ai.serve` |
| 4 | 静态页或极简 HTMX；WSL：`ssh -L 8787:127.0.0.1:8787 deploy` | 06 文 + 截图 |
| 5 | `eval/run_qa.py` 读 `eval/qa.jsonl`（CLI 或 HTTP） | 07 或小节 |

## 公众号顺序

| 篇 | 主题 | 跟做成果 |
|----|------|----------|
| **05** | SSH：Git + 连 Deploy + 隧道概念 | pull 不再全靠 HTTPS 赌运气 |
| **06** | 本机小客户端 | 浏览器里 ask，仍无私有云 |
| **07** | 固定 10～15 问 + eval | 回归不散架 |

## 05 文建议结构（起草时可照此）

1. 为何 04 之后先 SSH 而不是先 Web（pull 是问答代码的前提）
2. GitHub Deploy key / 用户 key，`git@github.com:…/sovereign-ai.git`
3. 禁止 `.ps1` 与 SSH 无直接关系，一句带过 `.cmd`
4. OpenSSH 开关、防火墙、从 WSL 远程 ask 示例（打码主机名）
5. 预告 06：127.0.0.1 + `-L` 隧道示意（示意图即可，代码下一篇）

## 06 文前提

- 读者已完成 05 或至少在 Deploy 本机可 `ask`
- 不写 0.0.0.0 暴露；不写账号体系（Phase 2 再议）
