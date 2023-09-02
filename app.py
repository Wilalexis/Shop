from flask import Flask, render_template, request, session,flash, redirect, url_for
import cx_Oracle

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'admin'  # clave secreta

# Configura la conexión a Oracle
dsn = cx_Oracle.makedsn(host='localhost', port=1521, sid='xe')
connection = cx_Oracle.connect(user='USR_DLSOCKS', password='admin', dsn=dsn)

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
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('users.html',usuarios=usuarios)

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
    rol = request.form.get('rol')

    # Preparar la consulta SQL
    sql = "INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES (:nombre, :correo, :contrasena, :rol)"

    # Ejecutar la consulta
    cursor = connection.cursor()
    cursor.execute(sql, {'nombre': nombre, 'correo': correo, 'contrasena': contrasena, 'rol': rol})
    connection.commit()

    #variable de sesion
    session['mensaje'] = 'Usuario agregado correctamente'   

    return redirect(url_for('users'))


if __name__ == '__main__':
    app.run(debug=True)


