import os
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv

load_dotenv()

# Configuración de Servidor SMTP (Gmail)
conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "tu-correo@gmail.com"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM", os.getenv("MAIL_USERNAME")),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Arreglos Florales"),
    MAIL_STARTTLS = os.getenv("MAIL_TLS", "True") == "True",
    MAIL_SSL_TLS = os.getenv("MAIL_SSL", "False") == "True",
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_reset_code_email(email: str, code: str):
    """Envía un correo con el código de recuperación de contraseña usando fastapi-mail."""
    html = f"""
    <div style="font-family: Arial, sans-serif; text-align: center; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #4f46e5; margin-bottom: 20px;">Recuperación de Contraseña</h2>
        <p style="color: #4b5563; font-size: 16px;">Has solicitado restablecer tu contraseña. Tu código de verificación es:</p>
        <div style="font-size: 36px; font-weight: bold; margin: 30px 0; color: #4f46e5; letter-spacing: 8px; background-color: #f3f4f6; padding: 15px; border-radius: 4px;">
            {code}
        </div>
        <p style="color: #6b7280; font-size: 14px;">Este código expira en 15 minutos.</p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        <p style="font-size: 12px; color: #9ca3af;">Si no solicitaste este cambio, simplemente ignora este correo.</p>
        <p style="font-size: 12px; color: #9ca3af;">&copy; 2024 Arreglos Florales Ale-Det</p>
    </div>
    """

    message = MessageSchema(
        subject="Código de Recuperación de Contraseña - Arreglos Florales",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        print(f"✅ Correo enviado exitosamente a {email} usando fastapi-mail")
        return True
    except Exception as e:
        print(f"❌ Error enviando correo: {str(e)}")
        raise e

async def send_email_change_code(email: str, code: str):
    """Envía un correo con el código para verificar el nuevo correo electrónico."""
    html = f"""
    <div style="font-family: Arial, sans-serif; text-align: center; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #4f46e5; margin-bottom: 20px;">Verificación de Nuevo Correo</h2>
        <p style="color: #4b5563; font-size: 16px;">Para confirmar tu cambio de correo electrónico, usa el siguiente código:</p>
        <div style="font-size: 36px; font-weight: bold; margin: 30px 0; color: #4f46e5; letter-spacing: 8px; background-color: #f3f4f6; padding: 15px; border-radius: 4px;">
            {code}
        </div>
        <p style="color: #6b7280; font-size: 14px;">Este código expira en 15 minutos.</p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;">
        <p style="font-size: 12px; color: #9ca3af;">Si no solicitaste este cambio, por favor contacta a soporte.</p>
        <p style="font-size: 12px; color: #9ca3af;">&copy; 2024 Arreglos Florales Ale-Det</p>
    </div>
    """

    message = MessageSchema(
        subject="Cambio de Correo Electrónico - Arreglos Florales",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        print(f"✅ Correo de verificación enviado a {email}")
        return True
    except Exception as e:
        print(f"❌ Error enviando correo de cambio de email: {str(e)}")
        raise e
