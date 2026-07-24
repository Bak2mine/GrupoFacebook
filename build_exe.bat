@echo off
REM Build Leiloaria Smart as a standalone .EXE file

echo.
echo ========================================
echo Building Leiloaria Smart .EXE
echo ========================================
echo.

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo Building executable (this may take a minute)...

for /f "delims=" %%A in ('cd') do set "groupDir=%%A"
for %%A in ("%groupDir%\..") do set "parentDir=%%~fA"

cd /d "%parentDir%"

pyinstaller --name "Leiloaria Smart" ^
  --onefile ^
  --clean ^
  --distpath "%groupDir%\dist" ^
  --workpath "%groupDir%\build" ^
  --specpath "%groupDir%" ^
  --add-data "%groupDir%\data:data" ^
  --hidden-import=openpyxl ^
  --hidden-import=playwright ^
  --hidden-import=bs4 ^
  --console ^
  "%groupDir%\bootstrap.py"

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

cd /d "%groupDir%"

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.

REM Copy .exe to Grupo folder
if exist "dist\Leiloaria Smart.exe" (
    copy "dist\Leiloaria Smart.exe" "Leiloaria Smart.exe"
    echo Copied to: Grupo\Leiloaria Smart.exe
) else (
    echo Warning: Could not find source exe at dist\Leiloaria Smart.exe
)

echo.
echo Executable location:
echo   - Parent: ..\dist\Leiloaria Smart.exe
echo   - Grupo: .\Leiloaria Smart.exe
echo.
pause
