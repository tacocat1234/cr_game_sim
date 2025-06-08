@echo off
:loop
python main.py
set /p choice=PLAY AGAIN? (Y/N): 
if /i "%choice%"=="y" goto loop
