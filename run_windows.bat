@echo off
echo ========================================
echo Iniciando Gym Daily...
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
echo Servidor corriendo en http://localhost:5000
echo Presiona Ctrl+C para detener el servidor
echo.
python run.py

pause
