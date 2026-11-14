@echo off
REM Install serve deps without rebuilding chromadb (Deploy Windows).
cd /d "%~dp0.."
.\.venv\Scripts\python.exe -m pip install "fastapi>=0.115.0" "uvicorn[standard]>=0.32.0"
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
echo OK. Run: scripts\serve.cmd