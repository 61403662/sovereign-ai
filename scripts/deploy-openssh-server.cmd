@echo off
REM Run as Administrator: right-click this file -> Run as administrator
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy-openssh-server.ps1" %*
pause