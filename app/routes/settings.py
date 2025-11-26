from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from app.utils import login_required
from app.db import get_connection

settings_bp = Blueprint('settings', __name__)

@settings_bp.route("/settings")
@login_required
def index():
    options = [
        {
            'category': 'Perfil',
            'menu_items': [
                {'name': 'Editar Perfil', 'desc': 'Cambiar nombre, email', 'link': '/settings/profile'},
                # {'name': 'Cambiar Contraseña', 'desc': 'Actualizar tu clave de acceso', 'link': '#'} # Future implementation
            ]
        },
        {
            'category': 'Preferencias',
            'menu_items': [
                {'name': 'Tema', 'desc': 'Alternar entre Modo Oscuro / Claro', 'link': '#', 'action': 'toggleTheme()'},
                # {'name': 'Valores por Defecto', 'desc': 'Configurar series/reps predeterminadas', 'link': '#'}
            ]
        },
        {
            'category': 'Datos',
            'menu_items': [
                {'name': 'Exportar CSV', 'desc': 'Descargar historial en CSV', 'link': '/export/csv'},
                {'name': 'Exportar JSON', 'desc': 'Descargar copia de seguridad completa', 'link': '/export/json'},
                # {'name': 'Importar Datos', 'desc': 'Restaurar desde una copia de seguridad', 'link': '#'}
            ]
        }
    ]
    return render_template("settings.html", options=options)

@settings_bp.route("/settings/profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        print(f"DEBUG: Updating profile for user {session.get('user_id')}: {full_name}, {email}")
        
        try:
            cur.execute("""
                UPDATE users 
                SET full_name = %s, email = %s 
                WHERE id = %s
            """, (full_name, email, session['user_id']))
            conn.commit()
            print(f"DEBUG: Update committed. Row count: {cur.rowcount}")
            
            # Update session if username was stored there (it's not, but good practice)
            # session['full_name'] = full_name 
            
            flash("Perfil actualizado correctamente.", "success")
            return redirect(url_for('settings.index'))
        except Exception as e:
            flash(f"Error al actualizar perfil: {e}", "error")
        finally:
            conn.close()

    # GET request - load current data
    cur.execute("SELECT full_name, email FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    conn.close()
    
    user_data = {
        'full_name': user[0] if user else '',
        'email': user[1] if user else ''
    }

    return render_template("edit_profile.html", user=user_data)
