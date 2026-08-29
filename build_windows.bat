@echo off
REM Script per creare eseguibile Windows di FatturaForfettario
REM Richiede Python 3.10+ e le dipendenze installate

echo ========================================
echo Creazione eseguibile FatturaForfettario
echo ========================================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato nel PATH
    echo Installa Python da https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Verifica dipendenze...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installazione PyInstaller...
    pip install pyinstaller
)

pip show PyQt6 >nul 2>&1
if errorlevel 1 (
    echo Installazione PyQt6...
    pip install PyQt6
)

pip show fpdf >nul 2>&1
if errorlevel 1 (
    echo Installazione fpdf...
    pip install fpdf
)

echo.
echo [2/4] Pulizia build precedente...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [3/4] Creazione eseguibile con PyInstaller...
py -m pyinstaller --clean FatturaForfettario.spec

if errorlevel 1 (
    echo.
    echo ERRORE durante la creazione dell'eseguibile
    pause
    exit /b 1
)

echo.
echo [4/4] Completato!
echo.
echo L'eseguibile si trova in: dist\FatturaForfettario\FatturaForfettario.exe
echo.
echo Per creare un installer, puoi usare NSIS o Inno Setup
echo.
pause
