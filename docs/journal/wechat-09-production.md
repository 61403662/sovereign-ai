# 主权 AI-09 公众号制作清单（内部）

母稿：`009-formal-corpus.md`

## 元信息

| 项 | 建议 |
|----|------|
| 标题 | 主权 AI-09：私有 CSV 灌进 BOM 库——和文档一样不进 Git |
| 摘要 | CSV 只更新本机 SQLite，不是第三路由；private 目录 gitignore，导入后 eval 仍 10/10。 |
| 封面 | `assets/sovereign-ai-09-cover-v1.jpg`（与 03–08 系列版式） |

## 核心信息（防读者误解）

- **必读一句**：CSV **不直接问答**，只 **灌进 fan_bom.db**；ask 仍 **SQL**。  
- 与 **data\raw** 对称：**私有真数不进 Git**。

## 实拍优先

1. `dir data\private\fan\csv` + 五文件（路径可打码盘符）  
2. `bom-import-private.cmd` 成功行  
3. `eval-all` 10/10  
4. `ask` [route:sql] + 26.7  
5. **加分**：改 `supplier_offer.csv` 一行 → re-import → 新合计  

## 跟做最短路径

```powershell
git pull
New-Item -ItemType Directory -Force data\private\fan\csv
Copy-Item data\samples\fan\csv\*.csv data\private\fan\csv\
.\scripts\bom-import-private.cmd
.\scripts\eval-all.cmd
.\scripts\ask.cmd "做一台 XF-120 材料费多少钱？"
```

## 发表前勾选

- [ ] 全文未出现真实客户/报价  
- [ ] 未误传 private 目录截图到公网  
- [ ] 图1 讲清 CSV≠第三路由  
- [ ] 文末 GitHub 一次  