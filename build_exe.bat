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
cd ..
pyinstaller --name "Leiloaria Smart" ^
  --onefile ^
  --distpath "Grupo\dist" ^
  --workpath "Grupo\build" ^
  --specpath "Grupo" ^
  --add-data "Grupo\data:Grupo/data" ^
  --add-data "Post:Post" ^
  --hidden-import=openpyxl ^
  --hidden-import=playwright ^
  --hidden-import=bs4 ^
  --console ^
  Grupo\bootstrap.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

cd Grupo

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
