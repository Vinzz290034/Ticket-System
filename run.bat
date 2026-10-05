@echo off
echo ==================================================================
echo Starting onIT — IT Ticketing System
echo Organization: UC-METC Multipurpose Cooperative
echo Built in Pure Python (Standard Library)
echo ==================================================================
echo.
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" app.py
if %ERRORLEVEL% NEQ 0 (
    python app.py
)
pause
