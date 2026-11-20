# 主权 AI-08 公众号制作清单（内部）

母稿：`008-formal-corpus.md`

## 元信息

| 项 | 建议 |
|----|------|
| 标题 | 主权 AI-08：使用人话来引用SQL数据 |
| 摘要 | DB 先算数，Ollama 只润色；一键对比模板与自然中文，eval 仍 10/10。 |
| 封面 | `assets/sovereign-ai-08-cover-v1.jpg`（同 03–07 系列版式） |

## 配图

| 图 | 文件 | 可实拍替换 |
|----|------|------------|
| 封面 | sovereign-ai-08-cover-v1.jpg | 左清单右口语 |
| 图1 | sovereign-ai-08-fig1.jpg | §一四步原则 |
| 图2 | sovereign-ai-08-fig2.jpg | sql-nl-compare |
| 图3 | sovereign-ai-08-fig3.jpg | yaml false/true ask |
| 图4 | sovereign-ai-08-fig4.jpg | eval 10/10 |

路径：`/home/ghjv84/.cursor/projects/home-ghjv84-falcon/assets/sovereign-ai-08-*`

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