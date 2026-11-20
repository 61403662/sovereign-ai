@echo off
setlocal
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bom-import-private.ps1" %*
exit /b %ERRORLEVEL%