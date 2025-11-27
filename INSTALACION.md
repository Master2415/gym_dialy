# Gym Daily - Instalador Automático

## 📋 Descripción

Este instalador configura automáticamente todo lo necesario para ejecutar Gym Daily en Windows, incluyendo:

- ✅ Python 3.12 (descarga e instalación automática si no está presente)
- ✅ Entorno virtual de Python
- ✅ Todas las dependencias necesarias
- ✅ Base de datos SQLite (incluida con Python)
- ✅ Acceso directo para inicio rápido

## 🚀 Instalación Rápida

### Opción 1: Instalador Automático (Recomendado)

1. **Descarga el proyecto** completo
2. **Ejecuta** `INSTALAR.bat` (doble clic)
3. **Espera** a que termine la instalación (puede tardar 2-5 minutos)
4. **¡Listo!** Usa `INICIAR_GYM_DAILY.bat` para abrir la aplicación

El instalador se encargará de:
- Detectar si Python está instalado
- Descargar e instalar Python 3.12 automáticamente si es necesario
- Configurar el entorno virtual
- Instalar todas las dependencias
- Crear la base de datos
- Crear un acceso directo para inicio rápido

### Opción 2: Instalación Manual

Si prefieres instalar manualmente:

1. **Instala Python 3.12+** desde [python.org](https://www.python.org/downloads/)
   - ⚠️ Marca "Add Python to PATH" durante la instalación

2. **Ejecuta** `setup_windows.bat`

3. **Inicia** con `run_windows.bat`

## 🐳 Instalación con Docker

Si prefieres usar Docker:

```bash
# Construir e iniciar con docker-compose
docker-compose up -d

# La aplicación estará disponible en http://localhost:5000
```

## 📁 Archivos de Instalación

| Archivo | Descripción |
|---------|-------------|
| `INSTALAR.bat` | **Instalador automático** - Instala Python y todas las dependencias |
| `INICIAR_GYM_DAILY.bat` | Acceso directo para iniciar la aplicación (creado por el instalador) |
| `setup_windows.bat` | Instalador manual (requiere Python pre-instalado) |
| `setup_easy.bat` | Instalador con opciones de configuración |
| `run_windows.bat` | Script para ejecutar la aplicación |
| `Dockerfile` | Configuración de Docker |
| `docker-compose.yml` | Orquestación de contenedores Docker |

## 🔧 Requisitos del Sistema

### Mínimos
- **Sistema Operativo**: Windows 10 o superior
- **RAM**: 2 GB mínimo
- **Espacio en Disco**: 500 MB
- **Conexión a Internet**: Solo para la instalación inicial

### Automáticos (instalados por INSTALAR.bat)
- Python 3.12
- SQLite (incluido con Python)
- Dependencias de Python (Flask, etc.)

## 📖 Uso

### Iniciar la Aplicación

**Después de instalar**, simplemente ejecuta:
```
INICIAR_GYM_DAILY.bat
```

La aplicación se abrirá en tu navegador en: `http://127.0.0.1:5000`

### Detener la Aplicación

Presiona `CTRL + C` en la ventana de comandos

## 🗄️ Base de Datos

La aplicación usa **SQLite** por defecto:
- ✅ No requiere instalación adicional
- ✅ Archivo único: `gym_daily.db`
- ✅ Fácil de respaldar (solo copia el archivo)
- ✅ Portátil

### Ubicación de la Base de Datos
```
gym-daily/
  └── gym_daily.db  ← Tu base de datos
```

### Respaldar tus Datos
Simplemente copia el archivo `gym_daily.db` a un lugar seguro.

## ❓ Solución de Problemas

### El instalador no descarga Python
- Verifica tu conexión a internet
- Descarga Python manualmente desde [python.org](https://www.python.org/downloads/)
- Ejecuta `setup_windows.bat` en su lugar

### Error al instalar dependencias
```bash
# Ejecuta manualmente:
venv\Scripts\activate
pip install -r requirements.txt
```

### La aplicación no inicia
1. Verifica que el puerto 5000 esté libre
2. Revisa el archivo `gym_daily.db` existe
3. Ejecuta nuevamente `INSTALAR.bat`

### Python no se encuentra después de instalar
1. Reinicia tu computadora
2. Verifica que Python esté en el PATH:
   ```
   python --version
   ```

## 🔄 Actualización

Para actualizar la aplicación:

1. Descarga la nueva versión
2. Copia tu archivo `gym_daily.db` a la nueva carpeta
3. Ejecuta `INSTALAR.bat` nuevamente

## 📞 Soporte

Si encuentras problemas:
- Revisa la [documentación completa](README.md)
- Abre un issue en [GitHub](https://github.com/Master2415/gym-daily)

---

**Desarrollado por Douglas (Master2415)**
