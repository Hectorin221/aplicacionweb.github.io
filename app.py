from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Clave secreta para sesiones y seguridad

# Conectar a la base de datos
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear la tabla de usuarios
def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para registrar usuarios
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        flash('Todos los campos son requeridos')
        return redirect(url_for('index'))

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        flash('Usuario registrado con éxito')
    except sqlite3.IntegrityError:
        flash('El nombre de usuario ya está en uso')
    return redirect(url_for('index'))

# Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        flash('Todos los campos son requeridos')
        return redirect(url_for('index'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user is None or not check_password_hash(user['password'], password):
        flash('Credenciales incorrectas')
        return redirect(url_for('index'))

    flash('Inicio de sesión exitoso')
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_table()  # Crear la tabla si no existe
    app.run(debug=True)