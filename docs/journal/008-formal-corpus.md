# 主权 AI-08：使用人话来引用SQL数据

发表前脱敏：内网 IP、主机名打码；截图保留 `[route: sql]` 与 **26.7** 等数字即可（虚构样例）。

## 开篇

**07** 把 **一条 ask、两路分流** 跑通：文档走 **RAG**，BOM/报价走 **SQL**；`eval-all.cmd` **10/10** 时，说明路由和数字都还在。

但那篇里 SQL 答案多半是 **模板句**——对得上账，读着略硬。读者会问：既然已经有 **Ollama**，能不能像 RAG 一样，把查库结果 **说成自然中文**，又 **不把 26.7 改歪**？

这一篇就做这件事：**DB 仍算数，模型只润色**。开关在 `config/rag.yaml` 的 **`sql_nl_format`**；默认 **false**（与 07、eval 稳定一致）。打开后，统一 `ask` 在 `[route: sql]` 时会多一次本地 **chat**；失败则 **静默回退模板**。

---

## 一、原则：先 SQL，后 LLM

【图1 下正文】

| 步骤 | 核心技术 | 不许做什么 |
|------|----------|------------|
| 1 算数 | SQLite 只读 + `fan_bom.db` / BOM SQL | chat **不许估算**材料费 |
| 2 模板 | `verified_template` 清单答（`sovereign_ai.bom`） | **不许编造**料号 |
| 3 润色 | `sql_nl_format` + Ollama（仅 `query_facts` JSON） | **不许改** 26.7、CNY、供应商代号 |
| 4 回归 | `eval-all`（跑题时强制 SQL 模板判分） | **不许因口语**丢 `expected_contains` 关键字 |

一句话：**sql_nl_format 是「版式」，不是「口径」。**

---

## 二、对比跟做（建议截图的两张终端）

【图2 下正文】

前提：Deploy 已 **07+**：`bom-import.cmd`（或 `bom-init.cmd`）、`eval-all` 曾 **10/10**，Ollama chat 模型可用。

**方式 A — 一键对比（推荐发文截图）**

```powershell
cd E:\sovereign-ai-repo
git pull
.\scripts\sql-nl-compare.cmd "做一台 XF-120 材料费多少钱？"
```

同一窗口会打出两段：

1. **模板**（等同 `sql_nl_format: false`）  
2. **自然语言**（强制走 Ollama 润色）

核对：两段都应出现 **26.7**（或与你种子库一致）。若第二段与第一段完全相同，末尾会提示 **润色未生效**（查 `ollama list` / `config\models.yaml`）。

**方式 B — 改配置看统一 ask**

1. 先保持 `config\rag.yaml` → `sql_nl_format: false`：

```powershell
.\scripts\ask.cmd "做一台 XF-120 材料费多少钱？"
```

截图：**[route: sql]** + 模板答。

2. 改为 `sql_nl_format: true`，同一句再问一遍 → 截图自然中文版。

3. 跑回归（润色不应弄丢关键字）：

```powershell
.\scripts\eval-all.cmd
```

仍要 **10/10**；若 fan 第二题 FAIL，先 **关润色** 或看答案是否缺 **26.7**。

**临时开关（不改 yaml）**

```powershell
$env:SOVEREIGN_SQL_NL_FORMAT="1"
.\scripts\ask.cmd "材料 M-BLADE-ABS 哪家最便宜？"
$env:SOVEREIGN_SQL_NL_FORMAT="0"
```

---

## 三、`python -m sovereign_ai.bom` 仍只出模板

调试 SQL 逻辑、对照数字时，直连 BOM 模块 **不经过润色**：

```powershell
.\.venv\Scripts\python.exe -m sovereign_ai.bom "做一台 XF-120 材料费多少钱？"
```

与 **模板段** 一致；避免「到底是 SQL 错了还是 LLM 写花了」分不清。

---

## 四、浏览器里（可选）

`serve.cmd` 走的也是 `ask_question()`。`sql_nl_format: true` 后，页面 JSON 里 `route` 仍为 **sql**，仅 **answer** 文本变口语化。可与 07 一样在 **127.0.0.1:8787** 各截一张 false/true（不必两个端口，改配置后 **重启 serve**）。

---

## 五、排障

| 现象 | 查什么 |
|------|--------|
| 开了 true 仍是模板 | Ollama 是否挂；`compare` 是否提示回退 |
| 自然语言把 26.7 改坏 | 先关润色；用 `bom` 模块核对 DB；再收紧 prompt（仓库 `nl_format.py`） |
| eval 10/10 但读着怪 | 润色只影响展示；仍以 fan jsonl 关键字为准 |
| 只想演示对比 | 用 **`sql-nl-compare.cmd`**，不必反复改 yaml |

---

## 六、本篇验收勾选

- [ ] `sql-nl-compare.cmd` 同屏模板 + 自然语言，**26.7** 均在  
- [ ] `sql_nl_format: true` 后 `ask.cmd` 同问可读性更好  
- [ ] `eval-all.cmd` **10/10**  
- [ ] 截图无内网 IP  

---

## 七、下一篇预告（09）

**真 CSV 进私有目录**（gitignore）、或 **多库/多表路由**——在润色与 eval 稳了之后再接。

---

## 附录：元信息

| 项 | 建议 |
|----|------|
| **标题** | 主权 AI-08：使用人话来引用SQL数据 |
| **摘要** | DB 先算数，Ollama 只润色 SQL 答；一键对比模板与自然中文，eval 仍 10/10。 |
| **外链** | https://github.com/61403662/sovereign-ai |

## 配图 shot list

| 图 | 内容 |
|----|------|
| 封面 | 左模板/右口语，中间 DB+26.7 |
| 图1 | 四步原则表 |
| 图2 | `sql-nl-compare` 双段输出 |
| 图3 | yaml true/false 两次 ask |
| 图4 | eval-all 10/10 |