@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0clarify-eval.ps1" %*