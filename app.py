from flask import Flask, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')

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


if __name__ == '__main__':
    app.run(debug=True)

#Prueba 1

