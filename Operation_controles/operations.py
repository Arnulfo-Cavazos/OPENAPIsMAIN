from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.header import Header
import os
from dotenv import load_dotenv

app = FastAPI()

# ----------------------------------------------------
# MODELOS
# ----------------------------------------------------
class Persona(BaseModel):
    nombre: str
    apariciones: int
    tiempo_hablando_minutos: int
    salario_usd: str
    correo: str
    tiene_sindicato: str


class PersonasPayload(BaseModel):
    personas: List[Persona]


# ----------------------------------------------------
# CONFIG SMTP (TWILIO SENDGRID)
# ----------------------------------------------------
# Datos del correo
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = 2525
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
SMTP_PASS = os.getenv("EMAIL_PASSWORD")
SMTP_USER = os.getenv("USERNAME")


# ----------------------------------------------------
# FUNCIÓN PARA ENVIAR CORREO
# ----------------------------------------------------
def enviar_correo(persona: Persona):
    subject = f"Reporte de actividad – {persona.nombre}"
    body = f"""
Hola {persona.nombre},

Aquí tienes tu resumen:

- Apariciones: {persona.apariciones}
- Tiempo hablando (minutos): {persona.tiempo_hablando_minutos}
- Salario USD: {persona.salario_usd}
- Afiliado a sindicato: {persona.tiene_sindicato}

Saludos.
"""

    msg = MIMEMultipart()
    msg["From"] = formataddr((str(Header("FastAPI Service", "utf-8")), EMAIL_SENDER))
    msg["To"] = persona.correo
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Enviar correo usando Twilio SMTP
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    return True


# ----------------------------------------------------
# ENDPOINT
# ----------------------------------------------------
@app.post("/enviar-correos")
def enviar_correos(payload: PersonasPayload):
    enviados = 0
    for persona in payload.personas:
        enviar_correo(persona)
        enviados += 1

    return {
        "status": "ok",
        "correos_enviados": enviados
    }
