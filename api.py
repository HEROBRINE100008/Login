from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # Permite peticiones desde cualquier origen

# Configuración de la base de datos
DATABASE = 'python.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acceso a columnas por nombre
    return conn

# Crear tabla si no existe
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS Login (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT UNIQUE NOT NULL,
                passwords TEXT NOT NULL
            )
        ''')
        db.commit()

# Endpoint de registro
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT * FROM Login WHERE user = ?", (username,))
        if cursor.fetchone():
            return jsonify({"error": "El usuario ya existe"}), 409
        
        # Crear nuevo usuario
        cursor.execute(
            "INSERT INTO Login (user, passwords) VALUES (?, ?)",
            (username, password)
        )
        db.commit()
        return jsonify({"message": "Usuario registrado exitosamente"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint de login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM Login WHERE user = ? AND passwords = ?",
            (username, password)
        )
        user = cursor.fetchone()
        
        if user:
            return jsonify({
                "message": "Login exitoso",
                "user": dict(user)  # Convierte la fila a diccionario
            }), 200
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para eliminar usuario
@app.route('/user/<username>', methods=['DELETE'])
def delete_user(username):
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verificar si el usuario existe
        cursor.execute("SELECT * FROM Login WHERE user = ?", (username,))
        if not cursor.fetchone():
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Eliminar usuario
        cursor.execute("DELETE FROM Login WHERE user = ?", (username,))
        db.commit()
        return jsonify({"message": f"Usuario '{username}' eliminado"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()  # Asegura que la tabla exista
    app.run(debug=True, port=5000)