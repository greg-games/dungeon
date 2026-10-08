@echo off
setlocal
cd /d "%~dp0"
python -m pip show pygbag >nul 2>&1 || python -m pip install pygbag==0.9.3
rem pygbag reads main.py with the Windows default encoding, but main.py contains UTF-8 box-drawing characters
set PYTHONUTF8=1
python -m pygbag --build  --ume_block=0 --title "Greg ganes - Dungeon" main.py
pause
