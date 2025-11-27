@echo off
setlocal enabledelayedexpansion

:: ============================================
:: GYM DAILY - INSTALADOR AUTOMATICO
:: ============================================
:: Este script instala automáticamente Python y todas las dependencias necesarias
:: Autor: Master2415
:: ============================================

title Gym Daily - Instalador Automatico

echo.
echo ==========================================
echo    GYM DAILY - INSTALADOR AUTOMATICO
echo ==========================================
echo.
echo Este instalador configurara automaticamente:
echo  - Python 3.12 (si no esta instalado)
echo  - Entorno virtual
echo  - Dependencias de la aplicacion
echo  - Base de datos SQLite
echo.
pause

:: ============================================
:: PASO 1: VERIFICAR/INSTALAR PYTHON
:: ============================================
echo.
echo [1/5] Verificando Python...

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python ya esta instalado.
    python --version
) else (
    echo [INFO] Python no encontrado. Descargando Python 3.12...
    
    :: Crear carpeta temporal
    if not exist temp mkdir temp
    
    :: Descargar Python 3.12 (instalador embebido)
    echo Descargando Python 3.12.0 (esto puede tardar unos minutos)...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile 'temp\python-installer.exe'}"
    
    if exist temp\python-installer.exe (
        echo [INFO] Instalando Python 3.12...
        echo IMPORTANTE: Se instalara Python automaticamente.
        
        :: Instalar Python silenciosamente con opciones recomendadas
        temp\python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
        
        :: Esperar a que termine la instalación
        timeout /t 30 /nobreak >nul
        
        :: Actualizar PATH en la sesión actual
        call refreshenv >nul 2>&1
        
        :: Verificar instalación
        python --version >nul 2>&1
        if %errorlevel% equ 0 (
            echo [OK] Python instalado correctamente.
            python --version
        ) else (
            echo [ERROR] La instalacion de Python fallo.
            echo Por favor instala Python manualmente desde: https://www.python.org/downloads/
            echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
            pause
            exit /b 1
        )
        
        :: Limpiar archivos temporales
        del temp\python-installer.exe
    ) else (
        echo [ERROR] No se pudo descargar Python.
        echo Por favor instala Python manualmente desde: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

:: ============================================
:: PASO 2: CREAR ENTORNO VIRTUAL
:: ============================================
echo.
echo [2/5] Configurando entorno virtual...

if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado.
) else (
    echo [OK] Entorno virtual ya existe.
)

:: ============================================
:: PASO 3: ACTIVAR ENTORNO E INSTALAR DEPENDENCIAS
:: ============================================
echo.
echo [3/5] Instalando dependencias...

call venv\Scripts\activate.bat

echo Actualizando pip...
python -m pip install --upgrade pip --quiet

echo Instalando paquetes requeridos...
pip install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo [ERROR] Fallo al instalar dependencias.
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas correctamente.

:: ============================================
:: PASO 4: CONFIGURAR BASE DE DATOS
:: ============================================
echo.
echo [4/5] Configurando base de datos SQLite...

:: SQLite viene incluido con Python, no necesita instalación adicional
if not exist gym_daily.db (
    echo Creando base de datos...
    python -c "from app import create_app; app = create_app(); print('Base de datos inicializada')"
    echo [OK] Base de datos creada: gym_daily.db
) else (
    echo [OK] Base de datos ya existe: gym_daily.db
)

:: ============================================
:: PASO 5: CREAR ACCESO DIRECTO
:: ============================================
echo.
echo [5/5] Creando acceso directo...

:: Crear script de inicio rápido
echo @echo off > INICIAR_GYM_DAILY.bat
echo cd /d "%%~dp0" >> INICIAR_GYM_DAILY.bat
echo call venv\Scripts\activate.bat >> INICIAR_GYM_DAILY.bat
echo echo ========================================== >> INICIAR_GYM_DAILY.bat
echo echo    GYM DAILY - SERVIDOR INICIADO >> INICIAR_GYM_DAILY.bat
echo echo ========================================== >> INICIAR_GYM_DAILY.bat
echo echo. >> INICIAR_GYM_DAILY.bat
echo echo Abre tu navegador en: http://127.0.0.1:5000 >> INICIAR_GYM_DAILY.bat
echo echo. >> INICIAR_GYM_DAILY.bat
echo echo Presiona CTRL+C para detener el servidor. >> INICIAR_GYM_DAILY.bat
echo echo. >> INICIAR_GYM_DAILY.bat
echo python run.py >> INICIAR_GYM_DAILY.bat
echo pause >> INICIAR_GYM_DAILY.bat

echo [OK] Acceso directo creado: INICIAR_GYM_DAILY.bat

:: ============================================
:: INSTALACION COMPLETADA
:: ============================================
echo.
echo ==========================================
echo   INSTALACION COMPLETADA EXITOSAMENTE
echo ==========================================
echo.
echo La aplicacion esta lista para usar.
echo.
echo COMO INICIAR LA APLICACION:
echo   1. Ejecuta: INICIAR_GYM_DAILY.bat
echo   2. Abre tu navegador en: http://127.0.0.1:5000
echo.
echo ARCHIVOS CREADOS:
echo   - venv\                (Entorno virtual de Python)
echo   - gym_daily.db         (Base de datos SQLite)
echo   - INICIAR_GYM_DAILY.bat (Acceso directo)
echo.
echo ==========================================
echo.

:: Preguntar si desea iniciar ahora
set /p start_now="Deseas iniciar la aplicacion ahora? (S/N): "
if /i "%start_now%"=="S" (
    echo.
    echo Iniciando aplicacion...
    call INICIAR_GYM_DAILY.bat
) else (
    echo.
    echo Para iniciar la aplicacion mas tarde, ejecuta: INICIAR_GYM_DAILY.bat
    pause
)
