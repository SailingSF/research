# Windows equivalent of setup_env.sh. Requires Python 3.14 on PATH (py launcher).
# Example system-wide install:
#   winget install -e --id Python.Python.3.14 --scope machine --override "/quiet InstallAllUsers=1 PrependPath=1"
$ErrorActionPreference = "Stop"

py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name space_datacenters_py314 --display-name "Python 3.14 (space_datacenters)"

Write-Host "Environment ready."
Write-Host "Activate with: .\.venv\Scripts\Activate.ps1"
Write-Host "Start notebook with: jupyter notebook"
