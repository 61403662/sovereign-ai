@echo off
REM One-time on DEV PC: ensure .ssh config exists (run from repo root).
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0dev-setup-ssh.ps1"
pause