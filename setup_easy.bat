@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo       GYM DAILY - SETUP & LAUNCHER
echo ==========================================

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Por favor instala Python 3.x desde https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b
)

:: 2. Create Virtual Environment
if not exist venv (
    echo [INFO] Creando entorno virtual (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Fallo al crear el entorno virtual.
        pause
        exit /b
    )
)

:: 3. Activate Virtual Environment
call venv\Scripts\activate

:: 4. Install Dependencies
echo [INFO] Verificando e instalando dependencias...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al instalar dependencias.
    pause
    exit /b
)

:: 5. Database Configuration
echo.
echo ==========================================
echo CONFIGURACION DE BASE DE DATOS
echo ==========================================
echo 1. SQLite (Recomendado - Facil, archivo local, sin instalacion extra)
echo 2. MySQL (Avanzado - Requiere servidor MySQL instalado)
echo.
set /p choice="Seleccione una opcion (1/2) [Enter para SQLite]: "

if "%choice%"=="2" (
    set DB_TYPE=mysql
    echo.
    echo [INFO] Configurando MySQL...
    echo Por favor ingrese las credenciales de su servidor MySQL.
    
    set /p DB_HOST="Host [localhost]: "
    if "!DB_HOST!"=="" set DB_HOST=localhost
    
    set /p DB_USER="Usuario [root]: "
    if "!DB_USER!"=="" set DB_USER=root
    
    set /p DB_PASSWORD="Password: "
    
    set /p DB_NAME="Nombre BD [gym_diario]: "
    if "!DB_NAME!"=="" set DB_NAME=gym_diario
    
    echo.
    echo [INFO] Intentando conectar a MySQL...
    :: We set env vars for the python process
    set DB_HOST=!DB_HOST!
    set DB_USER=!DB_USER!
    set DB_PASSWORD=!DB_PASSWORD!
    set DB_NAME=!DB_NAME!
    
) else (
    set DB_TYPE=sqlite
    echo.
    echo [INFO] Usando SQLite. La base de datos se creara automaticamente en 'gym_diario.db'.
)

:: 6. Run Application
echo.
echo ==========================================
echo INICIANDO APLICACION...
echo ==========================================
echo Abra su navegador en http://127.0.0.1:5000
echo Presione CTRL+C para detener el servidor.
echo.

python run.py

pause
