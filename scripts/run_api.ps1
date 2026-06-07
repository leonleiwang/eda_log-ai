$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $root "src"
& "D:\python\python.exe" -m uvicorn eda_log_ai.api:app --host 127.0.0.1 --port 8000
