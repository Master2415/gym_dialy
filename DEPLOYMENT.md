# Gym Daily - Deployment Guide

## 🐳 Opción 1: Docker (Recomendado)

### Requisitos
- Docker
- Docker Compose

### Instalación y Ejecución

1. **Clonar el repositorio:**
```bash
git clone https://github.com/Master2415/gym_dialy.git
cd gym_dialy
```

2. **Iniciar con Docker Compose:**
```bash
docker-compose up -d
```

3. **Acceder a la aplicación:**
- Abrir navegador en: `http://localhost:5000`

4. **Detener la aplicación:**
```bash
docker-compose down
```

### Comandos Útiles

```bash
# Ver logs
docker-compose logs -f web

# Reiniciar servicios
docker-compose restart

# Eliminar todo (incluyendo datos)
docker-compose down -v
```

---

## 🪟 Opción 2: Windows (Portable)

### Requisitos
- Python 3.12 o superior
- Git (opcional)

### Instalación

1. **Descargar el proyecto:**
   - Opción A: Clonar con Git
     ```cmd
     git clone https://github.com/Master2415/gym_dialy.git
     cd gym_dialy
     ```
   - Opción B: Descargar ZIP desde GitHub y extraer

2. **Ejecutar setup automático:**
   ```cmd
   setup_windows.bat
   ```
   
   Este script:
   - Crea un entorno virtual
   - Instala todas las dependencias
   - Configura la base de datos SQLite

### Ejecución

```cmd
run_windows.bat
```

La aplicación estará disponible en: `http://localhost:5000`

### Detener la Aplicación

Presiona `Ctrl+C` en la ventana de comandos.

---

## 🐧 Opción 3: Linux/Mac (Manual)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/Master2415/gym_dialy.git
cd gym_dialy

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar aplicación
python run.py
```

---

## 📊 Características

- ✅ Gestión de sesiones de entrenamiento
- ✅ Seguimiento de ejercicios por grupo muscular
- ✅ Calculadora de 1RM
- ✅ Mediciones corporales
- ✅ Exportación de datos (CSV/JSON)
- ✅ Modo claro/oscuro
- ✅ Calendario de entrenamientos
- ✅ Análisis de progreso

## 🔧 Configuración

### Base de Datos

Por defecto, la aplicación usa **SQLite** (archivo `gym_daily.db`).

Para usar **MySQL** con Docker, edita `docker-compose.yml` y actualiza las credenciales.

### Puerto

Para cambiar el puerto, edita `run.py`:

```python
app.run(host='0.0.0.0', port=5000, debug=True)  # Cambiar 5000 por el puerto deseado
```

---

## 🆘 Solución de Problemas

### Docker

**Error: "port is already allocated"**
```bash
# Cambiar el puerto en docker-compose.yml
ports:
  - "5001:5000"  # Usar 5001 en lugar de 5000
```

**Error: "Cannot connect to database"**
```bash
# Esperar a que MySQL esté listo
docker-compose logs db
```

### Windows

**Error: "Python no encontrado"**
- Instalar Python desde: https://www.python.org/
- Asegurarse de marcar "Add Python to PATH" durante la instalación

**Error: "pip no reconocido"**
```cmd
python -m pip install --upgrade pip
```

---

## 📝 Notas

- Los datos se guardan en `gym_daily.db` (SQLite) o en el volumen Docker (MySQL)
- El primer usuario que se registre tendrá acceso completo
- Se recomienda cambiar las contraseñas por defecto en producción

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.
