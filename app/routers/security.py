from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.command import CommandSchema
from app.services.mqtt_service import publish_command
from app.database import get_db

router = APIRouter()

@router.post("/command")
async def send_security_command(cmd: CommandSchema, db: Session = Depends(get_db)):
    """
    Envoie une commande sécurité à l'ESP32 via MQTT.
    Champs supportés :
      - security : True/False — active/désactive PIR + fil
      - buzzer   : True/False — active/désactive le buzzer local
      - email_alert : True/False — active/désactive les notifications email
    """
    await publish_command(cmd)
    return {"status": "ok", "message": "Commande sécurité envoyée à l'ESP32 via MQTT"}
