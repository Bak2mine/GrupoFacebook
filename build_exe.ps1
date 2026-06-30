# Build Leiloaria Smart as a standalone .EXE file

Write-Host ""
Write-Host "========================================"
Write-Host "Building Leiloaria Smart .EXE"
Write-Host "========================================"
Write-Host ""

# Check if PyInstaller is installed
try {
    pyinstaller --version >$null
}
catch {
    Write-Host "Installing PyInstaller..."
    pip install pyinstaller
}

Write-Host ""
Write-Host "Building executable (this may take a minute)..."

# Store current directory
$grupDir = Get-Location
$parentDir = Split-Path -Parent $grupDir

cd $parentDir

pyinstaller --name "Leiloaria Smart" `
  --onefile `
  --clean `
  --distpath "$grupDir\dist" `
  --workpath "$grupDir\build" `
  --specpath "$grupDir" `
  --add-data "$grupDir\data:Grupo/data" `
  --add-data "$parentDir\Post:Post" `
  --hidden-import=openpyxl `
  --hidden-import=playwright `
  --hidden-import=bs4 `
  --exclude-module=playwright.async_api `
  --console `
  "$grupDir\bootstrap.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "Build Complete!"
Write-Host "========================================"
Write-Host ""

cd $grupDir

# Copy .exe to Grupo folder for easy access
$sourceExe = "dist\Leiloaria Smart.exe"
$destExe = "Leiloaria Smart.exe"

if (Test-Path $sourceExe) {
    Copy-Item $sourceExe $destExe -Force
    Write-Host "Copied to: Grupo\Leiloaria Smart.exe"
} else {
    Write-Host "Warning: Could not find source exe at $sourceExe"
}

Write-Host ""
Write-Host "Executable location:"
Write-Host "  - Parent: ..\dist\Leiloaria Smart.exe"
Write-Host "  - Grupo: .\Leiloaria Smart.exe"
Write-Host ""
Read-Host "Press Enter to exit"
