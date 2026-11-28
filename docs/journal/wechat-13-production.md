# 主权 AI-13 公众号制作清单（内部）

母稿：`013-formal-corpus.md` · 可粘贴正文：`013-wechat-body.txt`

## 元信息

| 项 | 建议 |
|----|------|
| **标题** | 主权 AI-13：先澄清，再回答 |
| **摘要** | 一句像要两样又说不死时，先选文档/价钱/都要，再答；数走库、规矩走文档。 |
| **封面** | `assets/sovereign-ai-13-cover-v1.jpg`（待发/generate） |

## 前置（发文前）

- [x] Deploy：eval-all 13/13、compound-eval 1/1、clarify-eval 1/1  
- [x] CLI clarify + `--choice compound`  
- [x] serve 三按钮（用户已实拍 compound 浏览器）  
- [ ] 封面 + 配图上传公众号  

## 配图

| 图 | 建议内容 | 素材来源 |
|----|----------|----------|
| 封面 | 三岔路 / clarify 字样 | 生成或沿用系列风 |
| 图1 | `[route: clarify]` + 三选项终端 | Deploy 已跑通，可重截 |
| 图2 | 10 / 12 / 13 分工表 | 示意图或 ppt |
| 图3 | `--choice compound` 两段 + 26.7，或浏览器 compound | **已有浏览器实拍** + CLI |
| 图4 | clarify-eval 1/1 + eval-all 13/13 同屏 | 终端拼接 |
| 图5 | 边界：规程「未包含」+ BOM 仍有数 | compound 输出节选 |

## 文末预告（14，可原样贴）

下一篇：**无连接词自动 compound / 只读外部库** 放在 14+，澄清 POC 先收口。12「同时」、13「先选路」保留。

## 最短跟做

```powershell
git pull
.\scripts\ask.cmd "扇叶划痕能否让步接收？做一台 XF-120 材料费多少钱？"
.\scripts\ask.cmd "扇叶划痕能否让步接收？做一台 XF-120 材料费多少钱？" --choice compound
.\scripts\clarify-eval.cmd
.\scripts\eval-all.cmd
.\scripts\compound-eval.cmd
```

## 发表前勾选

- [ ] 正文与 `013-wechat-body.txt` 一致（发表前删「发前脱敏」段或缩为一句）  
- [ ] 截图无内网主机名  
- [ ] 12 文末预告已改成 13（若 12 已发可不动）  
- [ ] GitHub 链接可访问  