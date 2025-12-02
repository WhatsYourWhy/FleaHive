@echo off
:: This line tells the computer to look for python in the current folder
:: "%~dp0" is a variable that means "the folder this batch file is sitting in"

echo waking up the hive...
echo ---------------------------------------------------

:: This runs the python script and passes the file you dropped (%1) to it
python "%~dp0fleahive.py" "%~1"

echo.
echo ---------------------------------------------------
echo Done. JSON output is above.
pause