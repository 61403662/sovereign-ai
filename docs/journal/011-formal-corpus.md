# 主权 AI-11：浏览器里的 SQL 问答

> 副题：同一 127.0.0.1 小页；走 SQL 时见 **route / intent / data**，走文档仍 **RAG**。

> Phase 2 全貌见 **`docs/PHASE2-ROADMAP.md`**。本篇对应 **支柱 F（本地 UI/API）**：在 **06 的 127.0.0.1 小页** 上接 Phase 2；**不是** 复合答（支柱 I，留给 12+）。

发表前脱敏：截图保留 `127.0.0.1:8787`、`route` / `intent` 字样即可；`data` 里勿露真实厂内字段扩展。

## 开篇

从 **AI-07** 起：**要钱、要 BOM 走 SQL 库，问规格走文档**，终端有 **`[route: rag]` / `[route: sql]`**。**08** 用大语言模型给 SQL 答案做润色；**09** 用本机 CSV 灌 BOM 库；**10** 处理混合句 **该走哪条路**。入口仍是一条 **`ask`**。

**AI-06** 已在 Deploy 上加了 **`http://127.0.0.1:8787`** 小页——当时主要是 **翻文档、看引用**。Phase 2 之后，同一页、同一个 **`POST /api/ask`**，在走 SQL 时会多两样东西：

- 页面上方状态行：**`路由: sql · intent: estimate_cost`**（举例）；  
- 响应 JSON 里的 **`data`**：行级材料费、型号列表等 **结构化结果**（给界面/联调用，不是给模型编的数字）。

这一篇：**怎么启动 `serve`、怎么各问一句 RAG 与 SQL、怎么在浏览器或 curl 里核对 `route` / `intent` / `data`**；并说明 **`/health`** 里的 **`bom_db`**、**`sql_nl_format`**。

---

## 一、为什么还要打开浏览器？

【图1】

**`ask.cmd` 主要在开发、验收中使用**；贴近实际使用时，往往是 **浏览器** 形式。页面上可直接看见 **路由、意图、回答、引用**；走 SQL 时还有 **intent** 与 **data**（仍 **127.0.0.1**，与 06 相同）。

---

## 二、SQL 答多了什么（相对纯 RAG）

【图2】

统一函数 **`ask_question()`**（CLI、`serve`、**eval** 共用）。**RAG** 路径大致仍是：`route: rag`、`answer`、`citations`。

**SQL** 路径在 `answer` 之外常见字段：

| 字段 | 含义 | 示例 |
|------|------|------|
| `route` | 固定 `sql` | sql |
| `intent` | BOM 意图枚举 | `estimate_cost`、`list_bom`、`list_models`、`cheapest_supplier` |
| `data` | 查询结果对象 | 合计、行明细、`models` 列表等 |
| `citations_text` | SQL 来源说明 | fan_bom.db 提示行 |

**口语答案**（`sql_nl_format: true`）只改 **`answer` 文本**，**不改 `data` 里的数**。与 **08** 一致。

---

## 三、小页上你能看到什么

【图3】

`sovereign_ai/serve/static/index.html` 在成功提问后：

- **`status`**：`路由: sql · intent: list_bom`（有 intent 才显示第二段）；  
- **`answer`**：与 CLI 同源的展示文本；  
- **引用区**：RAG 为 md 条目；SQL 常为 **fan_bom.db** 一行说明。

**`data` 默认不在页面上展开**（避免手机屏刷 JSON）。跟做建议：**F12 → Network → `/api/ask` → Response**，或下文 **curl**。

---

## 四、跟做：serve + 两问 + health

【图4】

**前提**：Phase 1 ingest 过；BOM 库已 `bom-init` / `bom-import-private`；**07～10** 手测或 **eval-all 13/13** 过。

```powershell
cd E:\sovereign-ai-repo
git pull
.\scripts\serve.cmd
```

浏览器打开 **`http://127.0.0.1:8787`**（勿关 PowerShell 窗口）。

**问 1（文档）**  
`每批尺寸抽检至少几件？`  
预期：状态 **`路由: rag`**，无 `intent`；答案含 **5**；引用检验 md。

**问 2（SQL）**  
`做一台 XF-120 材料费多少钱？`  
预期：状态 **`路由: sql · intent: estimate_cost`**；答案含 **26.7**；Response 里 **`data.total`** 等为数字来源。

另开 PowerShell（可选）：

```powershell
curl -s http://127.0.0.1:8787/health
```

预期 JSON 含 **`"bom_db": true`**；**`sql_nl_format`** 反映当前配置。

回归（关 serve 后亦可）：

```powershell
.\scripts\eval-all.cmd
```

应仍 **13/13**（UI 不改变 eval 判分逻辑）。

---

## 五、和 AI-10「复合答」的边界

【图5】

**11 仍是一条问、一条路、一个 JSON。** 不会在同一次 `/api/ask` 里返回 **「RAG 段落 + SQL data 拼成一篇」**——那是 **支柱 I**，留给 **12+**。

这里解决的是：**走 SQL 时，除了人话，还能看见机器可读的 `intent` / `data`**，方便你和同事确认 **「系统认的是估本还是列料」**。

---

## 六、排障

| 现象 | 优先查 |
|------|--------|
| 页面打不开 | `serve.cmd` 是否在跑；是否 `127.0.0.1:8787` |
| SQL 问仍 rag | 与 10 相同：路由、库是否 ready |
| 无 `intent` | 是否真走 sql；看 Network 整段 JSON |
| `bom_db: false` | 先 `bom-import-private.cmd` 或 `bom-init` |
| 口语与 data 不一致 | 以 **`data` / 模板段** 为准；润色只动 `answer` |

---

## 七、本篇验收勾选

- [ ] `serve` 本机可问  
- [ ] RAG 一题：`route: rag` + 引用  
- [ ] SQL 一题：`route: sql` + `intent` + `data` 在 JSON 中可见  
- [ ] `/health` 中 `bom_db: true`  
- [ ] `eval-all` **13/13**  
- [ ] 截图脱敏  

---

## 八、下一篇预告（12）

**复合答**（一句里既要 SOP 又要材料费，两路都跑再合并），或 **只读连外部库**（支柱 H）——在 **UI 能看清 intent/data** 之后再写更顺。

---

## 附录：元信息

| 项 | 建议 |
|----|------|
| **标题** | 主权 AI-11：浏览器里的 SQL 问答 |
| **摘要** | 06 小页接 Phase 2；浏览器问价钱见 intent/data；本机 127.0.0.1；eval 13/13。 |
| **外链** | https://github.com/61403662/sovereign-ai （`sovereign_ai/serve/app.py`，`docs/runbook.md` serve） |

## 配图 shot list

| 图 | 内容 |
|----|------|
| 封面 | 浏览器 + sql intent + JSON data 示意 |
| 图1 | CLI vs 浏览器 同一 ask_question |
| 图2 | intent 四枚举 + data 示例 |
| 图3 | 页面上方 路由·intent 状态行 |
| 图4 | 两问截图 + Network data |
| 图5 | 11 单路 vs 12 复合答对比 |