# 主权 AI-06：本机浏览器问答——127.0.0.1 上的小界面

发表前脱敏：内网 IP、Windows 用户名、真实主机名一律打码；截图只保留 `127.0.0.1:8787` 与「引用来源」行。

## 开篇

01 在 Deploy 装 Ollama；02 用 GitHub 把代码拉到本机；03 用**虚构检验样例**跑通 `ingest` 与命令行 `ask`；04 把**自建 plan** 换进 `data\raw` 做正式检索；05 先把 **pull 与运维链路** 说清楚（GitHub SSH、doctor、可选连 Deploy）。

前五篇里，问答多半还在 **PowerShell 黑框**里完成。对得住答案，但不爱反复敲长命令；演示时也想要「像在用一个产品」——仍坚持 **数据不出本机、默认不上公网**。

这一篇在 **Deploy 本机**加一层极薄的 **Web**：浏览器打开 `http://127.0.0.1:8787` 提问，背后还是同一套 Ollama + Chroma + 带引用的 RAG。另外补一条 **`eval` 固定题回归**，改完 rerank 或 ingest 不至于答散架。

**不要求**家里笔记本 SSH 进 Deploy：人在 Deploy 电脑前跟做即可；**05 已写过** `ssh -L` 隧道，本篇末尾只作复习。

---

## 一、为什么先本机 127.0.0.1，而不是「内网 HTTPS」

【图1 下正文】

| 选择 | 这篇的做法 | 暂不做的 |
|------|------------|----------|
| 监听地址 | **仅 127.0.0.1:8787** | 不绑 `0.0.0.0` |
| 账号 | 无登录（单机自用） | 不接公司 SSO |
| 数据 | 问答走本机 chroma + Ollama | 不上传云端 API |
| 适用 | Deploy 本机浏览器 / 经隧道访问 | 企业全员 HTTPS（以后 Phase 2 再议） |

这和「主权」一致：**先在本机把体验闭环**，再谈权限与内网发布。

---

## 二、前提（你应该已经有）

1. Deploy 上 Phase 1 已通：`ingest` + `python -m sovereign_ai.ask "…"` 能出**中文答案**和**引用来源**。
2. Ollama 在 `http://127.0.0.1:11434`（默认即可）。
3. 代码在 `git pull` 后与 GitHub `main` 对齐（HTTPS 或 SSH 均可，与本文无关）。

若 03 样例还在，可先：

```powershell
cd D:\你的仓库\sovereign-ai-repo
copy data\samples\incoming-inspection-sample.md data\raw\
.\scripts\ingest.ps1 --reset
```

（盘符与路径按你机器改；`data\raw` 不进 Git。）

---

## 三、三步启动本地问答页

【图2 下正文】

**Step 1 — 拉代码**

```powershell
cd D:\你的仓库\sovereign-ai-repo
git pull
```

**Step 2 — 补 HTTP 依赖（不必重装 chromadb）**

已在跑通 `ingest` / `ask` 的 venv 上，只加 API 壳：

```powershell
.\.venv\Scripts\python.exe -m pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.32.0"
```

**Step 3 — 启动服务**

```powershell
.\scripts\serve.cmd
```

保持这个窗口**不要关**——关掉就等于关掉 API。

浏览器访问：**`http://127.0.0.1:8787/`**

在页面输入框试一句 03 老问题，例如：**「每批尺寸抽检至少几件？」**

预期：页面上有回答；底部或侧栏能看到 **引用**（文件名 + 小节），与 CLI `ask` 同源。

---

## 四、页面能问、但点「提问」失败——现象对照

【图3 下正文】

这是我在 Deploy 上真实踩过的几类情况，按顺序自查即可：

| 现象 | 优先查什么 |
|------|------------|
| 页面打不开 | `serve.cmd` 是否在跑；URL 是否是 **8787** 且 **127.0.0.1**（不是本地保存的 html 文件） |
| 能打开，提交后报错 | 另开终端：`python -m sovereign_ai.ask "测试"`；若 CLI 也挂，先修 Ollama/chroma，不是 Web 问题 |
| 日志里 Ollama **500** | `ollama list` / `ollama run` 你的 chat 模型；显存不够就换 7B 量化 |
| `git pull` 后 UI 仍旧 | **重启** `serve.cmd`；静态页每次全量刷新会读新 `index.html` |
| 健康检查 | `curl http://127.0.0.1:8787/health` 应返回 `ok: true` |

核心一句：**Web 只是 `ask` 的 HTTP 包装**；CLI 不通，Web 一定不通。

---

## 五、固定七题：eval 回归

【图4 下正文】

改 ingest、切块或 rerank 之后，我用手测四类题会疲。仓库带了 **`eval/qa.sample.jsonl`**（7 条，围绕检验样例 + 1 条「应拒绝瞎编」）。

在 Deploy、且已 ingest 的前提下：

```powershell
.\scripts\eval.ps1
```

或：

```powershell
.\.venv\Scripts\python.exe -m sovereign_ai.eval
```

终端会逐条打印 **PASS/FAIL**，最后汇总 `7/7 passed`。任一条 FAIL 退出码为 1——适合发文章前或 merge 后做一次「没砸」验收。

JSONL 里每条大致约定：

- `expected_contains`：答案里应出现的**关键词**（可多选，都要命中）。
- `expected_source`：引用里应对上的**文件名**（`data\raw` 与 `data\samples` 路径不同也没关系，按**文件名**对齐）。

样例题示例（节选，非全文）：

- 「每批尺寸抽检至少几件？」→ 应含 **5**，引用检验样例 md。
- 「火星上风机检验标准是什么？」→ 应倾向 **未包含 / 无法** 一类表述，避免胡编。

发 06 配图时，建议截一张 **全绿 PASS** 的终端，比单张浏览器更有「工程感」。

---

## 六、和命令行 `ask` 的关系

【图5 下正文】

- **同一函数**：`POST /api/ask` 内部调 `ask_question()`，与 `python -m sovereign_ai.ask` 一致。
- **仍在本机**：Ollama、chroma、私有 `data\raw` 都在 Deploy 磁盘；浏览器只是本机 HTTP 客户端。
- **04 的 plan 语料**：换过 `data\raw` 的同学，ingest 后同样在浏览器里问 plan 相关问题，引用应仍指向你的 md 与小节名（截图打码文件名即可）。

---

## 七、可选：笔记本上看 Deploy 的页面（隧道）

若你已完成 **05 的 WSL → Deploy SSH**（家里不通可跳过），可在笔记本开隧道，**仍只访问 127.0.0.1**：

Deploy 上先跑着 `serve.cmd`。WSL：

```bash
ssh -N -L 8787:127.0.0.1:8787 deploy
```

本机浏览器打开 `http://127.0.0.1:8787`。流量经 SSH 转发，**chroma 仍在 Deploy**，不把索引拷到笔记本。

家里 LAN / 公司 VPN 不通时：**直接在 Deploy 前用浏览器**即可，不影响本篇主线。

---

## 八、本篇验收勾选

- [ ] `serve.cmd` 常驻，`http://127.0.0.1:8787/health` 正常  
- [ ] 浏览器一问，答案 + 引用与 CLI 基本一致  
- [ ] `eval.ps1` 对样例库 **7/7 PASS**（或你自扩 jsonl 后全 PASS）  
- [ ] 全文截图无内网 IP、无未脱敏 plan 全名  

---

## 九、下一篇预告（07）

固定题表维护、改完代码后的节奏：**pull →（必要时）ingest --reset → eval → 截图**。若你加了 Phase 2（BOM / SQLite），eval 会再分「文档题」与「结构化题」两栏。

---

## 附录：给编辑器的元信息（定稿前改）

| 项 | 建议 |
|----|------|
| **标题** | 主权 AI-06：本机浏览器问答——127.0.0.1 上的小界面 |
| **摘要（54 字内）** | Phase 1 加 FastAPI 页与 eval 七题回归；仅本机 8787，数据仍不出 Deploy。 |
| **封面文案** | 「黑框 ask → 浏览器一问」或「7/7 PASS」 |
| **外链** | https://github.com/61403662/sovereign-ai （README + `docs/runbook.md` Local ask UI） |

---

## 配图 shot list

| 编号 | 内容 | 怎么做 |
|------|------|--------|
| 封面 | 左 CLI ask / 右浏览器问答 | PPT 一页或两张终端拼贴 |
| 图1 | 127.0.0.1 vs 0.0.0.0 对照表 | 本稿表导出 |
| 图2 | `serve.cmd` + 浏览器首页 | Deploy 实拍 |
| 图3 | 排障表或 health curl | 终端裁条 |
| 图4 | `eval.ps1` 7/7 PASS | 终端全绿 |
| 图5 | 浏览器答案 + 引用两行 | 打码路径，保留 `#小节` |