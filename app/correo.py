import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def enviar_alerta_correo(usuario_email, asunto, cuerpo):
    from_email = os.getenv("MAIL_USER")
    password = os.getenv("MAIL_PASSWORD")
    to_email = usuario_email

    if not from_email or not password:
        print("Faltan credenciales para correo en .env")
        return

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
            #print("Correo enviado con éxito")
    except Exception as e:
        print("Error al enviar el correo:", e)


def enviar_codigo_verificacion(usuario_email, codigo):
    from_email = os.getenv("MAIL_USER")
    password = os.getenv("MAIL_PASSWORD")
    to_email = usuario_email

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = "🔐 Código de verificación MFA"

    cuerpo = f"Tu código de verificación es: {codigo}\n\nEste código es válido por solo unos minutos."
    msg.attach(MIMEText(cuerpo, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
            #print("✅ Código MFA enviado con éxito.")
    except Exception as e:
        print("❌ Error al enviar el código MFA:", e)