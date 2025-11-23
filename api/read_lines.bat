@echo off
setlocal enabledelayedexpansion
set "file=C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src\flask\cli.py"
set /a line_num=820
for /f "skip=819 tokens=*" %%a in ('type "%file%"') do (
    echo !line_num!: %%a
    set /a line_num+=1
    if !line_num! gtr 830 goto :eof
)
