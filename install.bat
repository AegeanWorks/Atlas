@echo off
REM One-click Atlas install (Windows): double-click, no admin needed.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1
pause
