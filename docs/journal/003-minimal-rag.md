# 主权 AI-03：最小 RAG实现对私有文件问答

发表前脱敏；配图建议：流程图、ingest `6/6 chunks`、ask 输出含「引用来源」（打码路径）。

## 开篇

01 在部署机上装好了 Ollama；02 用 GitHub 把代码同步到 `E:\sovereign-ai-repo`。

这一篇做一件具体的事：**把 Markdown 放进本机私有目录 `data/raw`，建向量索引，对私有文件提问——尽量只依据检索到的段落回答，并在文末列出引用来源。**

还没有 Web 界面和 FastAPI，只有两条命令：`ingest` 和 `ask`。先把 **「有据可查的私有文件问答」** 跑通，比界面好看更重要。

## 一、这篇在解决什么问题

【图1 下正文】

这篇要解决的问题很直白：我对本机 `data/raw` 里的私有 Markdown 提问时，希望答案尽量来自文档，而不是模型随口编。

左半边是平时直接问大模型：它容易按训练印象答，也很难说清楚「依据原文哪一段」。右半边是最小 RAG：先把和你问题相关的段落检索出来，再交给本地 7B 组织成回答，并在文末标出来源（文件名和章节）。对我这种要对照规程、检验规范的人来说，后者才够用。

数据路径分工不变：

- **进 GitHub 的**：代码、`data/samples` 里的虚构样例、README
- **只在本机的**：`data\raw\` 里的真实/正式 md、`storage\chroma` 向量库、`config\models.yaml`

## 二、整体流程（Deploy 上）

【图2 下正文】

整条链路分成「建库」和「问答」两条线，对应仓库里两条命令。

上路是一次性（或换文档后重来）的 ingest：把 `data/raw` 下的 md 切成小块，用嵌入模型变成向量，写进本机 `storage/chroma`。下路是平时反复用的 ask：你的问题先去库里检索最相关的几段（top_k），再连同上下文交给对话模型生成答案，并在输出末尾打印引用来源。图里从 chroma 指向 ask 的虚线，就是「检索」这一步。

用到的组件分别是：嵌入用 Ollama 的 `nomic-embed-text`；对话用 `qwen2.5:7b-instruct-q4_K_M`；向量库是 Chroma，只留在部署机，不进 Git。下一节是在 Windows 上跑通时要注意的环境细节。

## 三、环境与前置（03 实操里踩过的坑）

【图3 下正文】

图上是一张跑通前的自检清单，我按 Deploy（Windows）上真实踩坑的顺序排的。

Python 务必用 **3.12** 建 venv（`py -3.12 -m venv .venv`）。我用 3.15 装过 `chromadb`，pip 会去编 numpy，机器上没有 VS 编译链就直接失败。venv 建好、`python --version` 确认是 3.12.x 之后，再 `pip install -r requirements.txt`。

Ollama 要先在跑：`ollama list` 里能看见对话模型和嵌入模型；浏览器或 `curl` 访问 `http://127.0.0.1:11434` 有响应。`config\models.yaml` 我手改过一回——YAML 少个冒号整段就挂，建议和仓库里的 `models.example.yaml` 逐项对齐。

第一次跟做可以把虚构样例拷进私有目录（图里第四行）：`copy data\samples\incoming-inspection-sample.md data\raw\`。正式用自己文档时，同样只放在 `data\raw`，不要进 Git。

## 四、两条命令

（公众号：命令可用正文代码样式；配图 `assets/sovereign-ai-03-fig4-terminal.jpg` 为示意，发表建议换自己终端实拍并打码路径。）

【图4 下正文】

跑通时我关心两件事：ingest 是否把 chunk 都吃进去（样例是 `6/6`），ask 是否在答案下面打出「引用来源」。图中是示意输出；你跟做时以本机终端为准，别忘了 `cd` 到仓库并用 `.venv` 里的 `python.exe`。

**1. 建索引（换文档集时建议带 `--reset`）**

```powershell
cd E:\sovereign-ai-repo
.\.venv\Scripts\python.exe -m sovereign_ai.ingest --reset
```

样例跑通时典型输出：`Indexed 6/6 chunks`，`Done. Collection='default', chunks=6`。

**2. 提问**

```powershell
.\.venv\Scripts\python.exe -m sovereign_ai.ask "每批尺寸抽检至少几件？"
```

## 五、三道样例题

（公众号插入配图：`assets/sovereign-ai-03-fig5-three-qa.jpg`）

【图5 下正文】

用虚构样例 md 试了三类情况：文档里明确写过的数（抽检 5 件）、写过的条件（500 V 耐压 1 分钟）、以及文档根本不存在的场景（火星风机——应说明无依据而不是硬编）。详细问答如下，引用行以你本机 ask 输出为准。

**（1）文档里有的——尺寸抽检**

问：每批尺寸抽检至少几件？  
答：每批尺寸抽检至少抽 **5 件**。  
文末有引用，其中应包含 **`#尺寸抽检`** 一类章节。

**（2）文档里有的——耐压**

问：耐压测试条件是什么？  
答：**500 V DC 下持续 1 分钟，无击穿**（对应「电气安全」）。

**（3）文档里没有的——无关问题**

问：火星上风机检验标准是什么？  
答：**上下文未包含相关信息**；样例只适用于小型直流风扇外购件检验。拒答好过瞎编。

## 六、关于「引用来源」列表

当前列出的是 **检索命中的 top_k 段落**（常为 5 段），不完全是「模型写答案时只用到的 1 段」。所以耐压题答案对了，来源里仍可能出现「外观检查」等章节名。Phase 1 接受这种粗糙；后续可只做 **最高分 1～2 段** 或让模型在正文里点名章节。

## 七、本篇结果

1. Deploy 上 **ingest / ask** 跑通，索引在 `storage\chroma`。
2. **样例 md** 可答「5 件抽检」「500V 耐压」，对无关问题能说明 **无依据**。
3. 回答末尾有 **`引用来源:`** 行，便于对照原文。

**还没做**：正式工作文档入库、用自己的问题验一轮；Web UI / FastAPI 再往后。

## 八、下一篇预告

**主权 AI-04（预告）｜正式语料入库：只问自己的 Markdown**

03 用的是仓库里的虚构样例。下一篇换成我手头的几份**正式 Markdown**——规程、检验要求这类平时真要翻的文件——只放在 Deploy 本机 `data\raw`，一样不进 GitHub。

打算记这几件事：换语料前怎么清理 `raw`、为什么必须 `ingest --reset`；真实篇幅下 chunk 数量大概什么样；我自己列的十几个问题里，哪些能答准、哪些该拒答、引用够不够对照原文。界面仍然不做，还是两条命令；等私有库问得顺手了，再谈 FastAPI 和浏览器里的 Web UI。

你若跟着做，提前想好：**哪些 md 可以进索引、哪些坚决不要进 `raw`**——进了索引就等于可能被检索进上下文。

公开仓库：<https://github.com/61403662/sovereign-ai>（`sovereign_ai.ingest` / `ask`，说明见 `docs/runbook.md`）

## 发表前自查

- [ ] 截图无内网 IP、无真实客户/价格
- [ ] 不贴完整 `models.yaml` 里的私密路径
- [ ] 与 01、02 衔接，不重复讲 Ollama 安装细节

## 插图清单（本机 assets）

| 用途 | 文件 |
|------|------|
| 封面 | `sovereign-ai-03-cover.jpg` |
| 图1 | `sovereign-ai-03-fig1-rag-compare-v2.jpg` |
| 图2 | `sovereign-ai-03-fig2-rag-flow.jpg` |
| 图3 | `sovereign-ai-03-fig3-env-prereq.jpg` |
| 图4 | `sovereign-ai-03-fig4-terminal.jpg`（示意，可换实拍） |
| 图5 | `sovereign-ai-03-fig5-three-qa.jpg` |

路径根目录：`/home/ghjv84/.cursor/projects/home-ghjv84-falcon/assets/`
