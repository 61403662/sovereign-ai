# 主权 AI-04：正式语料入库——用真实 Plan 验收私有 RAG

发表前脱敏：工单号、客户名、内网路径可换成「总 plan / 子 plan」示意；终端截图打码 `data\raw` 下的完整文件名。

## 开篇

01 装了 Ollama；02 用 GitHub 把仓库拉到 Deploy；03 用**虚构样例 md** 跑通 `ingest` + `ask`，并在文末打出引用来源。

这一篇换成本机 **`data\raw` 里的正式 Markdown**——我手头的几份工作 **plan**（总 plan + 若干子 plan，另有一份独立主题的 plan）。它们只留在 `E:\sovereign-ai-repo\data\raw`，**不进 GitHub**；索引在 `storage\chroma`，同样不进 Git。

仍没有 Web 界面。验收标准很简单：**问自己真在写的活，答案能对上 plan 里的章节，引用能点开对照。**

## 一、从样例到正式语料

【图1 下正文】

03 的样例 md 篇幅小、`ingest --reset` 后是 `chunks=6`，适合证明链路通了。正式 plan 一长，小节多，还有 YAML frontmatter 和子计划导航表——**检索会偏到「导航 / 缺口清单」**，模型也会更容易说「上下文未包含」。

所以我做了一次「换库」而不是在原样例上追加：

1. 清空或移出 `data\raw` 里不再要的 md（03 的检验样例我已删除）。
2. 把当前要用的 plan **整份复制**进 `data\raw`（可含子目录）。
3. **`ingest --reset`** 重建索引，避免删文件后库里留下孤儿 chunk。

左：只进 Git 的代码与 `data\samples`。右：只在本机的 `raw` + `chroma`。

## 二、建库：reset 与 chunk 规模

【图2 下正文】

换文档集时我固定带 `--reset`：

```powershell
cd E:\sovereign-ai-repo
.\.venv\Scripts\python.exe -m sovereign_ai.ingest --reset
```

我这一批：**5 个 md**（1 份独立 plan + 1 份总 plan + 3 份子 plan），索引大约 **`chunks=176`**。规模和你的 plan 长度、切块大小（`config/rag.yaml` 里 `chunk_size`）直接相关，不必和 6 对标。

`ingest` 当前会 **递归扫描** `data/raw` 下所有 `.md`；还没有「只索引某一个文件」的 `--path`。新增文件可以只跑 `ingest`（不带 reset），但**删文件、换一整套语料**时仍建议 reset。

切块时会把 **文档标题 + 章节名** 写进可被检索的文本，并把 Cursor plan 顶部的 YAML todo 区剥掉，减少「一堆 pending 任务」污染索引。

## 三、我用来验收的四类问题

【图3 下正文】

下面不是虚构检验规范，而是对照 **真实 plan 小节** 的自测题（发表时可把工单号改成「Plan-A / Plan-B」）。**期望**是一句话验收点，不是标准答案全文。

| 类型 | 示例问法（脱敏后可改写） | 期望 |
|------|--------------------------|------|
| 单 plan · 总目标 | 「某总 plan **目标与原则**一节说了什么？」 | 答 FAN/POD/PSI、ORG 规则等要点；引用 **`#目标与原则`**，不说「未直接提及」 |
| 单 plan · 技术 | 「某 plan 里 **FAN 的 assignee / ORG** 怎么定？」 | 命中总 plan 或 Jira 子 plan 对应段；引用合理 |
| 单 plan · 实现 | 「和 **Commit / SCT** 相关的 **FeaturePrService.getPodPsiFeatureKeys** 在哪说的？」 | 命中 commit-parser 或总 plan 拆单段 |
| **双 plan 对比** | 「Plan-A 和 Plan-B **分别管什么**？」 | A 讲 **Scope**（如 pipeline 展开边界）；B 讲 **总体入口 / 子计划**；引用 **两个文件各一节** |

第三类、第四类最容易翻车：长 plan 里 **Backend Plan** 和 **子计划导航** embedding 相近，需要仓库里对问法做一点 **重排**（后端 / 目标 / 对比意图）——读者跟做时用公开仓库拉最新 `main` 即可，不必自己改代码。

## 四、两道实拍级问答（可替换为你自己的终端截图）

【图4 下正文】

**（1）目标与原则**

问：`… 目标与原则一节说了什么？`  

答：应概括 backlog 同步、POD/PSI 独立 DoD、tag 映射、ORG 用 assignee/reporter 等（以你 plan 正文为准）。  

引用：`…plan.md#目标与原则`。

**（2）两个工单各管什么**

问：`Plan-A 和 Plan-B 分别管什么？`  

答：A 落在 **SKUNK pipeline 页 `+` 展开**、FI/FFB 与 SI 行为、**不**动 pipeline 计算等；B 落在 **AI-POD 总体计划**、子计划索引与需求收口。  

引用示例（双来源）：

- `…22162…#Scope`
- `…22163…#Plan 管理约束`（或 `#目标与原则`，以你库排序为准）

若脚注只有一份文件，见下面 **§五·问题 3**；更新代码并 pull 后，多 plan 对比应出现 **两条引用**。

## 五、换正式语料当天遇到的问题（现象 → 处理）

【图5 下正文】

这一节是 **04 实操当天** 的真实排障，不是理论。跟做时请保持：**代码用 `git pull` 跟仓库、语料只动本机 `raw`**；碰到问答怪象，**先 pull 再 ask**，仍不对再 `ingest --reset`。

### 5.1 问答 / 检索

| 现象 | 可能原因（人话） | 建议处理 |
|------|------------------|----------|
| 问「**目标与原则一节**」答「未包含」，引用却是 **#子计划导航** | 问法没对准「目标」意图，长 plan 里导航表 embedding 太近 | **`git pull` 到最新 `main` 后重问**（仓库已加强「目标与原则」问法）；仍错则确认该节已在 `raw` 且跑过 **`ingest --reset`** |
| 问「**两个 plan 分别管什么**」，只讲清一个，另一个被猜成「子计划」 | 「分别管」被当成「总目标」，检索挤满总 plan；另一份 plan 的 **Scope** 没进上下文前排 | **pull 最新后重问**；确认 **两份 md 都在 `raw`**；对比题要看 **#Scope** 与 **#Plan 管理约束**（或 #目标与原则） |
| 答案对了，**引用来源只有 1 个文件** | 旧逻辑只脚注「排名第一」那份 plan | **pull 最新**；多 plan 对比应看到 **两个文件各一节**（发表稿截图建议保留这一条） |
| 答对了，脚注章节和肉眼段落不完全一致 | 生成看了多段 top_k，脚注只列 1～2 段 | Phase 1 可接受；以 **答案 + 打开 md 搜章节** 为准 |
| 换过 `raw` 仍 cite 已删的样例 | 没 reset，Chroma 里留 **孤儿 chunk** | **`ingest --reset`** |
| PowerShell 里问题很长、引号乱 | 不是模型问题 | `$q = @'…长问题…'@` 再 `python -m sovereign_ai.ask $q` |

当天验收顺序我一般是：**pull →（语料变过则 reset ingest）→ 四类题各问一遍**。目标与原则、双 plan 对比都过了，再截图写公众号。

### 5.1.1 这些问答怪象，代码上是怎么修的（读者只需 `git pull`）

正式 plan 变长之后，问题多半不在「md 缺字」，而在 **ask 流水线**：向量检索 → 补充查询 → 合并重排 → 组上下文 → 生成 → 脚注。下面三块对应当天在仓库里改的 **Python**（模块 `sovereign_ai/ask/`，公开在 GitHub）。

**（1）问「目标与原则」，却命中子计划导航**

- **根因**：只有带「总体目标」等词才走「目标」检索；「目标与原则一节」没触发；重排也没压低「子计划导航」。
- **代码处理**：
  - 问句里出现「目标与原则」→ 标记为 `goals` 意图，并多打几条 **补充 embedding 查询**（专门找该节）。
  - **重排**抬高 `#目标与原则`，压低 `#子计划导航`；问句点名该节时再额外加权。
  - **系统提示**写明：上下文里已有该节时，不得回答「未直接提及」。
- **你要做**：`git pull` 后重问；**不必**改 `raw`、不必懂 rerank。

**（2）问「两个 plan 分别管什么」，只答一个、瞎猜子计划**

- **根因**：「分别管」曾被当成「讲总目标」，重排只抬总 plan 的「目标与原则」；另一份 plan 的范围在 **`Scope`**，挤不进上下文前排。
- **代码处理**：
  - 「管什么 / 分别管 / 对比」→ 单独 **`scope_compare` 意图**，不再并进 goals。
  - 重排抬高 **Scope / Plan 管理约束**，压低导航、缺口、Backend Plan 等细节段。
  - 问句里有两个 `COOP-*` 时：**加宽 top_k**、按工单 **补检索**（缺哪个 plan 的文件再 embed 一次）、合并后用 **`ensure_coop_coverage`** 保证每个 plan 至少几段排在上下文前面。
- **你要做**：`git pull`，确认 **两份 md 都在 `raw`**，再 ask。

**（3）双 plan 对比答对了，引用只有 1 个文件**

- **根因**：`cite_k: 1` 且「只脚注与第一名同源」→ 多 plan 题也只有一个 footer。
- **代码处理**：问句里识别 **≥2 个 COOP（或两篇 plan）** 时，脚注改为 **每个工单各取检索结果里该文件的第一节**（通常 Scope + 总 plan 管理约束）。
- **你要做**：`git pull` 后再跑对比题，应见 **两行引用来源**。

**（4）换 raw 仍 cite 已删样例**

- **根因**：ingest 增量不会删旧 chunk（**数据/Chroma**，不是 ask 代码）。
- **你要做**：`ingest --reset`（与 pull 无关）。

跟做者 **不需要 fork 改代码**；上述逻辑在 `rerank.py`、`runner.py`（系统提示）、`citations.py` 里，拉最新 `main` 即可。想对着看：`tests/test_ask_rerank.py`、`tests/test_ask_citations.py` 写了最小用例。

### 5.2 Deploy：`git pull` 与脚本

| 现象 | 可能原因（人话） | 建议处理 |
|------|------------------|----------|
| `Test-NetConnection github.com -Port 443` **成功**，`git pull` **21 秒超时** | Git HTTPS 栈（代理残留、HTTP/2 等），不是「网断了」 | **隔几分钟再 pull**（我有过连试几次才成功）；或跑诊断脚本（见下） |
| 想跑 `deploy-git-doctor.ps1`，提示 **禁止运行脚本** | Windows **ExecutionPolicy** 默认拦 `.ps1` | 用 **`.\scripts\deploy-git-doctor.cmd`** 或 `powershell -ExecutionPolicy Bypass -File .\scripts\deploy-git-doctor.ps1`；**不必**改整机策略也能用 |
| HTTPS 仍不稳 | 公司网络 / 代理长期折腾 | runbook：**HTTP/1.1 + schannel**（脚本 `-ApplyFixes`）；中长期 **Git 改 SSH**；紧急时 **WSL `git pull` + rsync 到 `E:\…`**（不覆盖 `data\raw`、`storage`） |

诊断与一键修复（仓库 `scripts/`，需先能 pull 到含脚本的版本）：

```powershell
cd E:\sovereign-ai-repo
.\scripts\deploy-git-doctor.cmd
.\scripts\deploy-git-doctor.cmd -ApplyFixes
```

`git pull` **不会**覆盖你的 `data\raw` 和 `storage\chroma`；怕的是 pull 不下来导致 **问答代码是旧的**，表上就会像 5.1 前几行那样翻车。

`.venv`、Python **3.12**、Ollama 前置条件同 03，不重复。

## 六、本篇结果

1. 正式 plan md 只在本机 `raw`，**`ingest --reset` → ~176 chunks** 量级跑通。
2. **目标与原则、双 plan 对比、技术拆单类**问题能答到对应小节，脚注可 **双来源**。
3. 已知边界：7B 仍可能啰嗦或掺「子计划」猜测；**导航 / 缺口** 段仍会干扰；无 Web、无自动评测报表。

## 七、下一篇预告（顺序已调整）

**主权 AI-05（预告）｜Deploy 用 SSH：拉代码、连机器、打隧道**

04  Day 还在跟 **HTTPS pull**、PowerShell 策略搏斗。下一篇先解决 **运维链路**，再谈界面：

1. **Git 改 SSH origin**（Deploy 上 pull 稳一点）
2. **（可选）Windows OpenSSH**：从 WSL 一条命令远程 `pull` / `ingest` / `ask`，不用坐 Deploy 前
3. **为 06 铺路**：本机 API 只绑 `127.0.0.1` 时，用 **SSH 本地转发** 在笔记本浏览器里问，数据仍只在 Deploy

**主权 AI-06（预告）｜本机问答客户端**

在 `run_ask` 外包一层 **FastAPI + 单页**（问题框、答案、引用列表），仍不接公网。依赖 05 的隧道或直接在 Deploy 上开浏览器。

**更后：07 或小节｜`eval/qa.jsonl` 固定问题集**  
CLI 或调 HTTP 批量回归，放客户端稳定之后。

公开仓库：<https://github.com/61403662/sovereign-ai>（`docs/runbook.md`、`docs/journal/003-minimal-rag.md` 衔接）

## 发表前自查

- [ ] 截图无内网 IP、无未脱敏工单全文
- [ ] `data\raw` 文件名打码或改成 Plan-A/B
- [ ] 不写客户定价、真实 FAN 项目代号（若敏感）
- [ ] 与 03 衔接：重复讲 ingest/ask 处尽量一句带过

## 插图清单（建议）

| 用途 | 建议内容 |
|------|----------|
| 封面 | raw 目录示意 +「不进 Git」 |
| 图1 | 样例 6 chunks vs 正式 ~176 chunks 对比 |
| 图2 | `ingest --reset` 终端（chunks 行打码路径） |
| 图3 | 四类问题表格（可排成图） |
| 图4 | 双 plan 问答 + **两条引用来源** 实拍 |
| 图5 | **§五 现象→处理** 表格截图，或 doctor.cmd / 成功 pull 二选一 |

04 配图（与 03 同目录，已生成示意图；**图4 发表建议换 Deploy 实拍双引用**）：

| 用途 | 文件 |
|------|------|
| 封面 | `…/assets/sovereign-ai-04-cover.jpg` |
| 图1 | `…/assets/sovereign-ai-04-fig1-corpus.jpg` |
| 图2 | `…/assets/sovereign-ai-04-fig2-ingest.jpg` |
| 图3 | `…/assets/sovereign-ai-04-fig3-four-types.jpg` |
| 图4 | `…/assets/sovereign-ai-04-fig4-dual-cite.jpg` |
| 图5 | `…/assets/sovereign-ai-04-fig5-troubleshoot.jpg` |

根目录：`/home/ghjv84/.cursor/projects/home-ghjv84-falcon/assets/`（Windows 拷到本机后插入公众号即可）。
