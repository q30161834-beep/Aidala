@echo off
echo Starting CopySpell AI Services...
echo.
echo Main Application: http://localhost:5000
echo Extension Service: http://localhost:5001
echo.
echo Press Ctrl+C to stop all services
echo ========================================
echo.

start "CopySpell AI Main" cmd /c "cd /d "c:\Users\Administrator\Desktop\AI\copyspell-ai" && python web_app.py"

timeout /t 3 /nobreak >nul

start "CopySpell AI Extension" cmd /c "cd /d "c:\Users\Administrator\Desktop\AI\copyspell-ai" && python run_extension.py"

echo Both services started successfully!
echo Main application will open in your browser shortly...
pause