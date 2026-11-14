@echo off
REM After OpenSSH Server is installed from Settings (no DISM). Run as Admin.
sc query sshd >nul 2>&1
if errorlevel 1 (
  echo sshd not found. Install OpenSSH Server in Settings - Optional features.
  exit /b 1
)
net start sshd
sc config sshd start= auto
echo.
echo sshd should be running. IPv4:
ipconfig | findstr /i IPv4
echo.
echo Add WSL pubkey to %%USERPROFILE%%\.ssh\authorized_keys
pause