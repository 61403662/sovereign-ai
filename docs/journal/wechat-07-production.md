# 主权 AI-07 公众号制作清单（内部）

母稿：`007-formal-corpus.md`  
粘贴用纯文本：从母稿逐段复制（与 05–06 同版式；表可做成图1/图5 后再删表发往 mp）。

## 元信息

| 项 | 建议 |
|----|------|
| 标题 | 主权 AI-07：一条入口、两路分流、两类数据源 |
| 摘要 | 统一问答自动分 RAG 与 SQL；样例 BOM 库 + eval 文档七题与结构三题回归节奏。 |
| 封面 | `assets/sovereign-ai-07-cover-v1.jpg`（与 03–06 同系列：深蓝 + 橙点缀、等距风） |

## 配图

| 图 | 文件 | 可实拍替换 |
|----|------|------------|
| 封面 | sovereign-ai-07-cover-v1.jpg | RAG/SQL 分叉示意 |
| 图1 | sovereign-ai-07-fig1.jpg | §一对照表 |
| 图2 | sovereign-ai-07-fig2.jpg | 四问 + route 终端 |
| 图3 | sovereign-ai-07-fig3.jpg | bom-init + ask sql |
| 图4 | sovereign-ai-07-fig4.jpg | 7/7 与 3/3 eval |
| 图5 | sovereign-ai-07-fig5.jpg | pull→ingest→bom→eval 清单 |

生成稿路径（Cursor）：`/home/ghjv84/.cursor/projects/home-ghjv84-falcon/assets/sovereign-ai-07-*`

发表前实拍优先：图2、图3、图4（Deploy 终端全绿）。

## 脱敏

- 无内网 IP；`E:\` 路径可改为「你的仓库目录」正文表述，截图打码用户名  
- plan 真文件名打码；保留 `#小节` 与 `incoming-inspection-sample` 样例名即可  
- BOM 料号为虚构样例，可全文保留  

## 跟做依赖（Deploy）

- `git pull` 含 Phase 2 统一 ask + `bom-init.cmd` + `eval/fan_qa.example.jsonl`  
- 已 ingest 检验样例（06 同源）  
- Ollama 运行中  

## 发表前勾选

- [ ] `bom-init.cmd` 已跑  
- [ ] 手测四问 route 正确  
- [ ] `eval.ps1` 7/7 + `python -m sovereign_ai.eval eval/fan_qa.example.jsonl` 3/3  
- [ ] 可选：`serve.cmd` 浏览器 rag/sql 各一问  
- [ ] 文末 GitHub 链接一次  
- [ ] 预告 08（sql 润色或 BOM 导入，与当时仓库主线一致）  

## 粘贴 mp 时注意

- 代码块用公众号「代码」样式；PowerShell 里用 `ask.cmd` / `bom-init.cmd`（ExecutionPolicy）  
- 勿把 Markdown 表格原样粘贴；表做成图1、手测四问可改为编号列表  