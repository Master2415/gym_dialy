@echo off
echo ========================================
echo Gym Daily - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado.
    echo Por favor instala Python 3.12 o superior desde https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Creando entorno virtual...
if not exist venv (
    python -m venv venv
    echo Entorno virtual creado.
) else (
    echo Entorno virtual ya existe.
)

echo.
echo [2/5] Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo [3/5] Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [4/5] Verificando base de datos...
if not exist gym_daily.db (
    echo Creando base de datos SQLite...
    python -c "from app.db import init_db; init_db()"
    echo Base de datos creada.
) else (
    echo Base de datos ya existe.
)

echo.
echo [5/5] Configuracion completada!
echo.
echo ========================================
echo Para iniciar la aplicacion, ejecuta:
echo   run_windows.bat
echo ========================================
pause
