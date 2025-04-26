from flask import Flask
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app.secret_key = 'pOQBnpQJzMhnDhcubjs9c6WrLeUZOx1KSFwNQPwNtcs='
# Importa las rutas y la API
from app import api, routes
