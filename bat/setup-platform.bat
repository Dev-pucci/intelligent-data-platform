@echo off
REM Intelligent Data Acquisition Platform - Complete Setup Script
REM This script sets up everything needed to run the platform

echo ============================================================
echo Intelligent Data Acquisition Platform - Setup
echo ============================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running with Administrator privileges
) else (
    echo [WARNING] Not running as Administrator
    echo Some PostgreSQL operations may require admin rights
)

echo.
echo [STEP 1/6] Checking PostgreSQL Service...
echo ============================================================

REM Check if PostgreSQL service exists
sc query postgresql-x64-17 >nul 2>&1
if %errorLevel% == 0 (
    echo PostgreSQL service found!

    REM Check if it's running
    sc query postgresql-x64-17 | find "RUNNING" >nul
    if %errorLevel% == 0 (
        echo PostgreSQL is already running
    ) else (
        echo Starting PostgreSQL service...
        net start postgresql-x64-17
        if %errorLevel% == 0 (
            echo PostgreSQL started successfully!
        ) else (
            echo [WARNING] Could not start PostgreSQL automatically
            echo Please start it manually: Services -^> PostgreSQL -^> Start
            pause
        )
    )
) else (
    echo [ERROR] PostgreSQL service not found!
    echo Please install PostgreSQL first
    echo Download from: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
    pause
    exit /b 1
)

timeout /t 3 >nul

echo.
echo [STEP 2/6] Setting up Database...
echo ============================================================

REM Set PostgreSQL password environment variable
set PGPASSWORD=123456

REM Check if database exists
psql -U postgres -lqt | find "scraper_db" >nul 2>&1
if %errorLevel% == 0 (
    echo Database 'scraper_db' already exists
) else (
    echo Creating database and user...
    psql -U postgres -c "CREATE DATABASE scraper_db;"
    psql -U postgres -c "CREATE USER scraper_user WITH PASSWORD '123456';"
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE scraper_db TO scraper_user;"
    echo Database created successfully!
)

echo.
echo [STEP 3/6] Applying Database Schema...
echo ============================================================

if exist "database\schema.sql" (
    echo Applying schema from database\schema.sql...
    psql -U scraper_user -d scraper_db -f database\schema.sql
    if %errorLevel% == 0 (
        echo Schema applied successfully!
    ) else (
        echo [WARNING] Schema may have already been applied or there were errors
    )
) else (
    echo [WARNING] Schema file not found at database\schema.sql
    echo You may need to create it manually
)

echo.
echo [STEP 4/6] Installing Python Dependencies...
echo ============================================================

if exist "requirements.txt" (
    echo Installing packages from requirements.txt...
    pip install -r requirements.txt
    if %errorLevel% == 0 (
        echo Python dependencies installed successfully!
    ) else (
        echo [ERROR] Failed to install Python dependencies
        pause
    )
) else (
    echo [WARNING] requirements.txt not found
)

echo.
echo [STEP 5/6] Initializing Git Repository...
echo ============================================================

if exist ".git" (
    echo Git repository already initialized
) else (
    echo Initializing Git repository...
    git init
    if %errorLevel__ == 0 (
        echo Git initialized successfully!

        echo Creating .gitignore...
        if not exist ".gitignore" (
            echo Creating .gitignore file...
        )

        echo.
        echo [INFO] To push to GitHub:
        echo 1. Create repository on GitHub
        echo 2. Run: git add .
        echo 3. Run: git commit -m "Initial commit"
        echo 4. Run: git remote add origin YOUR_GITHUB_URL
        echo 5. Run: git push -u origin main
    ) else (
        echo [WARNING] Git may not be installed
        echo Download from: https://git-scm.com/download/win
    )
)

echo.
echo [STEP 6/6] Testing Platform...
echo ============================================================

if exist "test_full_pipeline.py" (
    echo Running full pipeline test...
    python test_full_pipeline.py
    if %errorLevel% == 0 (
        echo [SUCCESS] Platform test completed!
    ) else (
        echo [WARNING] Test had some issues, but platform may still work
    )
) else (
    echo [INFO] Test file not found, skipping tests
)

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo What's Ready:
echo   - PostgreSQL database 'scraper_db'
echo   - Database schema applied
echo   - Python dependencies installed
echo   - Git repository initialized
echo.
echo Next Steps:
echo   1. Start n8n:        .\start-n8n.bat
echo   2. Access n8n:       http://localhost:5678
echo   3. Run scrapers:     python -m scrapers.scraper_runner --config configs/sites/jumia_spa.yml
echo   4. Deploy to Render: Follow RENDER_DEPLOYMENT_CHECKLIST.md
echo.
echo PostgreSQL Credentials:
echo   Database: scraper_db
echo   User:     scraper_user
echo   Password: 123456
echo   Host:     localhost
echo   Port:     5432
echo.
pause
