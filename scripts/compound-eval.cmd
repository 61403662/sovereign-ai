@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0compound-eval.ps1" %*