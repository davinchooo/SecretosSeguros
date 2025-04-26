from datetime import datetime, timedelta
from time import time
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
from functools import wraps

with open("secret.key", "rb") as f:
    SECRET_KEY = f.read()

cipher = Fernet(SECRET_KEY)

SECRETS_FILE = "secrets.json"

MAX_INTENTOS = 3  # Número máximo de intentos fallidos
TIEMPO_BLOQUEO = 5 * 60  # 5 minutos (en segundos)
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
# app.config['SESSION_COOKIE_SECURE'] = False

intentos_fallidos = {}  # Estructura: { "email": { "intentos": 0, "tiempoBloqueo": 0 } }

def login_requerido(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

# @app.before_request
# def validar_sesion():
#     ruta = request.endpoint
#     print("Endpoint actual:", ruta)
#     print("Sesión:", session)
#     rutas_publicas = {'login', 'create_record', 'secrets_pages', 'api_logout'}  # Agrega aquí tus rutas abiertas
#     if 'email' in session:
#         session.modified = True  # Actualiza el "último acceso"
#     elif ruta not in rutas_publicas:
#         return redirect(url_for('login'))
#     print("Sesión:", session)
    
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
    email = normalize_input(data.get('email'))
    nombre = normalize_input(data.get('nombre'))
    apellido = normalize_input(data.get('Apellidos'))
    password = data.get('password')
    cedula = data.get('cedula')
    celular = data.get('celular')

    errores = []
    if not validate_email(email):
        errores.append("Email inválido")
    if not validate_cedula(cedula):
        errores.append("Cédula inválida")
    if not validate_celular(celular):
        errores.append("Celular inválido")
    if not validate_name(nombre):
        errores.append("Nombre inválido")
    if not validate_name(apellido):
        errores.append("Apellido inválido")
    if not validate_pswd(password):
        errores.append("Contraseña inválida. Agrega mayusculas, minúsculas, números y caracteres especiales. Mínimo 8 caracteres y máximo 35.")
    if errores:
        print("Errores en validación:", errores)
        return render_template('form.html', error=errores)
        

    hash_pd, salt = hash_with_salt(password, None)

    insert_user({
        'email': email,
        'nombre': nombre,
        'apellido': apellido,
        'password': hash_pd,
        'salt': salt.hex(),
        'cedula': cipher.encrypt(cedula.encode()).decode(),
        'celular': celular,
    })

    return redirect("/login")




# Endpoint para el login
@app.route('/api/login', methods=['POST'])
def api_login():
    email = normalize_input(request.form['email'])
    password = request.form['password']

    user = get_user_by_email(email)
    error = "Credenciales inválidas"

    # Verifica si el usuario está temporalmente bloqueado
    estado = intentos_fallidos.get(email, {"intentos": 0, "tiempoBloqueo": 0})
    tiempo_actual = time()

    if estado["tiempoBloqueo"] > tiempo_actual:
        tiempo_restante = int((estado["tiempoBloqueo"] - tiempo_actual) / 60)
        return render_template('login.html', error=f"Usuario bloqueado. Intenta nuevamente en {tiempo_restante} minutos.")

    if not user or not compare_salt(password, user["password"], user["salt"]):
        estado["intentos"] += 1
        if estado["intentos"] >= MAX_INTENTOS:
            estado["tiempoBloqueo"] = tiempo_actual + TIEMPO_BLOQUEO
            estado["intentos"] = 0  # reiniciar contador
            intentos_fallidos[email] = estado
            return render_template('login.html', error="Demasiados intentos fallidos. Usuario bloqueado por 5 minutos.")
        intentos_fallidos[email] = estado
        return render_template('login.html', error=error)

    # Login exitoso, reiniciar estado
    if email in intentos_fallidos:
        del intentos_fallidos[email]

    if compare_salt(password, user["password"], user["salt"]):
        # session.permanent = True   # <- importante
        session['email'] = email
        return redirect(url_for('secrets_page'))



# Página principal del menú del cliente
# @app.route('/customer_menu')
# def customer_menu():

#     db = read_db("db.txt")

#     transactions = read_db("transaction.txt")
#     current_balance = 100
#     last_transactions = []
#     message = request.args.get('message', '')
#     error = request.args.get('error', 'false').lower() == 'true'
#     return render_template('customer_menu.html',
#                            message=message,
#                            nombre="",
#                            balance=current_balance,
#                            last_transactions=last_transactions,
#                            error=error,)


# Endpoint para leer un registro
# @app.route('/records', methods=['GET'])
# def read_record():
#     db = read_db("db.txt")
#     return render_template('records.html', users=db)

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
@login_requerido
def secrets_page():
    secrets = read_secrets()
    decrypted = {k: cipher.decrypt(v.encode()).decode() for k, v in secrets.items()}
    return render_template("secrets.html", secrets=decrypted)

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return redirect(url_for('login'))