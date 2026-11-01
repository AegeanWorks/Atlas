@echo off
REM One-click Atlas start (Windows): double-click to serve and open the workspace.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File start.ps1
