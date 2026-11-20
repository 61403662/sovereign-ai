# 主权 AI-09 公众号制作清单（内部）

母稿：`009-formal-corpus.md`

## 元信息

| 项 | 建议 |
|----|------|
| 标题 | 主权 AI-09：私有 CSV 灌进 BOM 库——和文档一样不进 Git |
| 摘要 | CSV 只更新本机 SQLite，不是第三路由；private 目录 gitignore，导入后 eval 仍 13/13。 |
| 封面 | `assets/sovereign-ai-09-cover-v1.jpg`（与 03–08 系列版式） |

## 配图（已生成稿，可换 Deploy 实拍）

| 图 | 文件 | 可实拍替换 |
|----|------|------------|
| 封面 | sovereign-ai-09-cover-v1.jpg | CSV→SQLite→ask |
| 图1 | sovereign-ai-09-fig1.jpg | §一 两类数据源 |
| 图2 | sovereign-ai-09-fig2.jpg | 五 CSV 列名 |
| 图3 | sovereign-ai-09-fig3.jpg | §三 路径纪律 |
| 图4 | sovereign-ai-09-fig4.jpg | **建议换** eval 13/13 终端 |
| 图5 | sovereign-ai-09-fig5.jpg | 命令对照 |
| 图6 | sovereign-ai-09-fig6.jpg | 维护节奏 |
| 图7 | sovereign-ai-09-fig7.jpg | 改价实验；未做实验可删 |
| 图8 | sovereign-ai-09-fig8.jpg | **建议换** 两条 ask 实拍 |

路径（双份备份）：

- 仓库：`sovereign-ai/assets/sovereign-ai-09-*.jpg`
- Cursor：`/home/ghjv84/.cursor/projects/home-ghjv84-falcon/assets/sovereign-ai-09-*.jpg`

## 核心信息（防读者误解）

- **必读一句**：CSV **不直接问答**，只 **灌进 fan_bom.db**；ask 仍 **SQL**。  
- 与 **data\raw** 对称：**私有真数不进 Git**。

## 实拍优先

1. `dir data\private\fan\csv` + 五文件（路径可打码盘符）  
2. `bom-import-private.cmd` 成功行  
3. `eval-all` 终端 **`=== total 13/13 passed ===`**（含 L4「样例库里有哪些风机型号？」）  
4. `ask`：[route:sql] + 26.7（材料费）  
5. `ask`：[route:sql] + XF-120/XF-200（型号列表，08 开润色时可作人话截图）  
6. **加分**：改 `supplier_offer.csv` 一行 → re-import → 新合计  

## 跟做最短路径

```powershell
git pull
New-Item -ItemType Directory -Force data\private\fan\csv
Copy-Item data\samples\fan\csv\*.csv data\private\fan\csv\
.\scripts\bom-import-private.cmd
.\scripts\eval-all.cmd
.\scripts\ask.cmd "做一台 XF-120 材料费多少钱？"
.\scripts\ask.cmd "样例库里有哪些风机型号？"
```

**注意**：回归用 `eval-all.cmd` 或 `python -m sovereign_ai.eval --all`；没有 `sovereign_ai.eval.eval_all` 模块。PowerShell 执行策略拦 `Activate.ps1` 时不必激活 venv。

## 发表前勾选

- [ ] 全文未出现真实客户/报价  
- [ ] 未误传 private 目录截图到公网  
- [ ] 图1 讲清 CSV≠第三路由  
- [ ] 文末 GitHub 一次  