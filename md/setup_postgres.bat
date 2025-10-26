@echo off
REM PostgreSQL Database Setup Script for Intelligent Data Platform

set PGBIN=C:\Program Files\PostgreSQL\17\bin
set PGPASSWORD=123456

echo Creating database and user...
"%PGBIN%\psql.exe" -U postgres -c "CREATE DATABASE scraper_db;"
"%PGBIN%\psql.exe" -U postgres -c "CREATE USER scraper_user WITH PASSWORD '123456';"
"%PGBIN%\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE scraper_db TO scraper_user;"
"%PGBIN%\psql.exe" -U postgres -d scraper_db -c "GRANT ALL ON SCHEMA public TO scraper_user;"
"%PGBIN%\psql.exe" -U postgres -d scraper_db -c "ALTER SCHEMA public OWNER TO scraper_user;"

echo Applying schema...
"%PGBIN%\psql.exe" -U scraper_user -d scraper_db -f "intelligent-data-platform\database\schema.sql"

echo.
echo Database setup complete!
pause
