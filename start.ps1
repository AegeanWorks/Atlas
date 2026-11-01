#Requires -Version 5.1
<#
One-click Atlas start (Windows): installs if needed, serves, opens the workspace.
Optional env: $env:MODEL_API_KEY (live Muse/SAM), $env:ATLAS_PORT (default 8765).
#>
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".\.venv\Scripts\python.exe")) { & "$PSCommandPath".Replace("start.ps1", "install.ps1") }
$port = if ($env:ATLAS_PORT) { $env:ATLAS_PORT } else { "8765" }
Start-Process "http://127.0.0.1:$port"
& ".\.venv\Scripts\python.exe" -m atlas.app --port $port
