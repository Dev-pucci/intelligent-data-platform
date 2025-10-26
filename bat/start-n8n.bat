@echo off
echo Starting n8n workflow automation...
echo.

REM Load environment variables from .env file
for /f "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do set %%a

REM Start n8n
echo n8n will be available at: http://localhost:5678
echo.
npx n8n start

pause
