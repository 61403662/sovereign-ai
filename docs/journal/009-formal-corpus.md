# 主权 AI-09：私有 CSV 进 BOM 库——不进 Git 的样例表

发表前脱敏：CSV 不含真客户名；截图仅虚构料号或打码。

## 开篇

08 把 **SQL 用人话说出来**（`sql_nl_format`）；07 把 **一条 ask、两路分流** 钉死。样例 BOM 一直在 **`data/samples/fan/csv/`**，适合跟做，但不是「你自己的表」。

Phase 2 下一步：**在 Deploy 本机**用 **同名五张 CSV** 灌进同一个 `fan_bom.db`，目录 **`data/private/fan/csv/`**，整棵 **gitignore**——和 `data/raw` 一样，**GitHub 只有 schema + 示例**。

---

## 一、五张表、固定文件名

【图1】

与 sample 相同：`fan_model.csv`、`material.csv`、`supplier.csv`、`bom_line.csv`、`supplier_offer.csv`。列名须一致；导入前会做 **表头校验**，缺列会报错而不是 silent 错数据。

---

## 二、跟做

```powershell
git pull
mkdir data\private\fan\csv
copy data\samples\fan\csv\*.csv data\private\fan\csv\
# 编辑 private 下 CSV（勿提交）
.\scripts\bom-import-private.cmd
.\scripts\eval-all.cmd
```

环境变量覆盖（可选）：`$env:SOVEREIGN_BOM_CSV_DIR="D:\exports\bom-csv"`

---

## 三、验收

- `ask.cmd` BOM 问法 `[route: sql]`，数字与 CSV 一致  
- `eval-all` **10/10**（eval 仍强制 SQL 模板判分）  
- `curl http://127.0.0.1:8787/health` → `bom_db: true`

---

## 下一篇

多型号 / 多库路由，或 RAG+SQL 混合句消歧——在私有 CSV 稳了之后写。