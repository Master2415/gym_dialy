from flask import Blueprint, render_template, session
from app.utils import login_required

settings_bp = Blueprint('settings', __name__)

@settings_bp.route("/settings")
@login_required
def index():
    # This is a mockup of what could be configured
    options = [
        {
            'category': 'Perfil',
            'menu_items': [
                {'name': 'Editar Perfil', 'desc': 'Cambiar nombre, peso, altura', 'link': '#'},
                {'name': 'Cambiar Contraseña', 'desc': 'Actualizar tu clave de acceso', 'link': '#'}
            ]
        },
        {
            'category': 'Preferencias',
            'menu_items': [
                {'name': 'Tema', 'desc': 'Alternar entre Modo Oscuro / Claro', 'link': '#', 'action': 'toggleTheme()'},
                {'name': 'Valores por Defecto', 'desc': 'Configurar series/reps predeterminadas', 'link': '#'}
            ]
        },
        {
            'category': 'Datos',
            'menu_items': [
                {'name': 'Exportar Datos', 'desc': 'Descargar copia de seguridad (CSV/JSON)', 'link': '/export/json'},
                {'name': 'Importar Datos', 'desc': 'Restaurar desde una copia de seguridad', 'link': '#'}
            ]
        }
    ]
    return render_template("settings.html", options=options)
