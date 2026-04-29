from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.command import CommandSchema, WifiCommandSchema
from app.services.mqtt_service import publish_command
from app.database import get_db
from app.models.action_log import ActionLog

router = APIRouter()


@router.post("/command")
async def send_irrigation_command(cmd: CommandSchema, db: Session = Depends(get_db)):
    """
    Envoie une commande à l'ESP32 via MQTT.

    Commandes supportées :
      { "auto": true  }            → Active  l'automatisation ESP32
      { "auto": false }            → Désactive l'automatisation ESP32
      { "pump_a": true  }          → Pompe A ON  (commande directe)
      { "pump_a": false }          → Pompe A OFF (commande directe)
      { "pump_b": true  }          → Pompe B ON  (commande directe)
      { "pump_b": false }          → Pompe B OFF (commande directe)
      { "mode": "thresholds", ... }→ Mise à jour seuils
      { "mode": "restart" }        → Redémarrage ESP32
    """
    await publish_command(cmd)

    # Enregistrer en BDD seulement les actions utiles
    should_log = (
        cmd.mode not in ("restart", "thresholds", "wifi")
        and (
            cmd.pump_a is not None
            or cmd.pump_b is not None
            or cmd.auto  is not None
        )
    )

    if should_log:
        try:
            action_desc = _build_action_desc(cmd)
            if cmd.auto is not None:
                mode_log = "auto"
            elif cmd.pump_a is not None or cmd.pump_b is not None:
                mode_log = "manuel"
            else:
                mode_log = "system"

            log = ActionLog(
                pump_a = cmd.pump_a if cmd.pump_a is not None else False,
                pump_b = cmd.pump_b if cmd.pump_b is not None else False,
                mode   = mode_log,
                action = action_desc,
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"⚠ Erreur enregistrement action : {e}")

    return {"status": "ok", "message": "Commande envoyée à l'ESP32 via MQTT"}


@router.post("/wifi")
async def send_wifi_command(cmd: WifiCommandSchema):
    """Envoie une configuration WiFi à l'ESP32."""
    wifi_payload = {"mode": "wifi", "ssid": cmd.ssid, "password": cmd.password or ""}
    await publish_command(wifi_payload)
    return {"status": "ok", "message": "Configuration WiFi envoyée à l'ESP32"}


def _build_action_desc(cmd: CommandSchema) -> str:
    parts = []
    if cmd.auto is True:
        parts.append("Automatisation ACTIVÉE (Pompe A + B)")
    elif cmd.auto is False:
        parts.append("Automatisation DÉSACTIVÉE")
    if cmd.pump_a is not None:
        parts.append(f"Pompe A {'ON' if cmd.pump_a else 'OFF'} (manuel)")
    if cmd.pump_b is not None:
        parts.append(f"Pompe B {'ON' if cmd.pump_b else 'OFF'} (manuel)")
    return " | ".join(parts) if parts else "Commande système"
