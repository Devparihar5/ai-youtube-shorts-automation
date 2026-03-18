@echo off
echo ╔══════════════════════════════════════════════════════════╗
echo ║   YouTube Shorts Automation - Windows Setup              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [1/5] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Download from https://python.org
    pause
    exit /b 1
)

echo.
echo [2/5] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some packages failed to install
)

echo.
echo [3/5] Checking FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ╔═══════════════════════════════════════════════════╗
    echo ║  FFmpeg NOT FOUND!                                ║
    echo ║                                                   ║
    echo ║  Option 1: choco install ffmpeg                   ║
    echo ║  Option 2: Download from https://ffmpeg.org       ║
    echo ║            Extract and add to system PATH         ║
    echo ╚═══════════════════════════════════════════════════╝
    echo.
) else (
    echo FFmpeg found!
)

echo.
echo [4/5] Checking Gemini configuration...
echo.
echo ╔═══════════════════════════════════════════════════╗
echo ║  Gemini setup required                            ║
echo ║                                                   ║
echo ║  1. Visit: https://aistudio.google.com/apikey     ║
echo ║  2. Create a free API key                         ║
echo ║  3. Add GEMINI_API_KEY to your .env file          ║
echo ╚═══════════════════════════════════════════════════╝
echo.

echo.
echo [5/5] Creating directories...
if not exist "output" mkdir output
if not exist "assets" mkdir assets
if not exist "logs" mkdir logs
if not exist "config" mkdir config

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  Setup Complete!                                         ║
echo ║                                                          ║
echo ║  NEXT STEPS:                                             ║
echo ║  1. Get free Pexels API key: https://www.pexels.com/api/ ║
echo ║  2. Set up YouTube API (see README.md)                   ║
echo ║  3. Edit config/settings.py with your API keys           ║
echo ║  4. Add GEMINI_API_KEY to your .env file               ║
echo ║  5. Test: python main.py --mode test                     ║
echo ║  6. Dashboard: python dashboard.py                       ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
pause
