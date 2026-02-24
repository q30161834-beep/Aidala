@echo off
echo Starting CopySpell AI Services...
echo.
echo Main Application: http://localhost:5000
echo Extension Service: http://localhost:5001
echo.
echo Press Ctrl+C to stop all services
echo ========================================
echo.

start cmd /k "cd /d "c:\Users\Administrator\Desktop\AI\copyspell-ai" && title CopySpell AI Main && python web_app.py"

timeout /t 5 /nobreak >nul

start cmd /k "cd /d "c:\Users\Administrator\Desktop\AI\copyspell-ai" && title CopySpell AI Extension && python run_extension.py"

pause