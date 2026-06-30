# Leiloaria Smart - One-Click Setup Script for PowerShell

Write-Host ""
Write-Host "========================================"
Write-Host "Leiloaria Smart - Setup"
Write-Host "========================================"
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/3] Python found:"
    Write-Host $pythonVersion
}
catch {
    Write-Host "ERROR: Python is not installed or not in PATH"
    Write-Host "Please install Python 3.8+ from https://www.python.org/"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Install dependencies
Write-Host "[2/3] Installing Python packages from requirements.txt..."
cd Grupo
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install packages"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Install Playwright browsers
Write-Host "[3/3] Installing Playwright browsers (this may take a few minutes)..."
playwright install
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Playwright browsers"
    Write-Host "Try running manually: playwright install"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "Setup Complete!"
Write-Host "========================================"
Write-Host ""
Write-Host "To start the pipeline, run:"
Write-Host "  cd Grupo"
Write-Host "  python main.py"
Write-Host ""
Read-Host "Press Enter to exit"
