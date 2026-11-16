# 主权 AI-06：本机浏览器问答（127.0.0.1）

（公众号草稿 · 脱敏；先 Dev 写代码，Deploy `git pull` 跟做）

## 这篇讲什么

05 解决了 **代码怎么到 Deploy**（Git SSH / pull）；06 讲 **怎么在 Deploy 本机用浏览器提问**，仍不暴露公网。

## 前提

- Deploy 已完成 Phase 1：`ingest` + CLI `ask` 能出答案和引用
- Ollama 在 `127.0.0.1:11434`

## 跟做步骤（Deploy PowerShell）

```powershell
cd E:\sovereign-ai-repo
git pull
.\.venv\Scripts\python.exe -m pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.32.0"
.\scripts\serve.cmd
```

浏览器打开 **`http://127.0.0.1:8787`**，输入检验样例题（与 03 相同文档）。

## 固定 10～15 问（eval）

```powershell
.\scripts\eval.ps1
```

基于 `eval/qa.sample.jsonl`；改 ingest/rerank 后先跑通再截图写文。

## 笔记本上看 Deploy 页面（可选）

需 WSL 到 Deploy 的 SSH（05）；在家不通时用 **Deploy 本机浏览器** 或等办公室再试隧道：

```bash
ssh -N -L 8787:127.0.0.1:8787 deploy
```

## 安全一句话

默认 **`127.0.0.1`  only**；不绑 `0.0.0.0`，不接 SSO——企业内网 Phase 2 再议。

## 下一篇

07：eval 结果解读 + 维护节奏（pull → ingest → eval → 截图）。