import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    email TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    password TEXT NOT NULL,
    salt TEXT NOT NULL,
    cedula TEXT NOT NULL,
    celular TEXT NOT NULL
)
''')

conn.commit()
conn.close()