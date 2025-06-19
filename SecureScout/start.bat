@echo off
title CySmart.ai  Web Security Scanner
color 0A

echo ==========================================================
echo             CySmart.ai  Web Security Scanner Starter
echo ==========================================================
echo.

:: Switch to the script directory
cd %~dp0

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    color 0C
    echo [Error] Python is not installed or not added to the PATH environment variable.
    echo Please install Python 3.8 or higher, then try again.
    echo.
    goto :end
)

:: Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    color 0C
    echo [Error] Node.js is not installed or not added to the PATH environment variable.
    echo Please install Node.js 16 or higher, then try again.
    echo.
    goto :end
)

:: Check if backend directory exists
if not exist "backend" (
    color 0C
    echo [Error] Cannot find backend directory.
    echo Please make sure you are running this script in the correct CySmart.ai  project directory.
    echo.
    goto :end
)

:: Check if frontend directory exists
if not exist "frontend" (
    color 0C
    echo [Error] Cannot find frontend directory.
    echo Please make sure you are running this script in the correct CySmart.ai  project directory.
    echo.
    goto :end
)

:: Start backend server
echo [Info] Starting backend server...
start cmd /k "title CySmart.ai  - Backend Server && color 0B && cd backend && call env\Scripts\activate && python run.py"

:: Wait a moment to let the backend start first
timeout /t 3 > nul

:: Start frontend server
echo [Info] Starting frontend server...
start cmd /k "title CySmart.ai  - Frontend Server && color 09 && cd frontend && npm run dev"

:: Show success message
color 0A
echo.
echo ==========================================================
echo [Success] CySmart.ai  started successfully!
echo.
echo Backend service address: http://localhost:8000
echo Frontend app address: http://localhost:3000
echo.
echo Please visit http://localhost:3000 in your browser to use CySmart.ai 
echo ==========================================================
echo.
echo [Tip] Closing this window will not stop the services. To stop the services, please close the opened command line windows.
echo.

:end
pause