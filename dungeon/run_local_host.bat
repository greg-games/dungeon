@echo off
setlocal
cd /d "%~dp0"
set PORT=9000
if not exist build\web\index.html (
    echo No build found in build\web - run build_local_host.bat first.
    pause
    exit /b 1
)
echo Serving build\web at http://127.0.0.1:%PORT%/ - press Ctrl+C to stop
start "" /b python -c "import time, webbrowser; time.sleep(1); webbrowser.open('http://127.0.0.1:%PORT%/')"
python -m http.server %PORT% --bind 127.0.0.1 --directory build\web
pause
