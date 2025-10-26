@echo off
REM nginx Setup for Windows - Intelligent Data Acquisition Platform
REM Run as Administrator

echo ============================================
echo nginx Setup for Windows
echo ============================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/5] Checking for nginx installation...
if exist "C:\nginx\nginx.exe" (
    echo nginx already installed at C:\nginx
) else (
    echo nginx not found. Installing via Chocolatey...
    where choco >nul 2>&1
    if %errorLevel% neq 0 (
        echo ERROR: Chocolatey not found. Please install from: https://chocolatey.org/install
        echo Or download nginx manually from: http://nginx.org/en/download.html
        pause
        exit /b 1
    )
    choco install nginx -y
)

echo.
echo [2/5] Stopping existing nginx instance...
cd C:\nginx
nginx -s stop >nul 2>&1
timeout /t 2 >nul

echo.
echo [3/5] Backing up existing configuration...
if exist "C:\nginx\conf\nginx.conf" (
    copy "C:\nginx\conf\nginx.conf" "C:\nginx\conf\nginx.conf.backup" >nul
    echo Backup created: C:\nginx\conf\nginx.conf.backup
)

echo.
echo [4/5] Copying new configuration...
copy /Y "%~dp0nginx.conf" "C:\nginx\conf\nginx.conf"
echo Configuration copied to C:\nginx\conf\nginx.conf

echo.
echo [5/5] Updating Windows hosts file...
findstr /C:"scraper.local" C:\Windows\System32\drivers\etc\hosts >nul
if %errorLevel% neq 0 (
    echo 127.0.0.1   scraper.local >> C:\Windows\System32\drivers\etc\hosts
    echo 127.0.0.1   api.scraper.local >> C:\Windows\System32\drivers\etc\hosts
    echo 127.0.0.1   grafana.scraper.local >> C:\Windows\System32\drivers\etc\hosts
    echo Hosts file updated
) else (
    echo Hosts entries already exist
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo To start nginx:
echo   cd C:\nginx
echo   start nginx
echo.
echo Access n8n at: http://scraper.local
echo.
echo Management commands:
echo   Test config:  nginx -t
echo   Start:        start nginx
echo   Stop:         nginx -s stop
echo   Reload:       nginx -s reload
echo.
pause
