🔐 Secretos Seguros – Sistema Web para Gestión Segura de Credenciales

Este proyecto implementa una aplicación web segura para almacenar, cifrar y gestionar secretos personales como contraseñas, tokens o claves privadas. Fue desarrollada con buenas prácticas de seguridad y está orientada a reducir la exposición de datos sensibles mediante autenticación multifactor (MFA), cifrado, y automatización.

🎯 Objetivo

Diseñar una herramienta local para que los usuarios puedan:

Almacenar, editar y eliminar secretos de forma privada.

Recibir alertas de seguridad y recordatorios por correo.

Contar con protección criptográfica sin intervención administrativa directa.

Validar el acceso con verificación en dos pasos (MFA).

🛡️ Funcionalidades de Seguridad

✅ Protección de clave secreta mediante .env (nunca expuesta en el código).

✅ Cifrado de datos sensibles con Fernet (clave simétrica).

✅ Autenticación multifactor vía correo electrónico.

✅ Rotación automática de secretos con recordatorio si no se actualizan.

✅ Ofuscación de valores y datos parcialmente visibles.

✅ Bloqueo temporal tras múltiples intentos de login.

✅ Validación de datos únicos: correo, cédula y celular no se pueden repetir.

🧱 Tecnologías Utilizadas

🔧 Framework: Flask (Python)

📂 Base de datos: SQLite + SQLAlchemy

🔐 Cifrado: Fernet (symmetric encryption)

📩 Correos: smtplib + contraseñas de aplicación Gmail

🕒 Tareas programadas: APScheduler

🎨 Frontend: HTML + Bootstrap

🚀 Instalación local

1. Clona el repositorio:

git clone https://github.com/davinchooo/SecretosSeguros.git
cd SecretosSeguros

2. Instala las dependencias:

pip install -r requirements.txt

3. Crea tu archivo .env:

SECRET_KEY=clave_para_cifrar_secretos
FLASK_SECRET_KEY=clave_para_sesiones
EMAIL_USER=tu_correo@gmail.com (con el cual se enviara los correos)
EMAIL_PASSWORD=tu_contraseña_de_app

⚠️ Asegúrate de haber activado las contraseñas de aplicación en tu cuenta de Gmail.

4. Ejecuta la app:

python run.py

La aplicación se ejecutará por defecto en: http://localhost:5000

📌 Funcionalidades destacadas

Panel principal con bienvenida.

Vista separada para secretos (crear, editar, eliminar).

Vista de perfil con cédula desencriptada parcialmente.

MFA obligatorio al iniciar sesión.

Notificaciones automáticas si un secreto no se actualiza después de 30 días.

📥 Ideas a futuro

Exportar secretos cifrados como respaldo.

Historial de cambios por secreto.

Validación biométrica local.

Uso de tokens de acceso temporal (TOTP).

Autenticación por dispositivos o ubicación.

Automatización total del sistema sin contacto humano.

🧑‍💻 Autores

Proyecto universitario desarrollado por NATALIA ALEJANDRA MARTINEZ MUÑOZ, JUAN DIEGO SOSA BARRETO, David Santiago Vargas Ovalle como parte del curso de Desarrollo de Software Seguro.

🛡️ Licencia

Este proyecto es de código abierto y fue creado únicamente con fines académicos y educativos.

