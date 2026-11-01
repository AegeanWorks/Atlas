#Requires -Version 5.1
<#
One-click Atlas install (Windows): creates .venv, installs dependencies.
Run from the Atlas folder:  powershell -ExecutionPolicy Bypass -File install.ps1
#>
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv")) { python -m venv .venv }
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip | Out-Null
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Write-Host "Atlas installed. Start it with: .\start.ps1"
