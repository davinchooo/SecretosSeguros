from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from app.models import db, Secret, Usuario
from app.correo import enviar_alerta_correo
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_apscheduler import APScheduler
import os

def notificar_secreto_desactualizado(app):
    with app.app_context():
        ahora = datetime.utcnow()
        secretos = Secret.query.all()

        for secreto in secretos:
            if (ahora - secreto.created_at) >= timedelta(minutes=10):
                usuario = Usuario.query.filter_by(email=secreto.owner_email).first()
                if usuario:
                    asunto = "Recordatorio: actualiza tus secretos"
                    cuerpo = f"Hola {usuario.nombre},\n\nEl secreto \"{secreto.name}\" no ha sido actualizado en más de 30 días. Te recomendamos revisarlo por seguridad."
                    enviar_alerta_correo(usuario.email, asunto, cuerpo)

        print("🔁 Se revisaron los secretos desactualizados.")


app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db.init_app(app)

# Crear las tablas automáticamente
with app.app_context():
    db.create_all()

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

scheduler.add_job(
    id='notificar_secreto_desactualizado',
    func=lambda: notificar_secreto_desactualizado(app),
    trigger='interval',
    minutes=10
)

# Importa las rutas y la API
from app import api, routes
