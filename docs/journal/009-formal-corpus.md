# 主权 AI-09：私有 CSV 灌进 BOM 库——和文档一样不进 Git

> Phase 2 全貌见仓库 **`docs/PHASE2-ROADMAP.md`**。本篇只覆盖 **支柱 C（数据进货）** 之一；路由/SQL 核心/润色/混合句等见 07、08、10。

发表前脱敏：CSV 无真客户/真报价；截图只用虚构料号 **XF-120**、**M-BLADE-ABS**；勿上传 `data\private\` 或 `storage\` 目录截图里的完整路径。

## 开篇

01～06 把 **本机 RAG** 与 Deploy 运维跑通。我们在 **AI-07** 做了一个规定：**算钱的走 SQL 库，问规格的走文档**；终端输出会提示实际路由 **`[route: rag]`** / **`[route: sql]`**。**08** 在数字仍来自 DB 的前提下只改「怎么说」（`sql_nl_format`），**`eval-all` 仍可 13/13**（7 题 RAG + 6 题 fan SQL）。

读者跟到 08 时，心里通常还有一个问题：

> 仓库里只有 **虚构 seed** 和 **`data\samples\...`**，我厂里 Excel / ERP 导出的 BOM、报价表 **怎么接进来？** 会不会又多出一套「CSV 问答」，和 SQL 打架？

**这一篇讲清楚：不会。**  
在 Phase 2 里，**问答的 Structured 口径只有 SQLite**；**CSV 只是「把表灌进库」的运维格式**，和 **`bom-init` 读 SQL seed** 是同一层的两种进货方式。  
真表放在 **`data\private\fan\csv\`**（整目录 **gitignore**），和 **`data\raw\`** 放私有文档是 **同一套主权逻辑**：**GitHub 同步代码与虚构样例，Deploy 本机保管真数。**

你在 Deploy 上若已跑通：

```text
bom-import-private.cmd → eval-all 13/13 → ask [route:sql] 26.7 / 型号列表
```

本篇就是把这条链 **写进系列手记**，并说明 **改 CSV、重建库、再验收** 的固定节奏。

---

## 一、先澄清：CSV 不是第三类数据源

【图1 下正文】

很多读者第一次看 `bom-import-private.cmd` 会以为：**是不是 CSV 也能直接问了？**  
不是。数据流只有一条：

```text
CSV 文件 ──导入──► fan_bom.db (SQLite) ──只读 SQL──► ask [route:sql] ──(可选)──► Ollama 润色
```

| 层次 | 是什么 | ask 会不会直接碰它 |
|------|--------|-------------------|
| **文档** | `data\raw\*.md` → Chroma | 会，走 **RAG** |
| **结构化库** | `storage\sqlite\fan_bom.db` | 会，走 **SQL** |
| **CSV** | 磁盘上的五个文本表 | **不会**；仅 **import** 时用 |

所以 **07 说的「两类数据源」没变**：**文档 + 库**；CSV 属于 **「库从哪更新」**，不是和 SQL 并列的第三路由。

三种 **建成/更新库** 的方式（任选，结果都进同一个 `fan_bom.db`）：

| 方式 | 命令 | 典型场景 |
|------|------|----------|
| SQL seed | `bom-init.cmd` | 最快跟做、与早期 07 文稿一致 |
| 样例 CSV | `bom-import.cmd` | 与 Git 里 `data\samples\fan\csv` 对齐 |
| **私有 CSV** | **`bom-import-private.cmd`** | **Excel 导出、脱敏真表、调单价做实验** |

**问答命令不变**：仍是 `ask.cmd`、`serve`，不会新增 `ask-csv.cmd`。

---

## 二、schema 与五张 CSV（列名要对齐）

【图2 下正文】

表结构在仓库 **`schema/fan_bom.sql`**（可提交）。导入脚本按 **固定文件名 + 表头** 写入，顺序：

1. `fan_model.csv` — 型号  
2. `material.csv` — 物料主数据  
3. `supplier.csv` — 供应商  
4. `bom_line.csv` — 单机用量  
5. `supplier_offer.csv` — 报价（含 `valid_from` / `valid_to`）

每张表 **必须出现的列**（缺了会 **报错退出**，避免 silent 错行）：

| 文件 | 关键列 |
|------|--------|
| fan_model.csv | model_code, name, revision |
| material.csv | material_code, name, unit |
| supplier.csv | supplier_code, name, contact |
| bom_line.csv | model_code, material_code, qty_per_unit |
| supplier_offer.csv | material_code, supplier_code, unit_price, currency, valid_from, valid_to |

样例数据在 **`data\samples\fan\csv\`**（进 Git）；**XF-120 材料费合计 26.7 CNY**、**XF-200** 等在库中均有虚构行，便于 **`fan_qa.example.jsonl` 六题**（BOM、材料费、最便宜供应商、型号列表、混合「检验+材料费」）对照。

**从 Excel 导出时建议：**

- 第一行 **英文列名** 与上表一致（与样例 CSV 相同）；  
- 另存 **CSV UTF-8**（Deploy 导入用 `utf-8-sig`，带 BOM 的 Excel 导出通常可用）；  
- 数字列勿夹千分位逗号；日期 `valid_from` 用 `YYYY-MM-DD`；`valid_to` 空表示仍有效。

---

## 三、私有目录：和 `data\raw` 同一套纪律

【图3 下正文】

| 路径 | Git | 放什么 |
|------|-----|--------|
| data\samples\... | 进仓库 | 虚构样例，读者可复现 |
| **data\private\fan\csv\** | **不进** | 你本机/Deploy 上的 **真表或脱敏副本** |
| data\raw\ | 不进 | 私有 SOP / plan（RAG） |
| storage\sqlite\fan_bom.db | 不进 | 导入 **生成** 的库 |
| storage\chroma\ | 不进 | 向量索引 |

**.gitignore 已包含 `data/private/`**，避免误 `git add`。  
公司合规上：即便脱敏，也 **不要** 把厂内 CSV 推到 GitHub；需要备份用 **公司网盘 / U 盘 / Deploy 镜像**，不走公开 remote。

可选：自定义目录而不改仓库树：

```powershell
$env:SOVEREIGN_BOM_CSV_DIR = "D:\exports\bom-daily"
python -m sovereign_ai.bom --import-csv $env:SOVEREIGN_BOM_CSV_DIR --reset
```

`bom-import-private.cmd` 则 **固定** 使用 `data\private\fan\csv\`（适合「我就放在仓库约定位置」）。

---

## 四、跟做：从样例复制到第一次私有导入

【图4 下正文】

**前提**：Deploy 已 Phase 1（ingest + eval 7 题曾绿）+ Phase 2（07/08 任一阶段摸过 `ask` / `eval-all`）。

```powershell
cd E:\sovereign-ai-repo
git pull

# 1. 建私有目录（仅第一次）
New-Item -ItemType Directory -Force data\private\fan\csv

# 2. 从样例复制（先保证 13/13，再改数做实验）
Copy-Item data\samples\fan\csv\*.csv data\private\fan\csv\

# 3. 导入（重建库；私有脚本内部带 --reset 语义见 runbook）
.\scripts\bom-import-private.cmd

# 4. 双轨回归（勿写 python -m sovereign_ai.eval.eval_all，无此模块）
.\scripts\eval-all.cmd

# 5. SQL 问答（08 若开了 sql_nl_format，会是口语；数字仍来自 DB）
.\scripts\ask.cmd "做一台 XF-120 材料费多少钱？"
.\scripts\ask.cmd "样例库里有哪些风机型号？"
.\scripts\ask.cmd "XF-120验收时材料费多少钱？"
```

**PowerShell 若禁止 `Activate.ps1`**：不必激活 venv；上面脚本已固定调用 `.\.venv\Scripts\python.exe`。等价命令：

```powershell
.\.venv\Scripts\python.exe -m sovereign_ai.eval --all
```

预期：

- **eval-all** → `7/7`（`qa.sample.jsonl`）+ `6/6`（`fan_qa.example.jsonl`），**total 13/13**  
- **ask** → `[route: sql]`，材料费含 **26.7**（或你改 CSV 后的新合计）；型号问句含 **XF-120**、**XF-200**  
- 引用行：**fan_bom.db**，不是 md

**故意改一个数（建议发文前自己做一次）：**  
用 Excel / 编辑器把 `supplier_offer.csv` 里某行 `unit_price` 微调 **0.1**，再跑 `bom-import-private.cmd` → 同一句 ask，合计应 **跟着变**；`python -m sovereign_ai.bom "…"` 模板段与合计一致——证明 **变的是库，不是模型瞎编**。

**Deploy 实测摘录（脱敏后可作图4/图7b 旁注）**

```text
=== total 13/13 passed ===

[route: sql]
XF-120验收时材料费是26.7元，包含了ABS扇叶、电源线1m、…
引用来源: storage/sqlite/fan_bom.db（样例 BOM，非模型臆测）

[route: sql]
样例库里有 XF-120 和 XF-200 两种风机型号，分别是小型桌面风扇 120mm 和 200mm。
引用来源: storage/sqlite/fan_bom.db（样例 BOM，非模型臆测）
```

（上例在 **`sql_nl_format: true`** 时出现口语；**eval** 仍按模板关键字判 **13/13**。）

---

## 五、和 07 / 08  Commands 对照（别记混）

【图5 下正文】

| 你想做的事 | 用什么 |
|------------|--------|
| 只想复现 Git 样例 | `bom-init.cmd` 或 `bom-import.cmd` |
| 用自己 CSV | `bom-import-private.cmd` |
| 调试 SQL 数字（无润色） | `python -m sovereign_ai.bom "…"` |
| 统一入口 + 路由 + 可选人话 | `ask.cmd` / `serve` |
| 对比模板 vs 润色 | `sql-nl-compare.cmd` |
| 文档 + SQL 一起回归 | `eval-all.cmd` |

**08 提醒**：`sql_nl_format: true` 时 **日常 ask 可读**；**eval-all 内部仍强制 SQL 模板判分**，所以你可以 **长期开润色** 且保持 **13/13**。

---

## 六、更新节奏：改 CSV 之后要跑什么

【图6 下正文】

把 05～09 收成一张 **Deploy 维护清单**：

1. **git pull** — 代码更新  
2. **语料变了？** → `ingest.cmd --reset`（只影响 RAG 七题）  
3. **BOM/报价 CSV 变了？** → **`bom-import-private.cmd`**（只影响 fan 六题 + SQL ask）  
4. **Ollama / models.yaml** — embed + chat 在跑  
5. **`eval-all.cmd`** — 必须 **13/13** 再截图写文  
6. **演示 Web** — `serve.cmd` 重启；`GET /health` 可看 **`bom_db: true`**、**`sql_nl_format`** 当前开关  

**不必每天全跑**：只改 md → 不必 import BOM；只改 CSV → 不必 ingest；**改了 `ask` 路由或 BOM 查询代码** → 两组 eval 都跑。

---

## 七、排障（CSV / 导入 / ask）

| 现象 | 优先查 |
|------|--------|
| import 报 missing columns | 列名与样例 CSV 第一行不一致 |
| import 成功 ask 仍是旧数 | 未再 import；或问的不是改价涉及的型号 |
| `[route: rag]` 却要价 | 少见：带 **材料费/多少钱** 等应走 SQL；若库未 `database_ready` 会回落 RAG |
| 型号列表答不出 XF 代号 | 问法须落 **LIST_MODELS**（如「有哪些风机型号」）；`git pull` 后重跑 eval |
| fan eval FAIL | 合计/料号与 `fan_qa.example.jsonl` 不一致（改 CSV 后要改 jsonl 或恢复样例数） |
| 口语答缺 CNY 但 eval 过 | 正常：eval 强制模板；日常问看 **数字** 即可 |
| 私有目录有文件仍找不到 | 路径须为 `data\private\fan\csv\` 五文件名齐全 |

---

## 八、边界与诚实说明（Phase 2 当下）

- **单库单 schema**：虚构 **风机 BOM**；尚未做多工厂、多币种、权限租户。  
- **导入是全量重建**（`--reset` 语义）：不是增量 CDC；厂内若需 **增量**，下一阶段再谈。  
- **CSV 不是安全沙箱**：恶意 CSV 只是文本；导入仍应在 **受信机器** 上做。  
- **直连企业 Oracle/SAP** 未做：09 的目标是 **「脱敏导出 → 本机库 → ask」** 的 **主权闭环**，不是接生产写库。

---

## 九、本篇验收勾选

- [ ] `data\private\fan\csv\` 有五张 CSV，**未** `git add`  
- [ ] `bom-import-private.cmd` 成功  
- [ ] `eval-all` **13/13**  
- [ ] `ask` 材料费 **`[route: sql]`**，合计与 CSV 一致  
- [ ] （可选）`样例库里有哪些风机型号？` 含 **XF-120**、**XF-200**  
- [ ] （可选）改价后 re-import，合计跟着变  
- [ ] （可选）`/health` 中 `bom_db: true`  
- [ ] 截图已脱敏  

---

## 十、下一篇预告（10）

可选主线：**混合句消歧**（一句里既有「检验」又有「BOM 价」）、或 **只读连正式库 / API**、或 **增量导入**——在 **私有 CSV → SQL → eval** 稳了之后写。

---

## 附录：元信息

| 项 | 建议 |
|----|------|
| **标题** | 主权 AI-09：私有 CSV 灌进 BOM 库——和文档一样不进 Git |
| **摘要** | CSV 只更新本机 SQLite，不是第三路由；private 目录 gitignore，导入后 eval 仍 13/13。 |
| **外链** | https://github.com/61403662/sovereign-ai （`data/samples/fan/csv/README.md`，`docs/runbook.md` Phase 2） |

## 配图 shot list

| 图 | 内容 |
|----|------|
| 封面 | Excel/CSV → 箭头 → SQLite → ask [route:sql]；旁路 data\raw → RAG |
| 图1 | 「两类数据源 + CSV 仅为进货」示意 |
| 图2 | 五表五文件名列名表 |
| 图3 | data\raw vs data\private vs storage 对照 |
| 图4 | bom-import-private + `=== total 13/13 passed ===` |
| 图5 | 命令对照小表 |
| 图6 | 维护节奏 1～6 |
| 图7 | 改 CSV 前后 ask 合计变化（实拍） |
| 图8 | ask 口语：型号列表 + 「验收时材料费」各一屏（08 联动） |