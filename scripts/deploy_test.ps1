$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $root "src"

Write-Host "Running unit tests..."
& "D:\python\python.exe" -m pytest

Write-Host "Running CLI smoke tests..."
& "D:\python\python.exe" -m eda_log_ai.cli (Join-Path $root "samples\logs\spice_convergence.log") --json | Out-Null
& "D:\python\python.exe" -m eda_log_ai.cli (Join-Path $root "samples\logs\netlist_missing_subckt.log") | Out-Null
& "D:\python\python.exe" -m eda_log_ai.cli (Join-Path $root "samples\logs\license_failure.log") | Out-Null

Write-Host "Deployment smoke test passed."
