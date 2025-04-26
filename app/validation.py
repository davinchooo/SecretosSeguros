from datetime import datetime
import re

import unicodedata
import unittest


def normalize_input(data):
    if isinstance(data, str):
        # Normalizar el texto a la forma canónica
        data = unicodedata.normalize('NFKD', data)
        # Convertir a minúsculas y eliminar espacios en blanco
        data = data.strip().lower()
    return data


# valido el email
def validate_email(email):
    email = normalize_input(email)
    return '@' in email

# valido el cedula
def validate_cedula(cedula):
    patron = r'^\d{10}$'
    return bool(re.fullmatch(patron, cedula))

def validate_celular(celular):
    patron = r'^3\d{9}$'
    return bool(re.fullmatch(patron, celular))

# valido la contraseña
def validate_pswd(pswd):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#*@\$%&\-!+=?])[A-Za-z\d#*@\$%&\-!+=?]{8,35}$'
    return bool(re.fullmatch(pattern, pswd))

def validate_name(name):
    return bool(re.fullmatch(r'^[a-zA-Z]+$', name))
