from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import HiddenField
from flask_paginate import Pagination, get_page_args
from flask_bootstrap import Bootstrap
import cx_Oracle
import os
import time
#import psycopg2


app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'admin'  # clave secreta

# Configura la conexión a Oracle
dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
connection = cx_Oracle.connect(user='USR_DLSOCKS', password='admin', dsn=dsn)

#   session['logged_in'] = True

class DeleteForm(FlaskForm):
    _method = HiddenField()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        # Busca el usuario en la tabla 'login' con el correo y contraseña proporcionados
        cursor = connection.cursor()
        cursor.execute("SELECT id_login, id_rol FROM login WHERE correo = :correo AND contrasena = :contrasena",
                       {'correo': correo, 'contrasena': contrasena})
        user = cursor.fetchone()

        if user:
            id_login, id_rol = user

            if id_rol == 2:
                # Usuario con rol 2, redirige a buy.html
                session['id_login'] = id_login  # Almacena el ID de inicio de sesión en la sesión
                return redirect(url_for('buy'))
            else:
                # Usuario con rol 1, redirige a dashboard.html
                session['id_login'] = id_login  # Almacena el ID de inicio de sesión en la sesión
                return redirect(url_for('dashboard'))
        else:
            # El usuario no se encontró en la tabla 'login', busca en la tabla 'usuarios'
            cursor.execute("SELECT id_rol FROM usuarios WHERE correo = :correo", {'correo': correo})
            user_rol = cursor.fetchone()

            if user_rol and user_rol[0] == 1:
                # Usuario con rol 1, redirige a dashboard.html
                return redirect(url_for('dashboard'))

        # Si ninguna coincidencia se encontró, muestra un mensaje de error
        error_message = 'Usuario no encontrado'
        return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Elimina la información de la sesión del usuario
    session.pop('id_login', None)  # Elimina la clave 'id_login' de la sesión si existe

    # Redirige al usuario a la página de inicio de sesión
    return redirect(url_for('login'))

@app.route('/') # Ruta para index.html
def index():
    return render_template('index.html')


@app.route('/contact')  # Ruta para la página de contacto
def contact():
    return render_template('contact.html')

@app.route('/register')  # Ruta para la página de registro
def register():
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    # Verifica si el usuario tiene una sesión válida y el rol correcto
    if 'id_login' in session:
        id_login = session['id_login']

        # Realiza cualquier otra lógica que necesites aquí

        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


@app.route('/shoppingcart')  # Ruta para la página de carrito de compras
def shoppingcart():
    return render_template('shoppingcart.html')

@app.route('/buy')
def buy():
    # Verifica si el usuario tiene una sesión válida y el rol correcto
    if 'id_login' in session:
        id_login = session['id_login']

        # Obtén los productos
        cursor = connection.cursor()
        cursor.execute("SELECT P.ID_PRODUCTO, P.NOMBRE_PRODUCTO, P.DESCRIPCION, T.NOMBRE_TALLA, C.NOMBRE_CATEGORIA, M.NOMBRE_MARCA, P.PRECIO, P.EXISTENCIA, P.IMAGEN FROM productos P JOIN TALLAS T ON P.ID_TALLA = T.ID_TALLA JOIN CATEGORIAS C ON P.ID_CATEGORIA = C.ID_CATEGORIA JOIN MARCAS M ON P.ID_MARCA = M.ID_MARCA ORDER BY P.ID_PRODUCTO DESC")
        productos = cursor.fetchall()
        cursor.close()

        # Obtén las tallas
        cursor1 = connection.cursor()
        cursor1.execute("SELECT ID_TALLA, NOMBRE_TALLA FROM TALLAS")
        tallasproductos = cursor1.fetchall()
        cursor1.close()

        # Obtén las categorías
        cursor2 = connection.cursor()
        cursor2.execute("SELECT ID_CATEGORIA, NOMBRE_CATEGORIA FROM CATEGORIAS")
        categoriasproductos = cursor2.fetchall()
        cursor2.close()

        # Obtén las marcas
        cursor3 = connection.cursor()
        cursor3.execute("SELECT ID_MARCA, NOMBRE_MARCA FROM MARCAS")
        marcasproductos = cursor3.fetchall()
        cursor3.close()

        # Obtén el timestamp actual
        timestamp = int(time.time())

        # Devuelve la plantilla de compras con los datos obtenidos
        return render_template('buy.html', productos=productos, tallasproductos=tallasproductos, categoriasproductos=categoriasproductos, marcasproductos=marcasproductos, timestamp=timestamp)
    else:
        return redirect(url_for('login'))



@app.route('/carrito')
def ver_carrito():
    carrito = []
    if 'carrito' in session:
        for producto_id in session['carrito']:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM productos WHERE id = :id", {'id': producto_id})
            producto = cursor.fetchone()
            carrito.append(producto)
    return render_template('carrito.html', carrito=carrito)

@app.route('/limpiar_carrito')
def limpiar_carrito():
    session.pop('carrito', None)
    return redirect(url_for('index'))

@app.route('/admin/category') # ruta para la pagina categorias
def category():
    cursor = connection.cursor()
    cursor.execute(
        "SELECT ID_CATEGORIA, NOMBRE_CATEGORIA FROM CATEGORIAS")
    categorias = cursor.fetchall()
    cursor.close()

    # Verificar si los parámetros 'page' y 'per_page' se pasan en la solicitud GET
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=5)

    # Supongamos que tienes una lista de categorias llamada 'categorias'
    total_category = len(categorias)

    # Calcula el índice de inicio y final para la página actual
    start = (page - 1) * per_page
    end = start + per_page

    #obtiene las categorias actuales
    category_to_display = categorias[start:end]

    # Crea un objeto de paginación
    pagination = Pagination(page=page, per_page=per_page, total=total_category,
                            css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} categorias')


    return render_template('category.html', categorias=category_to_display, pagination=pagination)

# Ruta para insertar a Oracle los datos de categoría
@app.route('/crear_categoria', methods=['POST'])
def crear_categoria():
    nombre_categoria = request.form.get('nombre_categoria')

    # Preparar la consulta SQL
    sql = "INSERT INTO categorias (nombre_categoria) VALUES (:nombre_categoria)"

    # Ejecutar la consulta
    cursor = connection.cursor()
    cursor.execute(sql, {'nombre_categoria': nombre_categoria})
    connection.commit()

    # variable de sesion
    session['mensaje'] = 'Categoría agregada correctamente'

    return redirect(url_for('category'))

@app.route('/editCategories/<int:ID_CATEGORIA>', methods=['GET', 'POST']) #ruta para editar categoria
def editCategories(ID_CATEGORIA):
    if request.method == 'GET':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Consulta SQL para obtener los datos por su ID
            query = "SELECT ID_CATEGORIA, nombre_categoria FROM categorias WHERE ID_CATEGORIA = :id_categoria"

            # Ejecuta la consulta con el ID_CATEGORIA como parámetro
            cursor.execute(query, id_categoria=ID_CATEGORIA)

            # Obtiene los datos del categoria
            categoria = cursor.fetchone()

            # Cierra el cursor y la conexión
            cursor.close()
            connection.close()

            if categoria is None:
                # Manejar el caso en el que no se encuentra el categoria
                flash('Categoria no encontrada', 'danger')
                # Redirige a la página de usuarios
                return redirect(url_for('category'))

            return render_template('editCategories.html', categoria=categoria)

        except Exception as e:
            print("Error al obtener la categoria:", str(e))
            flash('Error al obtener la categoria', 'danger')
            # Redirige a la página de usuarios
            return redirect(url_for('category'))

    elif request.method == 'POST':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Procesar el formulario de edición y actualizar los datos en la base de datos
            nombre_categoria = request.form.get('nombre_categoria')

            # Consulta SQL para actualizar los datos del usuario
            query = "UPDATE categorias SET nombre_categoria = :nombre_categoria WHERE ID_CATEGORIA = :id_categoria"

            # Ejecuta la consulta con los nuevos valores y el ID_CATEGORIA como parámetro
            cursor.execute(query, nombre_categoria=nombre_categoria, id_categoria=ID_CATEGORIA)

            # Confirma la transacción
            connection.commit()

            # Cierra el cursor y la conexión
            cursor.close()
            connection.close()

            flash('Categoria actualizada con éxito', 'success')
            # Redirige de nuevo a la página de usuarios
            return redirect(url_for('category'))

        except Exception as e:
            print("Error al actualizar la categoria:", str(e))
            flash('Error al actualizar la categoria', 'danger')
            # Redirige a la página de usuarios
            return redirect(url_for('category'))

@app.route('/eliminar_categoria/<int:ID_CATEGORIA>', methods=['POST', 'DELETE']) #ruta para eliminar categoria
def eliminar_categoria(ID_CATEGORIA):
    if request.method == 'POST' or request.form.get('_method') == 'DELETE':
        # Lógica para eliminar de la base de datos Oracle
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM CATEGORIAS WHERE ID_CATEGORIA = :ID_CATEGORIA", {
                           'ID_CATEGORIA': ID_CATEGORIA})
            connection.commit()
            flash('Categoria eliminada con éxito', 'success')
        except Exception as e:
            flash('Error al eliminar la categoria', 'danger')
        finally:
            cursor.close()

    return redirect(url_for('category'))

@app.route('/admin/client')
def client():
    cursor = connection.cursor()
    cursor.execute("SELECT clientes.id_cliente,clientes.nombre_cliente,clientes.direccion,clientes.nit,clientes.correo,login.contrasena FROM clientes INNER JOIN login ON clientes.id_login = login.id_login")
    #cursor.execute("SELECT U.ID_CLIENTE, U.NOMBRE_CLIENTE, U.DIRECCION, U.NIT, U.CORREO, U.ID_LOGIN FROM CLIENTES U JOIN LOGIN R ON U.ID_LOGIN = R.ID_LOGIN")
    clientes = cursor.fetchall()
    cursor.close()

    cursor1 = connection.cursor()
    cursor1.execute("SELECT ID_LOGIN, CONTRASENA FROM LOGIN")
    login = cursor1.fetchall()
    cursor1.close()

    # Verificar si los parámetros 'page' y 'per_page' se pasan en la solicitud GET
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=5)

    # Supongamos que tienes una lista de clientes llamada 'clientes'
    total_clients = len(clientes)

    # Calcula el índice de inicio y final para la página actual
    start = (page - 1) * per_page
    end = start + per_page

    #obtiene las clientes actuales
    clients_to_display = clientes[start:end]

    # Crea un objeto de paginación
    pagination = Pagination(page=page, per_page=per_page, total=total_clients,
                            css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} clientes')
    
    
    return render_template('client.html', clientes=clients_to_display, pagination=pagination, login = login)

@app.route('/crear_cliente', methods=['POST'])
def crear_client():
    return redirect(url_for('client'))

@app.route('/eliminar_client', methods=['POST'])
def eliminar_client():
    return redirect(url_for('client'))

@app.route('/editClient', methods=['POST'])
def editClient():
    return redirect(url_for('client'))

@app.route('/admin/marc')
def marc():
    cursor = connection.cursor()
    cursor.execute("SELECT ID_MARCA, NOMBRE_MARCA FROM MARCAS")
    marcas = cursor.fetchall()
    cursor.close()

    # Verificar si los parámetros 'page' y 'per_page' se pasan en la solicitud GET
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=5)

    # Supongamos que tienes una lista de usuarios llamada 'marcas'
    total_brands = len(marcas)

    # Calcula el índice de inicio y final para la página actual
    start = (page - 1) * per_page
    end = start + per_page

    #obtiene las marcas actuales
    brandas_to_display = marcas[start:end]

    # Crea un objeto de paginación
    pagination = Pagination(page=page, per_page=per_page, total=total_brands,
                            css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} marcas')
    
    
    return render_template('marc.html', marcas=brandas_to_display, pagination=pagination)

# Ruta para insertar a Oracle los datos de marcas
@app.route('/crear_marca', methods=['POST'])
def crear_marca():
    nombre_marca = request.form.get('nombre_marca')

    # Preparar la consulta SQL
    sql = "INSERT INTO marcas (nombre_marca) VALUES (:nombre_marca)"

    # Ejecutar la consulta
    cursor = connection.cursor()
    cursor.execute(sql, {'nombre_marca': nombre_marca})
    connection.commit()

    # variable de sesion
    session['mensaje'] = 'Marca agregada correctamente'

    return redirect(url_for('marc'))

@app.route('/editBrands/<int:ID_MARCA>', methods=['GET', 'POST']) #ruta para editar marcas
def editBrands(ID_MARCA):
    if request.method == 'GET':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Consulta SQL para obtener los datos por su ID
            query = "SELECT ID_MARCA, nombre_marca FROM marcas WHERE ID_MARCA = :id_marca"

            # Ejecuta la consulta con el ID_MARCA como parámetro
            cursor.execute(query, id_marca=ID_MARCA)

            # Obtiene los datos del marca
            marca = cursor.fetchone()

            # Cierra el cursor y la conexión
            cursor.close()
            connection.close()

            if marca is None:
                # Manejar el caso en el que no se encuentra el marca
                flash('Marca no encontrada', 'danger')
                # Redirige a la página de usuarios
                return redirect(url_for('marc'))

            return render_template('editBrands.html', marca=marca)

        except Exception as e:
            print("Error al obtener la marca:", str(e))
            flash('Error al obtener la marca', 'danger')
            # Redirige a la página de usuarios
            return redirect(url_for('marc'))

    elif request.method == 'POST':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Procesar el formulario de edición y actualizar los datos en la base de datos
            nombre_marca = request.form.get('nombre_marca')

            # Consulta SQL para actualizar los datos del usuario
            query = "UPDATE marcas SET nombre_marca = :nombre_marca WHERE ID_MARCA = :id_marca"

            # Ejecuta la consulta con los nuevos valores y el ID_CATEGORIA como parámetro
            cursor.execute(query, nombre_marca=nombre_marca, id_marca=ID_MARCA)

            # Confirma la transacción
            connection.commit()

            # Cierra el cursor y la conexión
            cursor.close()
            connection.close()

            flash('Categoria actualizada con éxito', 'success')
            # Redirige de nuevo a la página de marcas
            return redirect(url_for('marc'))

        except Exception as e:
            print("Error al actualizar la marca:", str(e))
            flash('Error al actualizar la marca', 'danger')
            # Redirige a la página de usuarios
            return redirect(url_for('marc'))

@app.route('/eliminar_marca/<int:ID_MARCA>', methods=['POST', 'DELETE']) #ruta para eliminar marcas
def eliminar_marca(ID_MARCA):
    if request.method == 'POST' or request.form.get('_method') == 'DELETE':
        # Lógica para eliminar de la base de datos Oracle
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM MARCAS WHERE ID_MARCA = :ID_MARCA", {
                           'ID_MARCA': ID_MARCA})
            connection.commit()
            flash('Marca eliminada con éxito', 'success')
        except Exception as e:
            flash('Error al eliminar la marca', 'danger')
        finally:
            cursor.close()

    return redirect(url_for('marc'))

@app.route('/admin/sizes') # Ruta para la pagina de tallas
def sizes():
    cursor = connection.cursor()
    cursor.execute(
        "SELECT ID_TALLA, NOMBRE_TALLA FROM TALLAS")
    tallas = cursor.fetchall()
    cursor.close()

    # Verificar si los parámetros 'page' y 'per_page' se pasan en la solicitud GET
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=5)

    # Supongamos que tienes una lista de tallas llamada 'tallas'
    total_sizes = len(tallas)

    # Calcula el índice de inicio y final para la página actual
    start = (page - 1) * per_page
    end = start + per_page

    #obtiene las categorias actuales
    sizes_to_display = tallas[start:end]

    # Crea un objeto de paginación
    pagination = Pagination(page=page, per_page=per_page, total=total_sizes,
                            css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} tallas')
    
    return render_template('sizes.html', tallas=sizes_to_display, pagination=pagination) 

# Ruta para insertar a Oracle los datos de tallas
@app.route('/crear_talla', methods=['POST'])
def crear_talla():
    nombre_talla = request.form.get('nombre_talla')

    # Preparar la consulta SQL
    sql = "INSERT INTO tallas (nombre_talla) VALUES (:nombre_talla)"

    # Ejecutar la consulta
    cursor = connection.cursor()
    cursor.execute(sql, {'nombre_talla': nombre_talla})
    connection.commit()

    # variable de sesion
    session['mensaje'] = 'talla agregada correctamente'

    return redirect(url_for('sizes'))

@app.route('/editSizes/<int:ID_TALLA>', methods=['GET', 'POST']) #ruta para editar tallas
def editSizes(ID_TALLA):
    if request.method == 'GET':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Consulta SQL para obtener los datos por su ID
            query = "SELECT ID_TALLA, nombre_talla FROM TALLAS WHERE ID_TALLA = :ID_TALLA"

            # Ejecuta la consulta con el ID_TALLA como parámetro
            cursor.execute(query, ID_TALLA=ID_TALLA)

            # Obtiene los datos del marca
            talla = cursor.fetchone()

            # Cierra el cursor y la conexión
            cursor.close()
            connection.close()

            if talla is None:
                # Manejar el caso en el que no se encuentra la talla
                flash('talla no encontrada', 'danger')
                # Redirige a la página de talla
                return redirect(url_for('sizes'))

            return render_template('editSizes.html', talla=talla)

        except Exception as e:
            print("Error al obtener la talla:", str(e))
            flash('Error al obtener la talla', 'danger')
            # Redirige a la página de tallas
            return redirect(url_for('sizes'))

    elif request.method == 'POST':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Procesar el formulario de edición y actualizar los datos en la base de datos
            nombre_talla = request.form.get('nombre_talla')

            # Consulta SQL para actualizar los datos del usuario
            query = "UPDATE tallas SET nombre_talla = :nombre_talla WHERE ID_talla = :id_tallas"

            # Ejecuta la consulta con los nuevos valores y el ID_TALLAS como parámetro
            cursor.execute(query, nombre_talla=nombre_talla, id_tallas=ID_TALLA)

            # Confirma la transacción
            connection.commit()

            # Cierra el cursor y la conexión
            cursor.close()
            connection.close()

            flash('Tallas actualizada con éxito', 'success')
            # Redirige de nuevo a la página de tallas
            return redirect(url_for('sizes'))

        except Exception as e:
            print("Error al actualizar la talla:", str(e))
            flash('Error al actualizar la talla', 'danger')
            # Redirige a la página de tallas
            return redirect(url_for('sizes'))

@app.route('/eliminar_talla/<int:ID_TALLA>', methods=['POST', 'DELETE']) #ruta para eliminar Tallas
def eliminar_talla(ID_TALLA):
    if request.method == 'POST' or request.form.get('_method') == 'DELETE':
        # Lógica para eliminar de la base de datos Oracle
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM TALLAS WHERE ID_TALLA = :ID_TALLA", {
                           'ID_TALLA': ID_TALLA})
            connection.commit()
            flash('Talla eliminada con éxito', 'success')
        except Exception as e:
            flash('Error al eliminar la talla', 'danger')
        finally:
            cursor.close()

    return redirect(url_for('sizes'))

@app.route('/admin/users')  # Ruta para la página de usuarios
def users():
    cursor = connection.cursor()
    cursor.execute("SELECT U.ID_USUARIO, U.NOMBRE, U.CORREO, U.CONTRASENA, R.NOMBRE_ROL FROM USUARIOS U JOIN ROLES R ON U.ID_ROL = R.ID_ROL")
    usuarios = cursor.fetchall()
    cursor.close()

    cursor1 = connection.cursor()
    cursor1.execute("SELECT ID_ROL, NOMBRE_ROL FROM ROLES")
    roles = cursor1.fetchall()
    cursor1.close()

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

    pagination = Pagination(page=page, per_page=per_page, total=total_users,
                            css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} categoria')

    return render_template('users.html', usuarios=users_to_display, pagination=pagination, roles=roles)

# Ruta para insertar a Oracle los datos de usuario
@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    id_rol = request.form.get('id_rol')

    # Preparar la consulta SQL
    sql = "INSERT INTO usuarios (nombre, correo, contrasena, id_rol) VALUES (:nombre, :correo, :contrasena, :id_rol)"

    # Ejecutar la consulta
    cursor = connection.cursor()
    cursor.execute(sql, {'nombre': nombre, 'correo': correo,
                   'contrasena': contrasena, 'id_rol': id_rol})
    connection.commit()

    # variable de sesion
    session['mensaje'] = 'Usuario agregado correctamente'

    return redirect(url_for('users'))

@app.route('/eliminar_usuario/<int:ID_USUARIO>', methods=['POST', 'DELETE'])
def eliminar_usuario(ID_USUARIO):
    if request.method == 'POST' or request.form.get('_method') == 'DELETE':
        # Lógica para eliminar el usuario de la base de datos Oracle
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM USUARIOS WHERE ID_USUARIO = :ID_USUARIO", {
                           'ID_USUARIO': ID_USUARIO})
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
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

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

            cursor1 = connection.cursor()
            cursor1.execute("SELECT ID_ROL, NOMBRE_ROL FROM ROLES")
            roles = cursor1.fetchall()
            cursor1.close()
            connection.close()

            if usuario is None:
                # Manejar el caso en el que no se encuentra el usuario
                flash('Usuario no encontrado', 'danger')
                # Redirige a la página de usuarios
                return redirect(url_for('users'))

            return render_template('editUsers.html', usuario=usuario, roles=roles)

        except Exception as e:
            print("Error al obtener el usuario:", str(e))
            flash('Error al obtener el usuario', 'danger')
            # Redirige a la página de usuarios
            return redirect(url_for('users'))

    elif request.method == 'POST':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

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
            cursor.execute(query, nombre=nombre, correo=correo,
                           contrasena=contrasena, id_rol=id_rol, id_usuario=ID_USUARIO)

            # Confirma la transacción
            connection.commit()

            # Cierra el cursor y la conexión
            cursor.close()
            connection.close()

            flash('Usuario actualizado con éxito', 'success')
            # Redirige de nuevo a la página de usuarios
            return redirect(url_for('users'))

        except Exception as e:
            print("Error al actualizar el usuario:", str(e))
            flash('Error al actualizar el usuario', 'danger')
            # Redirige a la página de usuarios
            return redirect(url_for('users'))

@app.route('/admin/products')  # Ruta para la página de productos
def products():
    cursor = connection.cursor()
    cursor.execute("SELECT P.ID_PRODUCTO, P.NOMBRE_PRODUCTO, P.DESCRIPCION, T.NOMBRE_TALLA, C.NOMBRE_CATEGORIA, M.NOMBRE_MARCA, P.PRECIO, P.EXISTENCIA, P.IMAGEN FROM productos P JOIN TALLAS T ON P.ID_TALLA = T.ID_TALLA JOIN CATEGORIAS C ON P.ID_CATEGORIA = C.ID_CATEGORIA JOIN MARCAS M ON P.ID_MARCA = M.ID_MARCA ORDER BY P.ID_PRODUCTO DESC")
    productos = cursor.fetchall()
    cursor.close()

    cursor1 = connection.cursor()
    cursor1.execute("SELECT ID_TALLA, NOMBRE_TALLA FROM TALLAS")
    tallasproductos = cursor1.fetchall()
    cursor1.close()

    cursor2 = connection.cursor()
    cursor2.execute("SELECT ID_CATEGORIA, NOMBRE_CATEGORIA FROM CATEGORIAS")
    categoriasproductos = cursor2.fetchall()
    cursor2.close()

    cursor3 = connection.cursor()
    cursor3.execute("SELECT ID_MARCA, NOMBRE_MARCA FROM MARCAS")
    marcasproductos = cursor3.fetchall()
    cursor3.close()

    # Verificar si los parámetros 'page' y 'per_page' se pasan en la solicitud GET
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=5)

    # Supongamos que tienes una lista de productos llamada 'productos'
    total_products = len(productos)

    # Calcula el índice de inicio y final para la página actual
    start = (page - 1) * per_page
    end = start + per_page

    # Obtiene los productos para la página actual
    products_to_display = productos[start:end]

    # Crea un objeto de paginación
    pagination = Pagination(page=page, per_page=per_page, total=total_products, css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} productos')

    return render_template('products.html', productos=products_to_display, tallasproductos=tallasproductos, categoriasproductos=categoriasproductos, marcasproductos=marcasproductos, pagination=pagination)

# Ruta para insertar a Oracle los datos del producto
@app.route('/crear_producto', methods=['POST'])
def crear_producto():
    nombre_producto = request.form.get('nombre_producto')
    descripcion = request.form.get('descripcion')
    id_talla = request.form.get('id_talla')
    id_categoria = request.form.get('id_categoria')
    id_marca = request.form.get('id_marca')
    precio = request.form.get('precio')
    existencia = request.form.get('existencia')
    imagen = request.files['imagen']

    if imagen:
        # Guarda la imagen en la ruta static/imgbd
        imagen.save(os.path.join('static/imgbd', imagen.filename))

        # Guarta la imagen en la base de datos empezando por imgbd/ seguido del nombre de la imagen
        ruta_imagen = os.path.join('imgbd/', imagen.filename)
    else:
        ruta_imagen = None

    # Preparar la consulta SQL
    sql = "INSERT INTO productos (nombre_producto, descripcion, id_talla, id_categoria, id_marca, precio, existencia, imagen) VALUES (:nombre_producto, :descripcion, :id_talla, :id_categoria, :id_marca, :precio, :existencia, :imagen)"

    # Ejecutar la consulta
    cursor = connection.cursor()
    cursor.execute(sql, {'nombre_producto': nombre_producto, 'descripcion': descripcion, 'id_talla': id_talla,
                   'id_categoria': id_categoria, 'id_marca': id_marca, 'precio': precio, 'existencia': existencia, 'imagen': ruta_imagen})
    connection.commit()

    # variable de sesion
    session['mensaje'] = 'Producto agregado correctamente'

    return redirect(url_for('products'))

@app.route('/editProducts/<int:ID_PRODUCTO>', methods=['GET', 'POST'])
def editProducts(ID_PRODUCTO):
    if request.method == 'GET':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Consulta SQL para obtener los datos del producto por su ID
            query = "SELECT ID_PRODUCTO, nombre_producto, descripcion, id_talla, id_categoria, id_marca, precio, existencia, imagen FROM productos WHERE ID_PRODUCTO = :id_producto"

            # Ejecuta la consulta con el ID_PRODUCTO como parámetro
            cursor.execute(query, id_producto=ID_PRODUCTO)

            # Obtiene los datos del producto
            producto = cursor.fetchone()

            # Cierra el cursor y la conexión
            cursor.close()

            cursor1 = connection.cursor()
            cursor1.execute("SELECT ID_TALLA, NOMBRE_TALLA FROM TALLAS")
            tallasproductos = cursor1.fetchall()
            cursor1.close()

            cursor2 = connection.cursor()
            cursor2.execute("SELECT ID_CATEGORIA, NOMBRE_CATEGORIA FROM CATEGORIAS")
            categoriasproductos = cursor2.fetchall()
            cursor2.close()

            cursor3 = connection.cursor()
            cursor3.execute("SELECT ID_MARCA, NOMBRE_MARCA FROM MARCAS")
            marcasproductos = cursor3.fetchall()
            cursor3.close()
            connection.close()

            if producto is None:
                # Manejar el caso en el que no se encuentra el producto
                flash('Producto no encontrado', 'danger')
                # Redirige a la página de usuarios
                return redirect(url_for('products'))


            return render_template('editProducts.html', producto=producto, tallasproductos=tallasproductos, categoriasproductos=categoriasproductos, marcasproductos=marcasproductos)


            #return render_template('editProducts.html', producto=producto)

        except Exception as e:
            print("Error al obtener el producto:", str(e))
            flash('Error al obtener el producto', 'danger')
            # Redirige a la página de usuarios
            return redirect(url_for('products'))

    elif request.method == 'POST':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Procesar el formulario de edición y actualizar los datos en la base de datos
            nombre_producto = request.form.get('nombre_producto')
            descripcion = request.form.get('descripcion')
            id_talla = request.form.get('id_talla')
            id_categoria = request.form.get('id_categoria')
            id_marca = request.form.get('id_marca')
            precio = request.form.get('precio')
            existencia = request.form.get('existencia')

            # Obtén la ruta de la imagen actual del producto
            cursor.execute("SELECT imagen FROM productos WHERE ID_PRODUCTO = :id_producto", id_producto=ID_PRODUCTO)
            resultado = cursor.fetchone()
            imagen_actual = resultado[0] if resultado else None

            imagen = request.files.get('imagen')

            if imagen:
                # Guarda la imagen en la ruta static/imgbd
                imagen.save(os.path.join('static/imgbd', imagen.filename))

                # Guarta la imagen en la base de datos empezando por imgbd/ seguido del nombre de la imagen
                ruta_imagen = os.path.join('imgbd/', imagen.filename)
            else:
                ruta_imagen = imagen_actual

            # Consulta SQL para actualizar los datos del Producto
            query = "UPDATE productos SET nombre_producto = :nombre_producto, descripcion = :descripcion, id_talla = :id_talla, id_categoria = :id_categoria, id_marca = :id_marca, precio = :precio, existencia = :existencia, imagen = :imagen WHERE ID_PRODUCTO = :id_producto"

            # Ejecuta la consulta con los nuevos valores y el ID_PRODUCTO como parámetro
            cursor.execute(query, nombre_producto=nombre_producto, descripcion=descripcion, id_talla=id_talla, id_categoria=id_categoria, 
                           id_marca=id_marca, precio=precio, existencia=existencia, imagen=ruta_imagen, id_producto=ID_PRODUCTO)

            # Confirma la transacción
            connection.commit()

            # Cierra el cursor y la conexión
            cursor.close()
            connection.close()

            flash('Producto actualizado con éxito', 'success')
            # Redirige de nuevo a la página de productos
            return redirect(url_for('products'))

        except Exception as e:
            print("Error al actualizar el producto:", str(e))
            flash('Error al actualizar el producto', 'danger')
            # Redirige a la página de productos
            return redirect(url_for('products'))

@app.route('/eliminar_producto/<int:ID_PRODUCTO>', methods=['POST', 'DELETE'])
def eliminar_producto(ID_PRODUCTO):
    if request.method == 'POST' or request.form.get('_method') == 'DELETE':
        # Lógica para eliminar el usuario de la base de datos Oracle
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM PRODUCTOS WHERE ID_PRODUCTO = :ID_PRODCUTO", {
                           'ID_PRODUCTO': ID_PRODUCTO})
            connection.commit()
            flash('PRODCUTO eliminado con éxito', 'success')
        except Exception as e:
            flash('Error al eliminar el usuario', 'danger')
        finally:
            cursor.close()

    return redirect(url_for('products'))

@app.route('/registerUser', methods=['POST'])#Función para registrar un nuevo cliente
def registerUser():
    # Obtén los valores de los campos del formulario
    nombre_cliente = request.form.get('nombre_cliente')
    direccion = request.form.get('direccion')
    nit = request.form.get('nit')
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    confirmarContrasena = request.form.get('confirmarContrasena')

    # Inicializa un mensaje y un tipo de mensaje predeterminado
    message = None
    message_type = 'success'

    # Verifica si las contraseñas coinciden
    if contrasena == confirmarContrasena:
        try:
             # Inicia una transacción
            connection.begin()

            # Inserta los datos en la tabla 'login' para obtener el valor autoincremental de 'id_login'
            cursor = connection.cursor()
            cursor.execute("INSERT INTO login (correo, contrasena, id_rol) VALUES (:correo, :contrasena, :id_rol)",
                           {'correo': correo, 'contrasena': contrasena, 'id_rol': 2})
            
            # Obtiene el valor de 'id_login' generado
            cursor.execute("SELECT id_login FROM login WHERE correo = :correo", {'correo': correo})
            row = cursor.fetchone()
            new_id_login = row[0]

            # Inserta los datos en la tabla 'clientes' usando 'id_login' obtenido
            cursor.execute("INSERT INTO clientes (nombre_cliente, direccion, nit, correo, id_login) VALUES (:nombre_cliente, :direccion, :nit, :correo, :id_login)",
                           {'nombre_cliente': nombre_cliente, 'direccion': direccion, 'nit': nit, 'correo': correo, 'id_login': new_id_login})

            # Confirma la transacción
            connection.commit()

            message = 'Usuario registrado con éxito'

            # Establece los valores de los campos en blanco
            nombre_cliente = ''
            direccion = ''
            nit = ''
            correo = ''
            contrasena = ''
            confirmarContrasena = ''

        except Exception as e:
            # Si ocurre un error, muestra un mensaje de error
            message = 'Error al registrar el usuario: ' + str(e)
            message_type = 'error'
            connection.rollback()
            print(e)

    else:
        # Las contraseñas no coinciden, muestra un mensaje de error al usuario
        message = 'Las contraseñas no coinciden, por favor inténtalo de nuevo'
        message_type = 'error'

    # Devuelve la plantilla de registro con los valores de los campos y el mensaje
    return render_template('register.html', nombre_cliente=nombre_cliente, direccion=direccion, nit=nit, correo=correo, message=message, message_type=message_type)

@app.route('/buscar_productos', methods=['POST'])
def buscar_productos():
    campo_busqueda = request.form.get('campo_busqueda')
    valor_busqueda = request.form.get('valor_busqueda')

    # Consulta SQL parametrizada
    query = "SELECT P.ID_PRODUCTO, P.NOMBRE_PRODUCTO, P.DESCRIPCION, T.NOMBRE_TALLA, C.NOMBRE_CATEGORIA, M.NOMBRE_MARCA, P.PRECIO, P.EXISTENCIA, P.IMAGEN FROM productos P JOIN TALLAS T ON P.ID_TALLA = T.ID_TALLA JOIN CATEGORIAS C ON P.ID_CATEGORIA = C.ID_CATEGORIA JOIN MARCAS M ON P.ID_MARCA = M.ID_MARCA WHERE 1=1"

    # Crear un diccionario de parámetros vacío
    params = {}

    if campo_busqueda == "nombre_producto" and valor_busqueda:
        query += " AND nombre_producto LIKE :nombre_producto"
        params['nombre_producto'] = f'%{valor_busqueda}%'
    elif campo_busqueda == "nombre_talla" and valor_busqueda:
        query += " AND nombre_talla LIKE :nombre_talla"
        params['nombre_talla'] = f'%{valor_busqueda}%'
    elif campo_busqueda == "nombre_categoria" and valor_busqueda:
        query += " AND nombre_categoria LIKE :nombre_categoria"
        params['nombre_categoria'] = f'%{valor_busqueda}%'
    elif campo_busqueda == "nombre_marca" and valor_busqueda:
        query += " AND nombre_marca LIKE :nombre_marca"
        params['nombre_marca'] = f'%{valor_busqueda}%'

    # Ejecutar la consulta y obtener los resultados
    cursor = connection.cursor()
    cursor.execute(query, params)
    productos_encontrados = cursor.fetchall()
    cursor.close()

    # Renderizar la página de resultados de búsqueda con los productos encontrados
    return render_template('resultadosBusquedaProducto.html', productos=productos_encontrados)

@app.route('/agregar/<int:producto_id>')
def agregar_producto(producto_id):
    if 'carrito' not in session:
        session['carrito'] = []
    session['carrito'].append(producto_id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)