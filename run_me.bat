@echo off
:loop
py main.py
set /p choice=PLAY AGAIN? (Y/N): 
if /i "%choice%"=="y" goto loop
