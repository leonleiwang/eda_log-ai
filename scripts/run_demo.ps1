$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $root "src"
& "D:\python\python.exe" -m eda_log_ai.cli (Join-Path $root "samples\logs\spice_convergence.log")
