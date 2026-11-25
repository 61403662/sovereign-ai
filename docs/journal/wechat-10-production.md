# 主权 AI-10 公众号制作清单（内部）

母稿：`010-formal-corpus.md`

## 元信息

| 项 | 建议 |
|----|------|
| 标题 | 主权 AI-10：混合句怎么路由——检验里出现「材料费」仍走 SQL |
| 摘要 | 价/BOM 强词优先于检验词；eval fan 第 6 题锁 route；尚未同答拼 RAG+SQL。 |
| 封面 | `assets/sovereign-ai-10-cover-v1.jpg`（待生成，同 03–09 系列） |

## 核心信息（防读者误解）

- **本篇做**：混合句 **选 sql 还是 rag**（L6 金句）。  
- **本篇不做**：一次回答里 **同时** 给 SOP 引用 + 材料费（支柱 I，预告 11+）。  
- **07 读者**：若记得「检验→RAG」，本篇是 **优先级升级**，不是推翻「数字走库」。

## 实拍优先

1. `ask.cmd "XF-120检验时材料费多少钱？"` → **[route: sql]** + **26.7**  
2. 对比 `ask.cmd "XF-120 装配工艺螺栓扭矩多少？"` → **rag**  
3. `eval-all.cmd` 中 fan **L6 PASS** 或 **total 13/13**  
4. （可选）`serve` 返回 JSON 的 `"route": "sql"`  

## 跟做最短路径

```powershell
git pull
.\scripts\eval-all.cmd
.\scripts\ask.cmd "XF-120检验时材料费多少钱？"
.\scripts\ask.cmd "XF-120 装配工艺螺栓扭矩多少？"
.\scripts\ask.cmd "每批尺寸抽检至少几件？"
```

## 配图（待生成）

| 图 | 文件 | 可实拍替换 |
|----|------|------------|
| 封面 | sovereign-ai-10-cover-v1.jpg | 混合句分叉 |
| 图1 | sovereign-ai-10-fig1.jpg | §一 07→10 |
| 图2 | sovereign-ai-10-fig2.jpg | 路由四步 |
| 图3 | sovereign-ai-10-fig3.jpg | **建议换** eval L6 |
| 图4 | sovereign-ai-10-fig4.jpg | **建议换** 三问终端 |
| 图5 | sovereign-ai-10-fig5.jpg | 复合答未做 |

路径：`sovereign-ai/assets/sovereign-ai-10-*.jpg`

## 发表前勾选

- [ ] 文内写清「只选路、不复合答」  
- [ ] 三问手测与截图一致  
- [ ] eval 13/13 截图或文字  
- [ ] 文末 GitHub 一次  