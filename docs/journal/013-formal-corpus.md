# 主权 AI-13：先澄清，再回答

> Phase 2 见 **`docs/PHASE2-ROADMAP.md`**。本篇：**双意图含糊时先澄清**（支柱 I）；**实现状态：Deploy 已验收**（clarify-eval 1/1，eval-all 13/13，compound-eval 1/1）。

## 开篇

**AI-07～11**：一问一路。**AI-10**：价赢单路。**AI-12**：用户说「同时」→ **compound**。

同事仍会问：**没有「同时」、又像既要规章又要价钱** 的句子。硬猜走 RAG、SQL 或 compound 都会挨骂。

**AI-13**：**先澄清，再回答**——系统先问用户要 **只要文档 / 只要价钱 / 两个都要**，第二轮再走已有 `ask` 管线；**不**用云端猜材料费。

---

## 一、澄清什么？

不是问技术细节，而是问 **这一次你要哪种结果**：

| 用户选 | 含义 | 第二轮 |
|--------|------|--------|
| A 只要文档 | 规程、让步、检验 | `route: rag` |
| B 只要价钱 | BOM、材料费 | `route: sql` |
| C 两个都要 | 规程 + 数字 | `route: compound`（拆句逻辑同 12） |

**不必澄清**：纯 RAG、纯 SQL、10 价赢、12 连接词 compound。

**宜澄清**：文档词 + 询价词 **并存**、**无连接词**、且 **不符合 10 价赢特例**。

---

## 二、和 10 / 12 的分工

- **10**：`检验+材料费` → **sql**（不问用户）  
- **12**：有 **同时/并且…** → **compound**（不问用户）  
- **13**：**其余双意图含糊** → **先澄清**  

---

## 三、交互形态（已落地）

- **CLI**：`[route: clarify]` + 选项；第二次 `ask --choice rag|sql|compound`  
- **serve**：JSON `clarify: true` + `options`；前端三按钮；第二次 POST 带 `clarify_choice` + 原问  
- **eval**：`eval/clarify_trigger.example.jsonl` + `scripts/clarify-eval.cmd`；**eval-all 跑时 `SOVEREIGN_CLARIFY=0`**  
- **状态**：浏览器会话内保存原问；**无**长对话记忆  

---

## 四、原则（不变）

- 澄清 **不算价、不编规章**  
- 第二轮仍 **RAG/SQL/compound** 既有实现  
- **eval-all 13/13**、**compound-eval 1/1**、**clarify-eval 1/1**  

---

## 五、下一篇（14）

无连接词 **自动** compound、只读外部库——在澄清 POC 稳后再议。

---

## 附录

| 项 | 建议 |
|----|------|
| **标题** | 主权 AI-13：先澄清，再回答 |
| **摘要** | 双意图含糊时先选文档/价钱/都要，再 second ask；仍本机 127.0.0.1。 |
| **公众号正文** | `docs/journal/013-wechat-body.txt` |
| **制作清单** | `docs/journal/wechat-13-production.md` |