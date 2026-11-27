# 主权 AI-12 公众号制作清单（内部）

母稿：`012-formal-corpus.md`

## 元信息

| 项 | 建议 |
|----|------|
| 标题 | 主权 AI-12：复合答——一句里既要文档又要价钱 |
| 摘要 | 「同时」+ 规章词 + 询价词 → compound 两段答；13/13 不变。 |
| 封面 | `assets/sovereign-ai-12-cover-v1.jpg`（已生成） |

## 配图

| 图 | 文件 | 建议 |
|----|------|------|
| 封面 | sovereign-ai-12-cover-v1.jpg | 推文头图 |
| 图1 | sovereign-ai-12-fig1.jpg | 10 vs 12 |
| 图2 | sovereign-ai-12-fig2.jpg | 触发条件 |
| 图3 | sovereign-ai-12-fig3.jpg | **实拍 compound 输出优先** |
| 图4 | sovereign-ai-12-fig4.jpg | **实拍 13/13 + compound 1/1** |
| 图5 | sovereign-ai-12-fig5.jpg | 边界 |

## 实拍

1. ask compound 两句标题 + 26.7  
2. eval-all 13/13  
3. compound jsonl 1/1  
4. serve 路由 compound (rag + sql)  

## 最短跟做

```powershell
git pull
.\scripts\eval-all.cmd
.\scripts\ask.cmd "扇叶划痕能否让步接收？同时做一台 XF-120 材料费多少钱？"
.\.venv\Scripts\python.exe -m sovereign_ai.eval eval\compound_qa.example.jsonl
```