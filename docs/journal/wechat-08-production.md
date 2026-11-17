# 主权 AI-08 公众号制作清单（内部）

母稿：`008-formal-corpus.md`

## 元信息

| 项 | 建议 |
|----|------|
| 标题 | 主权 AI-08：SQL 也要说人话——sql_nl_format 与对比截图 |
| 摘要 | DB 先算数，Ollama 只润色；一键对比模板与自然中文，eval 仍 10/10。 |
| 封面 | `assets/sovereign-ai-08-cover-v1.jpg`（同 03–07 系列版式） |

## 实拍优先

1. `sql-nl-compare.cmd` 一问双答（图2）  
2. `sql_nl_format` false / true 各一次 `ask.cmd`（图3，可拼图）  
3. `eval-all.cmd` **10/10**（图4）  

## 跟做

```powershell
git pull
.\scripts\sql-nl-compare.cmd "做一台 XF-120 材料费多少钱？"
# 改 config\rag.yaml sql_nl_format: true 后再 ask + eval-all
```

## 发表前

- [ ] 两段答案都含 **26.7**  
- [ ] eval-all 10/10  
- [ ] 脱敏  