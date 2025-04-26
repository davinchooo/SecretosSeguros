from datetime import datetime
import time
from app.validation import *
from app.reading import *
from flask import request, jsonify, redirect, url_for, render_template, session, make_response, Flask
from app import app
from cryptography.fernet import Fernet
import json
import os
from Crypto.Protocol.KDF import scrypt
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

SECRET_KEY = Fernet.generate_key()
cipher = Fernet(SECRET_KEY)

SECRETS_FILE = "secrets.json"

def hash_with_salt(password, salt):
    if salt is None:
        salt = get_random_bytes(16)
    else:
        salt = bytes.fromhex(salt)

    # Deriva una clave usando scrypt
    key = scrypt(password.encode(), salt, key_len=32, N=2**14, r=8, p=1)

    # Crea un hash SHA-256 de la clave derivada
    hash_obj = SHA256.new(key)
    hash_value = hash_obj.hexdigest()

    return hash_value, salt

def compare_salt(password, password_db, salt_db):
    hash_value2 = hash_with_salt(password, salt_db)[0]
    if (hash_value2 == password_db):
        return True
    else:
        return False

def read_secrets():
    if not os.path.exists(SECRETS_FILE):
        return {}
    with open(SECRETS_FILE, "r") as f:
        return json.load(f)

def write_secrets(data):
    with open(SECRETS_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route('/api/users', methods=['POST'])
def create_record():
    data = request.form
    email = data.get('email')
    nombre = data.get('nombre')
    apellido = data.get('Apellidos')
    password = data.get('password')
    cedula = data.get('cedula')
    celular = data.get('celular')
    errores = []
    print(data)
    # Validaciones
    if not validate_email(email):
        errores.append("Email inválido")
    #if not validate_pswd(password):
    #    errores.append("Contraseña inválida")
    if not validate_cedula(cedula):
        errores.append("cedula inválido")
    if not validate_celular(celular):
        errores.append("Usuario inválido")
    if not validate_name(nombre):
        errores.append("Nombre inválido")
    if not validate_name(apellido):
        errores.append("Apellido inválido")

    if errores:
        return render_template('form.html', error=errores)

    email = normalize_input(email)

    db = read_db("db.txt")
    hash_pd, salt = hash_with_salt(password, None)
    db[email] = {
        'nombre': normalize_input(nombre),
        'apellido': normalize_input(apellido),
        'password': hash_pd,
        "salt": salt.hex(),
        "cedula": cedula,
        "celular": celular,
    }

    write_db("db.txt", db)
    return redirect("/login")



# Endpoint para el login
@app.route('/api/login', methods=['POST'])
def api_login():
    email = normalize_input(request.form['email'])
    password = normalize_input(request.form['password'])

    db = read_db("db.txt")
    error = "Credenciales inválidas"

    if email not in db:
        return render_template('login.html', error=error)

    password_db = db.get(email)["password"]
    salt_db = db.get(email)["salt"]

    if compare_salt(password, password_db, salt_db):
        #session['email'] = email
        return redirect(url_for('secrets'))
    else:
        return render_template('login.html', error=error)


# Página principal del menú del cliente
@app.route('/customer_menu')
def customer_menu():

    db = read_db("db.txt")

    transactions = read_db("transaction.txt")
    current_balance = 100
    last_transactions = []
    message = request.args.get('message', '')
    error = request.args.get('error', 'false').lower() == 'true'
    return render_template('customer_menu.html',
                           message=message,
                           nombre="",
                           balance=current_balance,
                           last_transactions=last_transactions,
                           error=error,)


# Endpoint para leer un registro
@app.route('/records', methods=['GET'])
def read_record():
    db = read_db("db.txt")
    return render_template('records.html', users=db)

@app.route("/api/secrets", methods=["GET"])
def list_secrets():
    secrets = read_secrets()
    decrypted = {k: cipher.decrypt(v.encode()).decode() for k, v in secrets.items()}
    return jsonify(decrypted)

@app.route("/api/secrets", methods=["POST"])
def add_secret():
    data = request.json
    name = data.get("name")
    value = data.get("value")
    if not name or not value:
        return jsonify({"error": "Falta nombre o valor"}), 400
    secrets = read_secrets()
    secrets[name] = cipher.encrypt(value.encode()).decode()
    write_secrets(secrets)
    return jsonify({"message": "Secreto guardado correctamente"})

@app.route("/secrets")
def secrets_page():
    secrets = read_secrets()
    decrypted = {k: cipher.decrypt(v.encode()).decode() for k, v in secrets.items()}
    return render_template("secrets.html", secrets=decrypted)

@app.route("/api/logout", methods=["POST"])
def api_logout():
    #session.pop('email', None)
    return redirect(url_for('index'))