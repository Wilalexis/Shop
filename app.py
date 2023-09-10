from flask import Flask, render_template, request, session,flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import HiddenField
from flask_paginate import Pagination, get_page_args
from flask_bootstrap import Bootstrap
import cx_Oracle

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'admin'  # clave secreta

# Configura la conexión a Oracle
dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
connection = cx_Oracle.connect(user='USR_DLSOCKS', password='admin', dsn=dsn)

class DeleteForm(FlaskForm):
    _method = HiddenField()

#Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')  # Ruta para la página de contacto
def contact():
    return render_template('contact.html')

@app.route('/login')  # Ruta para la página de login
def login():
    return render_template('login.html')

@app.route('/register')  # Ruta para la página de registro
def register():
    return render_template('register.html')

@app.route('/dashboard')# Ruta para la página de adminstrador
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin/users')# Ruta para la página de usuarios
def users():
    cursor = connection.cursor()
    cursor.execute("SELECT U.ID_USUARIO, U.NOMBRE, U.CORREO, U.CONTRASENA, R.NOMBRE_ROL FROM USUARIOS U JOIN ROLES R ON U.ID_ROL = R.ID_ROL")
    usuarios = cursor.fetchall()
    cursor.close()
    
    # Verificar si los parámetros 'page' y 'per_page' se pasan en la solicitud GET
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=5)
    
    # Supongamos que tienes una lista de usuarios llamada 'usuarios'
    total_users = len(usuarios)
    
    # Calcula el índice de inicio y final para la página actual
    start = (page - 1) * per_page
    end = start + per_page
    
    # Obtiene los usuarios para la página actual
    users_to_display = usuarios[start:end]

    # Crea un objeto de paginación
    pagination = Pagination(page=page, per_page=per_page, total=total_users, css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} usuarios')

    return render_template('users.html', usuarios=users_to_display, pagination=pagination)

@app.route('/admin/products')# Ruta para la página de productos
def products():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    return render_template('products.html',productos=productos)

@app.route('/crear_usuario', methods=['POST']) # Ruta para insertar a Oracle los datos de usuario
def crear_usuario():
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    id_rol = request.form.get('id_rol')

    # Preparar la consulta SQL
    sql = "INSERT INTO usuarios (nombre, correo, contrasena, id_rol) VALUES (:nombre, :correo, :contrasena, :id_rol)"

    # Ejecutar la consulta
    cursor = connection.cursor()
    cursor.execute(sql, {'nombre': nombre, 'correo': correo, 'contrasena': contrasena, 'id_rol': id_rol})
    connection.commit()

    #variable de sesion
    session['mensaje'] = 'Usuario agregado correctamente'   

    return redirect(url_for('users'))

@app.route('/eliminar_usuario/<int:ID_USUARIO>', methods=['POST', 'DELETE'])
def eliminar_usuario(ID_USUARIO):
    if request.method == 'POST' or request.form.get('_method') == 'DELETE':
        # Lógica para eliminar el usuario de la base de datos Oracle
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM USUARIOS WHERE ID_USUARIO = :ID_USUARIO", {'ID_USUARIO': ID_USUARIO})
            connection.commit()
            flash('Usuario eliminado con éxito', 'success')
        except Exception as e:
            flash('Error al eliminar el usuario', 'danger')
        finally:
            cursor.close()

    return redirect(url_for('users'))

@app.route('/buscar_usuarios', methods=['POST'])
def buscar_usuarios():
    campo_busqueda = request.form.get('campo_busqueda')
    valor_busqueda = request.form.get('valor_busqueda')

    # Consulta SQL parametrizada
    query = "SELECT * FROM usuarios WHERE 1=1"

    # Crear un diccionario de parámetros vacío
    params = {}

    if campo_busqueda == "nombre" and valor_busqueda:
        query += " AND nombre LIKE :nombre"
        params['nombre'] = f'%{valor_busqueda}%'
    elif campo_busqueda == "correo" and valor_busqueda:
        query += " AND correo LIKE :correo"
        params['correo'] = f'%{valor_busqueda}%'

    # Ejecutar la consulta y obtener los resultados
    cursor = connection.cursor()
    cursor.execute(query, params)
    usuarios_encontrados = cursor.fetchall()
    cursor.close()

    # Renderizar la página de resultados de búsqueda con los usuarios encontrados
    return render_template('resultadosBusquedaUsuario.html', usuarios=usuarios_encontrados)

@app.route('/editUsers/<int:ID_USUARIO>', methods=['GET', 'POST'])
def editUsers(ID_USUARIO):
    if request.method == 'GET':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Consulta SQL para obtener los datos del usuario por su ID
            query = "SELECT ID_USUARIO, nombre, correo, contrasena, id_rol FROM usuarios WHERE ID_USUARIO = :id_usuario"

            # Ejecuta la consulta con el ID_USUARIO como parámetro
            cursor.execute(query, id_usuario=ID_USUARIO)

            # Obtiene los datos del usuario
            usuario = cursor.fetchone()

            # Cierra el cursor y la conexión
            cursor.close()
            connection.close()

            if usuario is None:
                # Manejar el caso en el que no se encuentra el usuario
                flash('Usuario no encontrado', 'danger')
                return redirect(url_for('users'))  # Redirige a la página de usuarios

            return render_template('editUsers.html', usuario=usuario)

        except Exception as e:
            print("Error al obtener el usuario:", str(e))
            flash('Error al obtener el usuario', 'danger')
            return redirect(url_for('users'))  # Redirige a la página de usuarios

    elif request.method == 'POST':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Procesar el formulario de edición y actualizar los datos en la base de datos
            nombre = request.form.get('nombre')
            correo = request.form.get('correo')
            contrasena = request.form.get('contrasena')
            id_rol = request.form.get('id_rol')

            # Consulta SQL para actualizar los datos del usuario
            query = "UPDATE usuarios SET nombre = :nombre, correo = :correo, contrasena = :contrasena, id_rol = :id_rol WHERE ID_USUARIO = :id_usuario"

            # Ejecuta la consulta con los nuevos valores y el ID_USUARIO como parámetro
            cursor.execute(query, nombre=nombre, correo=correo, contrasena=contrasena, id_rol=id_rol, id_usuario=ID_USUARIO)

            # Confirma la transacción
            connection.commit()

            # Cierra el cursor y la conexión
            cursor.close()
            connection.close()

            flash('Usuario actualizado con éxito', 'success')
            return redirect(url_for('users'))  # Redirige de nuevo a la página de usuarios

        except Exception as e:
            print("Error al actualizar el usuario:", str(e))
            flash('Error al actualizar el usuario', 'danger')
            return redirect(url_for('users'))  # Redirige a la página de usuarios


if __name__ == '__main__':
    app.run(debug=True)


