from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    email = db.Column(db.String, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    apellido = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    password_ver = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    cedula = db.Column(db.String, unique=True, nullable=False)
    celular = db.Column(db.String, unique=True, nullable=False)

    secretos = db.relationship('Secret', backref='usuario', lazy=True)

class Secret(db.Model):
    __tablename__ = 'secrets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    encrypted_value = db.Column(db.Text, nullable=False)
    owner_email = db.Column(db.String, db.ForeignKey('usuarios.email'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
