import sqlite3

DB_FILE = "database.db"

def get_user_by_email(email):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def insert_user(user_data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (email, nombre, apellido, password, salt, cedula, celular)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_data['email'],
        user_data['nombre'],
        user_data['apellido'],
        user_data['password'],
        user_data['salt'],
        user_data['cedula'],
        user_data['celular']
    ))
    conn.commit()
    conn.close()