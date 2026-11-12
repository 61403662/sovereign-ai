@echo off
REM Runs doctor without changing machine ExecutionPolicy (Bypass for this process only).
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy-git-doctor.ps1" %*
