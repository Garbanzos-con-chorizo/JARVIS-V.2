# PowerShell script to install JARVIS-V.2 on Windows
# Creates a virtual environment and installs requirements

param([
    switch]$InstallPython
)

function Ensure-Python {
    try {
        python --version | Out-Null
    } catch {
        if (-not $InstallPython) {
            Write-Host "Python is not installed. Please run with -InstallPython to download and install." -ForegroundColor Yellow
            exit 1
        }
        $installer = "$env:TEMP\python-installer.exe"
        Write-Host "Downloading Python installer..."
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe" -OutFile $installer
        Write-Host "Installing Python..."
        & $installer /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    }
}

Ensure-Python

if (-not (Test-Path "venv")) {
    python -m venv venv
}

& venv\Scripts\pip install --upgrade pip
& venv\Scripts\pip install -r requirements.txt

Write-Host "Installation complete. Run 'python main.py' to start JARVIS." -ForegroundColor Green
