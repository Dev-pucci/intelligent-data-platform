@echo off
REM PostgreSQL Password Reset Script

set PGBIN=C:\Program Files\PostgreSQL\17\bin
set PGDATA=C:\Program Files\PostgreSQL\17\data

echo Step 1: Backing up pg_hba.conf...
copy "%PGDATA%\pg_hba.conf" "%PGDATA%\pg_hba.conf.backup"

echo Step 2: Changing authentication to trust mode...
powershell -Command "(Get-Content '%PGDATA%\pg_hba.conf') -replace 'scram-sha-256', 'trust' | Set-Content '%PGDATA%\pg_hba.conf'"

echo Step 3: Reloading PostgreSQL configuration...
"%PGBIN%\pg_ctl.exe" reload -D "%PGDATA%"

timeout /t 2 /nobreak >nul

echo Step 4: Resetting postgres password to 123456...
"%PGBIN%\psql.exe" -U postgres -c "ALTER USER postgres WITH PASSWORD '123456';"

echo Step 5: Restoring original pg_hba.conf...
copy "%PGDATA%\pg_hba.conf.backup" "%PGDATA%\pg_hba.conf"

echo Step 6: Reloading PostgreSQL configuration again...
"%PGBIN%\pg_ctl.exe" reload -D "%PGDATA%"

echo.
echo Password reset complete! postgres password is now: 123456
pause
