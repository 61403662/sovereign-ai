# 主权 AI-13 公众号制作清单（内部）

## 元信息

| 项 | 建议 |
|----|------|
| **标题** | 主权 AI-13：先澄清，再回答 |
| **摘要** | 一句像要两样又说不死时，先选文档/价钱/都要，再答；数走库、规矩走文档。 |

## 前置（发文前必须有）

- [x] API：`POST /api/ask` 首轮回 `clarify` + `options`，第二轮带 `clarify_choice`  
- [x] CLI：`--choice rag|sql|compound`；serve 三按钮  
- [x] `eval/clarify_trigger.example.jsonl` + `scripts/clarify-eval.cmd`  
- [ ] Deploy：**eval-all 13/13**、**compound-eval 1/1**、**clarify-eval 1/1**

```powershell
git pull
.\scripts\ask.cmd "扇叶划痕能否让步接收？做一台 XF-120 材料费多少钱？"
.\scripts\ask.cmd "扇叶划痕能否让步接收？做一台 XF-120 材料费多少钱？" --choice compound
.\scripts\clarify-eval.cmd
.\scripts\eval-all.cmd
.\scripts\compound-eval.cmd
```

## 系列衔接

- 10 价赢单路 · 11 intent/data · 12 同时 compound  
- **13 澄清** 只接「含糊双意图」，不替代 10/12  