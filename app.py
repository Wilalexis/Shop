from datetime import datetime
from flask import Flask, render_template, request, session, flash, redirect, url_for, Response
from flask_wtf import FlaskForm
from wtforms import HiddenField
from flask_paginate import Pagination, get_page_args
from flask_bootstrap import Bootstrap
from reportlab.pdfgen import canvas
import io
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

        cursor = connection.cursor()
        cursor.execute("SELECT id_rol FROM login WHERE correo = :correo AND contrasena = :contrasena", {'correo': correo, 'contrasena': contrasena})
        user = cursor.fetchone() 

        if user:
            id_rol_u = user[0]
            session['id_rol'] = id_rol_u

            # Ahora, recupera y guarda las variables de sesión
            cursor.execute("SELECT id_cliente, nombre_cliente, direccion, nit, correo FROM clientes WHERE correo = :correo", {'correo': correo})
            cliente_info = cursor.fetchone()

            if cliente_info:
                id_cliente,nombre_cliente, direccion, nit, correo = cliente_info
                session['id_cliente'] = id_cliente
                session['nombre_cliente'] = nombre_cliente
                session['direccion'] = direccion
                session['nit'] = nit
                session['correo'] = correo

            if id_rol_u == 1:
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('buy'))
        else:
            cursor.execute("SELECT id_rol FROM usuarios WHERE correo = :correo AND contrasena = :contrasena", {'correo': correo, 'contrasena': contrasena})
            user_rol = cursor.fetchone()

            if user_rol:
                id_rol = user_rol[0]
                session['id_rol'] = id_rol

                if id_rol == 1:
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('buy'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    # Elimina la información de la sesión del usuario
    # Elimina la clave 'id_login' de la sesión si existe
    session.clear()

    # Redirige al usuario a la página de inicio de sesión
    return redirect(url_for('login'))

@app.route('/ingresar_datos_comprador', methods=['GET', 'POST'])
def ingresar_datos_comprador():
    return render_template('formulario_datos_comprador.html')

@app.route('/')  # Ruta para index.html
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
    if 'id_rol' in session:
        id_rol_u = session['id_rol']
    if 'id_rol' in session:
        id_rol = session['id_rol']
        # Realiza cualquier otra lógica que necesites aquí

        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/shoppingcart')  # Ruta para la página de carrito de compras
def shoppingcart():
    return render_template('shoppingcart.html')

@app.route('/buy_show')
def buy_show():
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
        cursor2.execute(
            "SELECT ID_CATEGORIA, NOMBRE_CATEGORIA FROM CATEGORIAS")
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
        return render_template('buy_show.html', productos=productos, tallasproductos=tallasproductos, categoriasproductos=categoriasproductos, marcasproductos=marcasproductos, timestamp=timestamp)

@app.route('/buy')
def buy():
    # Verifica si el usuario tiene una sesión válida y el rol correcto
    if 'id_rol' in session:
        id_rol_u = session['id_rol']
    if 'id_rol' in session:
        id_rol = session['id_rol']
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
        cursor2.execute(
            "SELECT ID_CATEGORIA, NOMBRE_CATEGORIA FROM CATEGORIAS")
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

@app.route('/agregar_al_carrito/<int:ID_PRODUCTO>', methods=['POST'])
def agregar_al_carrito(ID_PRODUCTO):
    if 'id_rol' in session:
        id_rol_u = session['id_rol']
    if 'id_rol' in session:
        id_rol = session['id_rol']
        if 'carrito' not in session:
            session['carrito'] = []
    
        cantidad = int(request.form.get('cantidad', 1))
    
        # Busca si el producto ya está en el carrito
        for item in session['carrito']:
            if item[0] == ID_PRODUCTO:
                item[1] += cantidad
                break
        else:
            session['carrito'].append([ID_PRODUCTO, cantidad])
    
        flash('Producto(s) agregado(s)', 'success')
        return redirect(request.referrer)
    else:
        return redirect(url_for('login'))
    
@app.route('/carrito')
def carrito():
    carrito = []
    total_carrito = 0
    if 'carrito' in session:
        for ID_PRODUCTO, cantidad in session['carrito']:
            cursor = connection.cursor()
            cursor.execute("SELECT P.ID_PRODUCTO, P.NOMBRE_PRODUCTO, P.DESCRIPCION, T.NOMBRE_TALLA, C.NOMBRE_CATEGORIA, M.NOMBRE_MARCA, P.PRECIO, P.EXISTENCIA, P.IMAGEN FROM productos P JOIN TALLAS T ON P.ID_TALLA = T.ID_TALLA JOIN CATEGORIAS C ON P.ID_CATEGORIA = C.ID_CATEGORIA JOIN MARCAS M ON P.ID_MARCA = M.ID_MARCA WHERE id_producto = :id", {'id': ID_PRODUCTO})
            producto = cursor.fetchone()
            carrito.append((producto, cantidad))     

            total_carrito += producto[6] * cantidad
    return render_template('shoppingcart.html', carrito=carrito, total_carrito=total_carrito)

@app.route('/limpiar_carrito')
def limpiar_carrito():
    session.pop('carrito', None)
    return redirect(url_for('buy'))

@app.route('/quitar/<int:ID_PRODUCTO>')
def quitar(ID_PRODUCTO):
    if 'carrito' in session:
        for item in session['carrito']:
            if item[0] == ID_PRODUCTO:
                session['carrito'].remove(item)
                flash('Producto eliminado del carrito', 'success')
                break
        else:
            flash('Producto no encontrado en el carrito', 'danger')

    return redirect(url_for('carrito'))

@app.route('/admin/category')  # ruta para la pagina categorias
def category():
    if 'id_rol' in session:
        id_rol_u = session['id_rol']
    if 'id_rol' in session:
        id_rol = session['id_rol']
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

        # obtiene las categorias actuales
        category_to_display = categorias[start:end]

        # Crea un objeto de paginación
        pagination = Pagination(page=page, per_page=per_page, total=total_category,
                                css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} categorias')

        return render_template('category.html', categorias=category_to_display, pagination=pagination)
    else:
        return redirect(url_for('login'))

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

# ruta para editar categoria
@app.route('/editCategories/<int:ID_CATEGORIA>', methods=['GET', 'POST'])
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
            cursor.execute(query, nombre_categoria=nombre_categoria,
                           id_categoria=ID_CATEGORIA)

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

# ruta para eliminar categoria
@app.route('/eliminar_categoria/<int:ID_CATEGORIA>', methods=['POST', 'DELETE'])
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
    # Verifica si el usuario tiene una sesión válida y el rol correcto
    if 'id_rol' in session:
        id_rol_u = session['id_rol']
    if 'id_rol' in session:
        id_rol = session['id_rol']
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

        # obtiene las clientes actuales
        clients_to_display = clientes[start:end]

        # Crea un objeto de paginación
        pagination = Pagination(page=page, per_page=per_page, total=total_clients,
                                css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} clientes')

        return render_template('client.html', clientes=clients_to_display, pagination=pagination, login=login)
    else:
        return redirect(url_for('login'))

@app.route('/crear_cliente', methods=['POST'])
def crear_client():
    nombre = request.form.get('nombre')
    direccion = request.form.get('direccion')
    nit = request.form.get('nit')
    correo = request.form.get('correo')
    contrasena = request.form.get('contrasena')
    id_cliente = request.form.get('id_cliente')

    # Preparar la consulta SQL
    sql = "INSERT INTO cliente (nombre, direccion, nit, correo, contrasena, id_cliente) VALUES (:nombre, :direccion, :nit, :correo, :contrasena, :id_login)"

    # Ejecutar la consulta
    cursor = connection.cursor()
    cursor.execute(sql, {'nombre': nombre, 'direccion': direccion, 'nit': nit,
                   'correo': correo, 'contrasena': contrasena, 'id_cliente': id_cliente})
    connection.commit()

    # variable de sesion
    session['mensaje'] = 'cliente agregado correctamente'

    return redirect(url_for('client'))

@app.route('/eliminar_client/<int:ID_CLIENTE>', methods=['POST', 'DELETE'])
def eliminar_client(ID_CLIENTE):
    if request.method == 'POST' or request.form.get('_method') == 'DELETE':
        # Lógica para eliminar el usuario de la base de datos Oracle
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM CLIENTE WHERE ID_CLIENTE = :ID_CLIENTE", {
                           'ID_CLIENTE': ID_CLIENTE})
            connection.commit()
            flash('cliente eliminado con éxito', 'success')
        except Exception as e:
            flash('Error al eliminar el cliente', 'danger')
        finally:
            cursor.close()

    return redirect(url_for('client'))

@app.route('/editClient/<int:ID_CLIENTE>', methods=['GET', 'POST'])
def editClient(ID_CLIENTE):
    if request.method == 'GET':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Consulta SQL para obtener los datos del usuario por su ID
            query = "SELECT C.id_cliente,C.nombre_cliente,C.direccion,C.nit,C.correo,L.contrasena FROM clientes C JOIN login L ON C.id_login = L.id_login WHERE C.ID_CLIENTE = :id_cliente"

            # Ejecuta la consulta con el ID_USUARIO como parámetro
            cursor.execute(query, id_cliente=ID_CLIENTE)

            # Obtiene los datos del usuario
            cliente = cursor.fetchone()

            # Cierra el cursor y la conexión
            cursor.close()

            cursor1 = connection.cursor()
            cursor1.execute("SELECT ID_LOGIN, CONTRASENA FROM LOGIN")
            roles = cursor1.fetchall()
            cursor1.close()
            connection.close()

            if cliente is None:
                # Manejar el caso en el que no se encuentra el usuario
                flash('Cliente no encontrado', 'danger')
                # Redirige a la página de usuarios
                return redirect(url_for('client'))

            return render_template('editClient.html', cliente=cliente, roles=roles)

        except Exception as e:
            print("Error al obtener el cliente:", str(e))
            flash('Error al obtener el cliente', 'danger')
            # Redirige a la página de usuarios
            return redirect(url_for('client'))

    elif request.method == 'POST':
        try:
            # Realiza la conexión a tu base de datos Oracle
            dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
            connection = cx_Oracle.connect(
                user='USR_DLSOCKS', password='admin', dsn=dsn)

            # Crea un cursor
            cursor = connection.cursor()

            # Procesar el formulario de edición y actualizar los datos en la base de datos
            nombre_cliente = request.form.get('nombre_cliente')
            direccion = request.form.get('direccion')
            nit = request.form.get('nit')
            correo = request.form.get('correo')
            contrasena = request.form.get('contrasena')
            id_login = request.form.get('id_login')

            # Consulta SQL para actualizar los datos del usuario
            query = "UPDATE CLIENTES SET NOMBRE_CLIENTE = :nombre_cliente, direccion = :direccion, nit = :nit, correo = :correo WHERE ID_CLIENTE = :id_cliente"

            # Ejecuta la consulta con los nuevos valores y el ID_USUARIO como parámetro
            cursor.execute(query, nombre_cliente=nombre_cliente, direccion=direccion, nit=nit, correo=correo, id_cliente=ID_CLIENTE)

            # Confirma la transacción
            connection.commit()

            # Cierra el cursor y la conexión
            cursor.close()
            connection.close()

            flash('Cliente actualizado con éxito', 'success')
            # Redirige de nuevo a la página de usuarios
            return redirect(url_for('client'))

        except Exception as e:
            print("Error al actualizar el cliente:", str(e))
            flash('Error al actualizar el cliente', 'danger')
            # Redirige a la página de usuarios
            return redirect(url_for('client'))

@app.route('/admin/marc')
def marc():
    # Verifica si el usuario tiene una sesión válida y el rol correcto
    if 'id_rol' in session:
        id_rol_u = session['id_rol']
    if 'id_rol' in session:
        id_rol = session['id_rol']
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

        # obtiene las marcas actuales
        brandas_to_display = marcas[start:end]

        # Crea un objeto de paginación
        pagination = Pagination(page=page, per_page=per_page, total=total_brands,
                                css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} marcas')

        return render_template('marc.html', marcas=brandas_to_display, pagination=pagination)

    else:
        return redirect(url_for('login'))

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

# ruta para editar marcas
@app.route('/editBrands/<int:ID_MARCA>', methods=['GET', 'POST'])
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

# ruta para eliminar marcas
@app.route('/eliminar_marca/<int:ID_MARCA>', methods=['POST', 'DELETE'])
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

@app.route('/admin/sizes')  # Ruta para la pagina de tallas
def sizes():
    # Verifica si el usuario tiene una sesión válida y el rol correcto
    if 'id_rol' in session:
        id_rol_u = session['id_rol']
    if 'id_rol' in session:
        id_rol = session['id_rol']
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

        # obtiene las categorias actuales
        sizes_to_display = tallas[start:end]

        # Crea un objeto de paginación
        pagination = Pagination(page=page, per_page=per_page, total=total_sizes,
                                css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} tallas')

        return render_template('sizes.html', tallas=sizes_to_display, pagination=pagination)
    else:
        return redirect(url_for('login'))

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

# ruta para editar tallas
@app.route('/editSizes/<int:ID_TALLA>', methods=['GET', 'POST'])
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
            cursor.execute(query, nombre_talla=nombre_talla,
                           id_tallas=ID_TALLA)

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

# ruta para eliminar Tallas
@app.route('/eliminar_talla/<int:ID_TALLA>', methods=['POST', 'DELETE'])
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
    # Verifica si el usuario tiene una sesión válida y el rol correcto
    if 'id_rol' in session:
        id_rol_u = session['id_rol']
    if 'id_rol' in session:
        id_rol = session['id_rol']
        cursor = connection.cursor()
        cursor.execute(
            "SELECT U.ID_USUARIO, U.NOMBRE, U.CORREO, U.CONTRASENA, R.NOMBRE FROM USUARIOS U JOIN ROLES R ON U.ID_ROL = R.ID_ROL")
        usuarios = cursor.fetchall()
        cursor.close()

        cursor1 = connection.cursor()
        cursor1.execute("SELECT ID_ROL, NOMBRE FROM ROLES")
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
    else:
        return redirect(url_for('login'))

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
            query = "SELECT U.ID_USUARIO, U.NOMBRE, U.CORREO, U.CONTRASENA, R.NOMBRE FROM USUARIOS U JOIN ROLES R ON U.ID_ROL = R.ID_ROL WHERE U.ID_USUARIO = :id_usuario"

            # Ejecuta la consulta con el ID_USUARIO como parámetro
            cursor.execute(query, id_usuario=ID_USUARIO)

            # Obtiene los datos del usuario
            usuario = cursor.fetchone()

            # Cierra el cursor y la conexión
            cursor.close()

            cursor1 = connection.cursor()
            cursor1.execute("SELECT ID_ROL, NOMBRE FROM ROLES")
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
    # Verifica si el usuario tiene una sesión válida y el rol correcto
    if 'id_rol' in session:
        id_rol_u = session['id_rol']
    if 'id_rol' in session:
        id_rol = session['id_rol']
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
        pagination = Pagination(page=page, per_page=per_page, total=total_products,
                                css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} productos')

        return render_template('products.html', productos=products_to_display, tallasproductos=tallasproductos, categoriasproductos=categoriasproductos, marcasproductos=marcasproductos, pagination=pagination)
    else:
        return redirect(url_for('login'))
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
            cursor2.execute(
                "SELECT ID_CATEGORIA, NOMBRE_CATEGORIA FROM CATEGORIAS")
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

            # return render_template('editProducts.html', producto=producto)

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
            cursor.execute(
                "SELECT imagen FROM productos WHERE ID_PRODUCTO = :id_producto", id_producto=ID_PRODUCTO)
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

# Función para registrar un nuevo cliente
@app.route('/registerUser', methods=['POST'])
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
            cursor.execute("SELECT id_login FROM login WHERE correo = :correo", {
                           'correo': correo})
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
    query = "SELECT P.ID_PRODUCTO, P.NOMBRE_PRODUCTO, P.DESCRIPCION, T.NOMBRE_TALLA, C.NOMBRE_CATEGORIA, M.NOMBRE_MARCA, P.PRECIO, P.EXISTENCIA, P.IMAGEN FROM productos P JOIN TALLAS T ON P.ID_TALLA = T.ID_TALLA JOIN CATEGORIAS C ON P.ID_CATEGORIA = C.ID_CATEGORIA JOIN MARCAS M ON P.ID_MARCA = M.ID_MARCA"

    # Crear un diccionario de parámetros vacío
    params = {}

    if campo_busqueda == "nombre_producto" and valor_busqueda:
        query += " WHERE 1=1 AND UPPER(nombre_producto) LIKE UPPER(:nombre_producto)"
        params['nombre_producto'] = f'%{valor_busqueda}%'
    elif campo_busqueda == "nombre_categoria" and valor_busqueda:
        query += " WHERE 1=1 AND UPPER(nombre_categoria) LIKE UPPER(:nombre_categoria)"
        params['nombre_categoria'] = f'%{valor_busqueda}%'
    elif campo_busqueda == "nombre_talla" and valor_busqueda:
        query += " WHERE 1=1 AND UPPER(nombre_talla) LIKE UPPER(:nombre_talla)"
        params['nombre_talla'] = f'%{valor_busqueda}%'       
    elif campo_busqueda == "nombre_marca" and valor_busqueda:
        query += " WHERE 1=1 AND UPPER(nombre_marca) LIKE UPPER(:nombre_marca)"
        params['nombre_marca'] = f'%{valor_busqueda}%'
    elif (campo_busqueda or valor_busqueda) or (campo_busqueda == "nada" and valor_busqueda):
        query += " ORDER BY P.ID_PRODUCTO DESC"

    # Ejecutar la consulta y obtener los resultados
    cursor = connection.cursor()
    cursor.execute(query, params)
    productos_encontrados = cursor.fetchall()
    cursor.close()

    # Renderizar la página de resultados de búsqueda con los productos encontrados
    return render_template('resultadosBusquedaProducto.html', productos=productos_encontrados)

@app.route('/admin/receipts')
def receipts():
    cursor = connection.cursor()
    cursor.execute("select r.no_recibo, r.fecha_emision, c.nombre_cliente from recibos r join clientes c on r.id_cliente = c.id_cliente")
    recibos = cursor.fetchall()
    cursor.close()

    cursor1 = connection.cursor()
    cursor1.execute("SELECT id_cliente, nombre_cliente FROM clientes")
    clientes = cursor1.fetchall()
    cursor1.close()

    # Verificar si los parámetros 'page' y 'per_page' se pasan en la solicitud GET
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=5)

    # Supongamos que tienes una lista de usuarios llamada 'marcas'
    total_recibos = len(recibos)

    # Calcula el índice de inicio y final para la página actual
    start = (page - 1) * per_page
    end = start + per_page

    # obtiene las marcas actuales
    brandas_to_display = recibos[start:end]

    # Crea un objeto de paginación
    pagination = Pagination(page=page, per_page=per_page, total=total_recibos,
                            css_framework='bootstrap4', display_msg='Mostrando {start} - {end} de {total} recibos')

    return render_template('receipts.html', recibos=brandas_to_display, pagination=pagination, clientes=clientes)

@app.route('/crear_recibo', methods=['POST'])
def crear_recibo():
    fecha_emision = datetime.now()
    fecha_hoy = fecha_emision.strftime('%d-%m-%Y')
    id_cliente = request.form.get('id_cliente')
    nit = request.form.get('nit')
    direccion = request.form.get('direccion')
    nombre = request.form.get('nombre_cliente')

    # Preparar la consulta SQL para insertar el recibo
    sql_recibo = "INSERT INTO RECIBOS (FECHA_EMISION, ID_CLIENTE, NIT, DIRECCION, NOMBRE) VALUES (:fecha_emision, :id_cliente, :nit, :direccion, :nombre_cliente)"

    # Ejecutar la consulta para insertar el recibo
    cursor = connection.cursor()
    cursor.execute(sql_recibo, {'fecha_emision': fecha_hoy, 'id_cliente': id_cliente, 'nit': nit, 'direccion': direccion, 'nombre_cliente': nombre})
    connection.commit()

    # Obtener el ID del recibo recién insertado
    cursor.execute("SELECT RECIBOS_SEQ.CURRVAL FROM DUAL")
    recibo_id = cursor.fetchone()[0]

    # Insertar los detalles del carrito en la tabla DETALLES_RECIBO
    if 'carrito' in session:
        for producto_id, cantidad in session['carrito']:
            cursor.execute("SELECT P.PRECIO FROM PRODUCTOS P WHERE P.ID_PRODUCTO = :producto_id", {'producto_id': producto_id})
            precio_unitario = cursor.fetchone()[0]
            
            sql_detalles_recibo = "INSERT INTO DETALLES_RECIBO (NO_RECIBO, ID_PRODUCTO, CANTIDAD, P_UNITARIO) VALUES (:no_recibo, :id_producto, :cantidad, :precio_unitario)"
            cursor.execute(sql_detalles_recibo, {'no_recibo': recibo_id, 'id_producto': producto_id, 'cantidad': cantidad, 'precio_unitario': precio_unitario})
            connection.commit()

    return redirect(url_for('generar_recibo'))

def obtener_detalles_carrito():
    if 'carrito' in session:
        detalles = []
        for producto_id, cantidad in session['carrito']:
            cursor = connection.cursor()
            cursor.execute("SELECT P.NOMBRE_PRODUCTO, P.PRECIO FROM PRODUCTOS P WHERE P.ID_PRODUCTO = :producto_id", {'producto_id': producto_id})
            producto = cursor.fetchone()
            if producto:
                concepto = producto[0]
                precio = producto[1]
                total = precio * cantidad
                detalles.append((cantidad, concepto, precio, total))
        return detalles
    return []

@app.route('/generar_recibo', methods=['GET', 'POST'])
def generar_recibo():
    # Datos de ejemplo para el recibo (puedes reemplazar esto con datos de tu base de datos)
    fecha = datetime.now()
    fecha_hoy = fecha.strftime('%d-%m-%Y')
    id_cliente = request.form.get('id_cliente')
    nit = request.form.get('nit')
    direccion = request.form.get('direccion')
    nombre = request.form.get('nombre_cliente')

    # Preparar la consulta SQL para insertar el recibo
    sql_recibo = "INSERT INTO RECIBOS (ID_CLIENTE, NIT, DIRECCION, NOMBRE) VALUES (:id_cliente, :nit, :direccion, :nombre_cliente)"

    # Ejecutar la consulta para insertar el recibo
    cursor = connection.cursor()
    cursor.execute(sql_recibo, {'id_cliente': id_cliente, 'nit': nit, 'direccion': direccion, 'nombre_cliente': nombre})
    connection.commit()

    # Obtener el ID del recibo recién insertado
    cursor.execute("SELECT RECIBOS_SEQ.CURRVAL FROM DUAL")
    recibo_id = cursor.fetchone()[0]

    # Insertar los detalles del carrito en la tabla DETALLES_RECIBO
    if 'carrito' in session:
        for producto_id, cantidad in session['carrito']:
            cursor.execute("SELECT P.PRECIO FROM PRODUCTOS P WHERE P.ID_PRODUCTO = :producto_id", {'producto_id': producto_id})
            precio_unitario = cursor.fetchone()[0]
            
            sql_detalles_recibo = "INSERT INTO DETALLES_RECIBO (NO_RECIBO, ID_PRODUCTO, CANTIDAD, P_UNITARIO) VALUES (:no_recibo, :id_producto, :cantidad, :precio_unitario)"
            cursor.execute(sql_detalles_recibo, {'no_recibo': recibo_id, 'id_producto': producto_id, 'cantidad': cantidad, 'precio_unitario': precio_unitario})
            connection.commit()

    # Obtener detalles de los productos en el carrito
    detalles_carrito = obtener_detalles_carrito()  # Implementa esta función para obtener los detalles del carrito

    # Crear el PDF del recibo usando ReportLab
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    # Configurar el tamaño de la página
    width, height = 400, 400
    p.setPageSize((width, height))

    # Agregar encabezado
    p.setFont("Helvetica", 12)
    p.drawString(10, height - 20, "Recibo de compra")
    p.drawString(10, height - 40, "Di Socks GT")

    # Agregar una imagen al recibo (ajusta la ruta de la imagen)
    imagen_path = 'static/img/logo_recibo.jpg'
    p.drawImage(imagen_path, 350, 350, 50, 50)

    # Agregar información del negocio
    p.setFont("Helvetica", 10)
    p.drawString(10, height - 80, f"Vendido a: {nombre}")
    p.drawString(10, height - 90, f"Dirección: {direccion}")
    p.drawString(250, height - 80, f"Fecha: {fecha_hoy}")
    p.drawString(250, height - 90, f"No. de recibo: {recibo_id}")

    # Agregar línea separadora
    p.line(10, height - 100, width - 10, height - 100)

    p.drawString(10, height - 120, f"Cantidad")
    p.drawString(120, height - 120, f"Concepto")
    p.drawString(250, height - 120, f"Precio")
    p.drawString(350, height - 120, f"Total")

    # Agregar detalles del carrito al recibo
    y_position = height - 140
    total_compra = 0
    for detalle in detalles_carrito:
        cantidad, concepto, precio, total = detalle
        p.drawString(10, y_position, str(cantidad))
        p.drawString(120, y_position, concepto)
        p.drawString(250, y_position, str(precio))
        p.drawString(350, y_position, str(total))
        total_compra += precio * cantidad
        y_position -= 10  # Ajusta la posición vertical
    p.line(10, height - 325, width - 10, height - 325)
    p.drawString(300, 50, "Total: "+str(total_compra))
    # Guardar el PDF
    p.showPage()
    p.save()

    # Preparar el PDF para ser descargado
    buffer.seek(0)
    response = Response(buffer)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=recibo.pdf'

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
