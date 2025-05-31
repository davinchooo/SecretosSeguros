from time import time
from app.validation import *
from flask import request, jsonify, redirect, url_for, render_template, session
from app import app
from app.models import db, Secret, Usuario
from app.correo import enviar_alerta_correo, enviar_codigo_verificacion
from cryptography.fernet import Fernet
from Crypto.Protocol.KDF import scrypt
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from functools import wraps
from dotenv import load_dotenv
import json, os, random

load_dotenv()  # Carga las variables desde .env
        
def mfa_requerido(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not session.get("mfa_verified"):
            return redirect(url_for("api_verify"))
        return f(*args, **kwargs)
    return wrap

key = os.environ.get("SECRET_KEY")
if not key:
    raise ValueError("SECRET_KEY no está definida en el entorno")

cipher = Fernet(key.encode())

SECRETS_FILE = "secrets.json"

MAX_INTENTOS = 3  # Número máximo de intentos fallidos
TIEMPO_BLOQUEO = 5 * 60  # 5 minutos (en segundos)

intentos_fallidos = {}  # Estructura: { "email": { "intentos": 0, "tiempoBloqueo": 0 } }

def login_requerido(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

    
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
    # Verificar si ya existe un usuario con ese correo, celular o cédula
    if validate_duplicate(email, cedula, celular):
        errores.append("Ya existe un usuario con ese correo, celular o cédula.")
    if errores:
        print("Errores en validación:", errores)
        return render_template('form.html', error=errores)
        
    hash_pd, salt = hash_with_salt(password, None)

    # Convertimos salt a hex una sola vez
    salt_hex = salt.hex()

    # Permutamos la contraseña
    password_lista = list(password)
    mitad = int(len(password) / 2)
    password_lista[mitad], password_lista[-1] = password_lista[-1], password_lista[mitad]
    password_ver = ''.join(password_lista)

    # Segunda verificación
    hash_pd2 = hash_with_salt(password_ver, salt_hex)[0]

    nuevo_usuario = Usuario(
        email=email,
        nombre=nombre,
        apellido=apellido,
        password=hash_pd,
        password_ver=hash_pd2,
        salt=salt_hex,
        cedula=cipher.encrypt(cedula.encode()).decode(),
        celular=celular
    )

    db.session.add(nuevo_usuario)
    db.session.commit()
    
    asunto = "🎉 Registro exitoso en Secretos Seguros"
    cuerpo = f"Hola {nombre},\n\nSe ha creado una cuenta con este correo ({email}) en la plataforma de Secretos Seguros.\n\nSi no fuiste tú, por favor contacta con soporte."
    enviar_alerta_correo(email, asunto, cuerpo)

    return redirect("/login")




# Endpoint para el login
@app.route('/api/login', methods=['POST'])
def api_login():
    email = normalize_input(request.form['email'])
    password = request.form['password']

    user = Usuario.query.filter_by(email=email).first()
    error = "Credenciales inválidas"

    # Verifica si el usuario está temporalmente bloqueado
    estado = intentos_fallidos.get(email, {"intentos": 0, "tiempoBloqueo": 0})
    tiempo_actual = time()

    if estado["tiempoBloqueo"] > tiempo_actual:
        tiempo_restante = int((estado["tiempoBloqueo"] - tiempo_actual) / 60)
        return render_template('login.html', error=f"Usuario bloqueado. Intenta nuevamente en {tiempo_restante} minutos.")

    # Si el usuario no existe o falla el primer hash
    if not user or not compare_salt(password, user.password, user.salt):
        estado["intentos"] += 1
        if estado["intentos"] >= MAX_INTENTOS:
            estado["tiempoBloqueo"] = tiempo_actual + TIEMPO_BLOQUEO
            estado["intentos"] = 0  # reiniciar contador
            intentos_fallidos[email] = estado
            return render_template('login.html', error="Demasiados intentos fallidos. Usuario bloqueado por 5 minutos.")
        intentos_fallidos[email] = estado
        return render_template('login.html', error=error)

    # Segunda verificación con contraseña permutada
    password_lista = list(password)
    mitad = int(len(password) / 2)
    password_lista[mitad], password_lista[-1] = password_lista[-1], password_lista[mitad]
    password_ver = ''.join(password_lista)

    if not compare_salt(password_ver, user.password_ver, user.salt):
        return render_template('login.html', error="Credenciales inválidas")

    # Si pasa ambas verificaciones, quitar bloqueo
    if email in intentos_fallidos:
        del intentos_fallidos[email]

    # Guardar sesión e iniciar MFA
    session['email'] = email
    session['mfa_verified'] = False

    codigo_mfa = random.randint(100000, 999999)
    session['mfa_code'] = str(codigo_mfa)
    enviar_codigo_verificacion(email, codigo_mfa)

    return redirect(url_for('api_verify'))

        
@app.route("/inicio")
@mfa_requerido
@login_requerido
def inicio():
    email = session['email']
    user = Usuario.query.filter_by(email=email).first()
    secretos = Secret.query.filter_by(owner_email=email).all()
    decrypted = {s.name: cipher.decrypt(s.encrypted_value.encode()).decode() for s in secretos}
    return render_template("inicio.html", secrets=decrypted, nombre_usuario=user.nombre)


@app.route("/usuario")
@login_requerido
def usuario():
    email = session['email']
    user = Usuario.query.filter_by(email=email).first()
    cedula_descifrada = cipher.decrypt(user.cedula.encode()).decode()
    cedula_ofuscada = '*' * (len(cedula_descifrada) - 4) + cedula_descifrada[-4:]
    return render_template("perfil.html", user=user, cedula=cedula_ofuscada)


@app.route("/api/secrets", methods=["GET"])
@login_requerido
def list_secrets():
    user_email = session["email"]
    secrets = Secret.query.filter_by(owner_email=user_email).all()

    decrypted = {
        s.name: cipher.decrypt(s.encrypted_value.encode()).decode()
        for s in secrets
    }

    return jsonify(decrypted)

@app.route("/api/secrets", methods=["POST"])
@login_requerido
def add_secret():
    user_email = session["email"]
    data = request.json
    name = data.get("name")
    value = data.get("value")

    if not name or not value:
        return jsonify({"error": "Falta nombre o valor"}), 400

    encrypted = cipher.encrypt(value.encode()).decode()
    secret = Secret(name=name, encrypted_value=encrypted, owner_email=user_email)
    db.session.add(secret)
    db.session.commit()
    return jsonify({"message": "Secreto guardado correctamente"})


@app.route("/api/secrets/<int:secret_id>", methods=["PUT"])
@login_requerido
def editar_secreto(secret_id):
    data = request.json
    nuevo_valor = data.get("value")

    secreto = Secret.query.get(secret_id)
    if not secreto or secreto.owner_email != session["email"]:
        return jsonify({"error": "Secreto no encontrado o acceso no autorizado"}), 404

    secreto.encrypted_value = cipher.encrypt(nuevo_valor.encode()).decode()
    db.session.commit()
    return jsonify({"message": "Secreto actualizado"})


@app.route("/api/secrets/<int:secret_id>", methods=["DELETE"])
@login_requerido
def eliminar_secreto(secret_id):
    secreto = Secret.query.get(secret_id)
    if not secreto or secreto.owner_email != session["email"]:
        return jsonify({"error": "Secreto no encontrado o acceso no autorizado"}), 404

    db.session.delete(secreto)
    db.session.commit()
    return jsonify({"message": "Secreto eliminado"})


@app.route("/secrets")
@login_requerido
def secrets_page():
    user_email = session["email"]
    asunto = "🔐 Alerta de seguridad"
    cuerpo = f"Se ha ingresado a la seccion de secretos."
    enviar_alerta_correo(user_email, asunto, cuerpo)
    secretos = Secret.query.filter_by(owner_email=user_email).all()
    lista_secretos = [
        {
            "id": s.id,
            "name": s.name,
            "value": cipher.decrypt(s.encrypted_value.encode()).decode()
        } for s in secretos
    ]
    return render_template("secrets.html", secrets=lista_secretos)


@app.route("/api/verify", methods=["GET", "POST"])
def api_verify():
    if request.method == "POST":
        code = request.form['codigo']
        if code == session.get("mfa_code"):
            session["mfa_verified"] = True
            session.pop("mfa_code", None)
            return redirect(url_for('inicio'))
        else:
            session.pop("mfa_code", None)
            return render_template('login.html', error="Código de verificación incorrecto")

    return render_template("verify.html")


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return redirect(url_for('login'))