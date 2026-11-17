# 主权 AI-07：一条入口、两路分流、两类数据源

发表前脱敏：内网 IP、Windows 用户名、真实主机名、未公开 plan 全名一律打码；截图保留 `[route: sql]` / `[route: rag]` 与「引用来源」或 `fan_bom.db` 说明即可。

## 开篇

01～04 把 **Ollama + 虚构语料** 建在 Deploy 本机；05 稳住 **pull / SSH**；06 加了 **`127.0.0.1:8787` 小页** 和 **`eval/qa.sample.jsonl` 七题回归**——清一色是 **翻 md、带引用** 的 RAG。

真实企业里，知识不只在 **文档**（PDF、Word、SOP、plan…），还有大量落在 **数据库** 里：BOM 行、报价、库存、工单状态。若问答只接 RAG，**「做一台 XF-120 型风扇材料费多少钱？」** 这类题只能让模型猜——而答案其实在 **BOM 和报价表** 里，应当 **可复算、可对账**。

Phase 2 要解决的就是：**一条问答入口，如何同时接「文档检索」和「结构化库」？** 企业里两类问法也常混在一起：

- **「每批尺寸抽检至少几件？」** → 规矩在 md / plan 里，要 **引用**，不能编。
- **「做一台 XF-120 型风扇材料费多少钱？」** → 数在库里，要 **SQL（或等价结构化查询）**，不能心算。

这一篇是 **Phase 2 的第一步**：仍是一个 **`ask` 入口**，背后自动选 **`rag` 或 `sql`**；样例用虚构风机 **XF-120** 和 SQLite **`fan_bom.db`**（不进 Git）。文末还会把 **eval 维护节奏** 说清楚：**文档七题 + 结构三题**，改 ingest 或 BOM 逻辑之后不易踩空。

**不要求**你把真 BOM 上传 GitHub；仓库里只有 **schema + 种子 SQL**，私有库仍在 `storage\`。

---

## 一、为什么价格不让大模型「直接答」

【图1 下正文】

| 题型 | 可信来源 | 这篇的做法 |
|------|----------|------------|
| 工艺 / 检验 / plan 段落 | `data\raw` 里的 md | **RAG**：检索 + 引用小节 |
| 清单行数 / 材料费 / 哪家供应商便宜 | 结构化表 | **SQL**：只读查询 SQLite |
| 两类混在一句里 | 易走错路 | 关键词 **优先 RAG**（检验、工艺、计划…），其余才看 BOM 意图 |

原则一句：**算钱的走库，讲规矩的走文档。** 模型可以润色措辞（可选配置），但 **数字以 DB 为准**。

---

## 二、统一 `ask`：终端里先看 `[route: …]`

【图2 下正文】

`python -m sovereign_ai.ask`（以及 `ask.cmd`、`serve` 背后的同一函数）会在答案前打印：

- **`[route: rag]`** — Chroma + Ollama，答案末尾有 **引用来源**（文件名 + `#小节`）。
- **`[route: sql]`** — `storage\sqlite\fan_bom.db`，无 md 引用；来源说明指向样例 BOM 库（非臆测）。

路由示意（不必背代码，跟做时对照即可）：

1. 问里带 **检验、工艺、计划、Scope** 等 → **强制 RAG**（哪怕出现型号）。
2. 否则若识别为 **列 BOM / 估材料费 / 比供应商价** 且库已初始化 → **SQL**。
3. 库不存在 → BOM 类问题会提示先 `bom-init`，不会假装查到数。

**手测四问（建议照抄）**

| 问题 | 预期 route | 你心里对的点 |
|------|------------|--------------|
| 每批尺寸抽检至少几件？ | rag | 答案含 **5**，引用检验样例 md |
| 扇叶划痕能否让步接收？ | rag | 走工艺/文档，不是 BOM 价 |
| XF-120 的 BOM 有哪些料？ | sql | 出现 **M-BLADE-ABS** 等料号 |
| 做一台 XF-120 材料费多少钱？ | sql | 合计约 **26.7** CNY（样例种子数据） |

浏览器 `serve` 返回 JSON 里也有 **`route` 字段**，可与 CLI 对照截图。

---

## 三、跟做：pull → 初始化 BOM 库 → 四问

【图3 下正文】

在 **Deploy PowerShell**（盘符按你机器改）：

**Step 1 — 拉代码**

```powershell
cd E:\sovereign-ai-repo
git pull
```

**Step 2 — 一次性建样例库**

```powershell
.\scripts\bom-init.cmd
```

成功后在 `storage\sqlite\fan_bom.db` 有虚构数据（该路径 **gitignore**，换机要重做本步）。

**Step 3 — 确保 RAG 仍可用**

若 `data\raw` 里仍有 03/04 检验或 plan 语料，且 chroma 未清空，可跳过 ingest；若刚换语料或 chroma 空：

```powershell
copy data\samples\incoming-inspection-sample.md data\raw\
.\scripts\ingest.cmd --reset
```

**Step 4 — 四问验收**

```powershell
.\scripts\ask.cmd "每批尺寸抽检至少几件？"
.\scripts\ask.cmd "扇叶划痕能否让步接收？"
.\scripts\ask.cmd "XF-120 的 BOM 有哪些料？"
.\scripts\ask.cmd "做一台 XF-120 材料费多少钱？"
```

每条看 **`[route: …]`** 与答案是否合理；SQL 两条可不出现 md 引用。

---

## 四、eval：文档七题 + 结构三题

【图4 下正文】

06 只跑了 **`eval/qa.sample.jsonl`（7 条，全 RAG）**。Phase 2 增加 **`eval/fan_qa.example.jsonl`（3 条，SQL 侧）**——料号、 **26.7**、最便宜供应商 **SUP-ALPHA / 2.8** 等写在 `expected_contains` 里。

**文档回归（要先 ingest）**

```powershell
.\scripts\eval.ps1
```

或显式：

```powershell
.\.venv\Scripts\python.exe -m sovereign_ai.eval eval\qa.sample.jsonl
```

**结构回归（要先 bom-init）**

```powershell
.\.venv\Scripts\python.exe -m sovereign_ai.eval eval\fan_qa.example.jsonl
```

发 07 前我建议两张终端：**7/7 PASS** + **3/3 PASS**。任一组 FAIL，退出码为 1，别急着截图发文。

JSONL 约定（与 06 相同，便于自己加题）：

- `question`：原句提问。
- `expected_contains`：答案里 **都要出现** 的子串（大小写不敏感）。
- `expected_source`：仅 RAG 题需要；对引用里的 **文件名** 对齐。
- SQL 题 **不写** `expected_source`；用 CLI 的 **`[route: sql]`** 肉眼再确认一眼更稳。

---

## 五、改完代码后的维护节奏（我用的顺序）

【图5 下正文】

把 05～07 串成一条清单，以后每篇文末也可照此验收：

1. **`git pull`**（SSH 或 HTTPS，与 05 一致）。
2. **语料变了吗？** 变则 `data\raw` 更新 → **`ingest.cmd --reset`**。
3. **换新机或删过 storage？** 跑 **`bom-init.cmd`**。
4. **Ollama 在吗？** `ollama list`；embed/chat 模型与 `config\models.yaml` 一致。
5. **`eval.ps1` → 7/7**，再 **`sovereign_ai.eval fan_qa.example.jsonl` → 3/3**。
6. 要演示 Web：**重启 `serve.cmd`**，浏览器一问 RAG、一问 SQL，看 `route` 与引用。

**不必每天全跑**：只改 SSH 文档可跳过 ingest；只改 BOM SQL 可只跑 fan 三题；改 **ask 路由或 rerank** 则两组都跑。

---

## 六、排障速查

| 现象 | 优先查 |
|------|--------|
| BOM 问法却 `[route: rag]` 且答不准 | 是否含 **检验/工艺/计划** 等 override 词；或 `fan_bom.db` 未建 |
| `[route: sql]` 但报库不存在 | 重跑 **`bom-init.cmd`** |
| SQL 对了，RAG 七题 FAIL | chroma 空 → ingest；Ollama embed 挂 |
| RAG 对了，fan 三题 FAIL | 种子数据被改过 → 对齐 jsonl 里的期望子串 |
| `git pull` 后行为仍旧 | 重启终端；Web 要重启 **serve** |

---

## 七、和 06 浏览器的关系

**没有换入口**：`POST /api/ask` 仍是 `ask_question()`。Difference 只是响应里多 **`route`**，SQL 时 **citations 为空**、文案说明来自样例库。

06 的安全边界不变：**仅 127.0.0.1**，默认无 SSO。BOM 库也在 Deploy 磁盘，不上传 GitHub。

---

## 八、本篇验收勾选

- [ ] `bom-init.cmd` 成功，`fan_bom.db` 存在  
- [ ] 手测四问 route 与答案符合上表  
- [ ] `eval.ps1` **7/7**，`fan_qa.example.jsonl` **3/3**  
- [ ] 可选：`serve.cmd` 上各问一句，UI 显示 `route`  
- [ ] 截图已脱敏  

---

## 九、下一篇预告（08）

可选方向（定稿前择一主线）：**SQL 答案自然语言润色**（`config/rag.yaml` 里 `sql_nl_format`，数字仍锁 DB）；或 **BOM CSV 导入 / 真表脱敏接入**。读者把 07 两套路由跑顺即可。

---

## 附录：给编辑器的元信息（定稿前改）

| 项 | 建议 |
|----|------|
| **标题** | 主权 AI-07：一条入口、两路分流、两类数据源 |
| **摘要（54 字内）** | 统一问答自动分 RAG 与 SQL；样例 BOM 库 + eval 文档七题与结构三题回归节奏。 |
| **封面文案** | 「RAG 讲规矩 / SQL 算账」或「7/7 + 3/3 PASS」 |
| **外链** | https://github.com/61403662/sovereign-ai （`docs/runbook.md` Phase 2 · eval） |

---

## 配图 shot list

| 编号 | 内容 | 怎么做 |
|------|------|--------|
| 封面 | RAG 文档径 vs SQL 数据库径 | `assets/sovereign-ai-07-cover-v1.jpg` 或同系列重绘 |
| 图1 | 「算钱走库 / 讲规矩走文档」对照 | 本稿 §一表导出 |
| 图2 | 四问 + `[route: …]` 终端 | Deploy 实拍 |
| 图3 | `bom-init.cmd` + 一条 sql 问 | 终端 |
| 图4 | eval 7/7 与 fan 3/3 各一张 | 可拼成一张图 |
| 图5 | 维护节奏 1～6 清单 | PPT 一页或本稿 §五 |