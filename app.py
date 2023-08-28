from flask import Flask, render_template
import cx_Oracle

app = Flask(__name__, static_folder='static', template_folder='templates')

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

if __name__ == '__main__':
    app.run(debug=True)


