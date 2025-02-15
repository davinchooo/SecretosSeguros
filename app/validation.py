from _datetime import datetime
import re

import unicodedata


def normalize_input(data):
    if isinstance(data, str):
        return unicodedata.normalize('NFKD', data)
    return data


# valido el email
def validate_email(email):
    email = normalize_input(email)
    patron = r'^[a-zA-Z0-9._%+-]+@urosario\.edu\.co$'
    return bool(re.fullmatch(patron, email))


# valido la edad
def validate_dob(dob):
    """Verifica si el usuario tiene al menos 16 años."""
    formato_fecha = "%Y-%m-%d"  # Ajusta el formato si es necesario (Ej: "%d/%m/%Y")
    try:
        fecha_nac = datetime.strptime(dob, formato_fecha)
        hoy = datetime.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        return edad >= 16
    except ValueError:
        return False  # Retorna False si la fecha no tiene el formato correcto
    

# valido el usuario
def validate_user(user):
    patron = r'^[a-zA-Z]+(\.[a-zA-Z]+)*$'
    return bool(re.fullmatch(patron, user))

# valido el dni
def validate_dni(dni):
    if dni.isdigit() and len(dni) == 10:
        return 1000000000 <= int(dni) <= 9999999999
    return False


# valido la contraseña
def validate_pswd(pswd):
    patron = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#*@\$%&\-!+=?])[A-Za-z\d#*@\$%&\-!+=?]{8,35}$'
    return bool(re.fullmatch(patron, pswd))


def validate_name(name):
    return True

