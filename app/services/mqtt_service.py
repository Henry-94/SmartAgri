import asyncio
import aiomqtt
import json
import ssl
import os
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models.user import User
from app.models.sensor_data import SensorData
from app.models.security_event import SecurityEvent
from app.routers.websocket import active_connections

load_dotenv()

# Configuration HiveMQ
BROKER   = os.getenv("MQTT_BROKER")
PORT     = int(os.getenv("MQTT_PORT", 8883))
USERNAME = os.getenv("MQTT_USERNAME")
PASSWORD = os.getenv("MQTT_PASSWORD")
USE_TLS  = os.getenv("MQTT_USE_TLS", "true").lower() == "true"

TOPIC_SENSORS  = os.getenv("MQTT_TOPIC_SENSORS")
TOPIC_COMMANDS = os.getenv("MQTT_TOPIC_COMMANDS")
TOPIC_SECURITY = os.getenv("MQTT_TOPIC_SECURITY")
TOPIC_ACK      = os.getenv("MQTT_TOPIC_ACK")

# Configuration Email (SMTP) - DÉSACTIVÉ
# SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
# SMTP_PORT     = int(os.getenv("SMTP_PORT", 465))  # Changé à 465 pour SSL
# SMTP_USER     = os.getenv("SMTP_USER", "")        # Votre adresse Gmail
# SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")    # App Password Gmail
# ALERT_EMAIL   = os.getenv("ALERT_EMAIL", "")      # Adresse de destination

# Dossier musique d'alerte (fichier MP3 mis par l'utilisateur)
MUSIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "music")


# async def send_alert_email(event_type: str, description: str, to_email: str = None):
#     """Envoie un email d'alerte de sécurité à l'utilisateur"""
#     recipient = to_email or ALERT_EMAIL
#     if not recipient or not SMTP_USER or not SMTP_PASSWORD:
#         print("⚠ Email non configuré — vérifiez SMTP_USER, SMTP_PASSWORD et ALERT_EMAIL dans .env")
#         return False

#     try:
#         msg = MIMEMultipart("alternative")
#         msg["Subject"] = f"🚨 Alerte Sécurité SmartAgri — {event_type}"
#         msg["From"]    = SMTP_USER
#         msg["To"]      = recipient

#         html_body = f"""
#         <html>
#         <body style="font-family: Arial, sans-serif; background: #f5faf5; padding: 20px;">
#           <div style="max-width: 500px; margin: auto; background: white; border-radius: 12px;
#                       border: 2px solid #16a34a; padding: 30px; box-shadow: 0 4px 20px rgba(22,163,74,0.15);">
#             <h2 style="color: #ef4444; margin: 0 0 16px;">🚨 Alerte de Sécurité Détectée</h2>
#             <p style="color: #374151;"><strong>Type :</strong> {event_type}</p>
#             <p style="color: #374151;"><strong>Description :</strong> {description}</p>
#             <p style="color: #6b7280; font-size: 13px;">
#               Connectez-vous à votre plateforme SmartAgri pour gérer l'alarme.
#             </p>
#             <hr style="border: 1px solid #dcfce7; margin: 20px 0;" />
#             <p style="color: #9ca3af; font-size: 11px;">SmartAgri — Système de surveillance automatique</p>
#           </div>
#         </body>
#         </html>
#         """

#         msg.attach(MIMEText(html_body, "html"))

#         with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
#             server.login(SMTP_USER, SMTP_PASSWORD)
#             server.sendmail(SMTP_USER, recipient, msg.as_string())

#         print(f"✉ Email d'alerte envoyé à {recipient}")
#         return True

#     except Exception as e:
#         print(f"✗ Erreur envoi email : {e}")
#         return False


def get_alert_music_path() -> str | None:
    """Retourne le chemin du fichier MP3 d'alerte s'il existe"""
    if not os.path.isdir(MUSIC_DIR):
        os.makedirs(MUSIC_DIR, exist_ok=True)
        return None
    for fname in ["alert.mp3", "alarm.mp3", "alert.wav", "alarm.wav"]:
        fpath = os.path.join(MUSIC_DIR, fname)
        if os.path.isfile(fpath):
            return fpath
    return None


async def publish_command(cmd):
    """Envoie une commande à l'ESP32 via MQTT"""
    async with aiomqtt.Client(
        hostname=BROKER,
        port=PORT,
        username=USERNAME or None,
        password=PASSWORD or None,
        tls_context=ssl.create_default_context() if USE_TLS else None,
    ) as client:
        if hasattr(cmd, 'dict'):
            payload = json.dumps(cmd.dict(exclude_none=True))
        else:
            payload = json.dumps(cmd)
        await client.publish(TOPIC_COMMANDS, payload)
        print(f"✓ Commande MQTT envoyée → {payload}")


async def start_mqtt():
    """Écoute les messages du broker HiveMQ et gère les alertes"""
    print(f"✓ Connexion au broker HiveMQ : {BROKER}:{PORT} (TLS={USE_TLS})")

    # Vérifier le fichier musique au démarrage
    music_path = get_alert_music_path()
    if music_path:
        print(f"✓ Fichier musique alerte trouvé : {music_path}")
    else:
        print(f"⚠ Aucun fichier musique dans {MUSIC_DIR} — ajoutez alert.mp3")

    while True:
        try:
            async with aiomqtt.Client(
                hostname=BROKER,
                port=PORT,
                username=USERNAME or None,
                password=PASSWORD or None,
                tls_context=ssl.create_default_context() if USE_TLS else None,
            ) as client:
                async with client.messages() as messages:
                    await client.subscribe(TOPIC_SENSORS)
                    await client.subscribe(TOPIC_SECURITY)
                    await client.subscribe(TOPIC_ACK)
                    print(f"✓ Abonné aux topics : {TOPIC_SENSORS}, {TOPIC_SECURITY}, {TOPIC_ACK}")

                    async for message in messages:
                        try:
                            payload = json.loads(message.payload)
                        except json.JSONDecodeError as e:
                            print(f"✗ Erreur traitement message : {e}")
                            continue

                        try:
                            db = SessionLocal()

                            if str(message.topic) == TOPIC_SENSORS:
                                data = SensorData(
                                    temp=payload.get("temp"),
                                    hum=payload.get("hum"),
                                    soil=payload.get("soil"),
                                    tank=payload.get("tank")
                                )
                                db.add(data)
                                db.commit()

                            elif str(message.topic) == TOPIC_SECURITY:
                                event_type  = payload.get("type", "UNKNOWN")
                                description = payload.get("description", "Alerte sécurité")

                                # Envoi d'email d'alerte DÉSACTIVÉ
                                # email_sent = False
                                # try:
                                #     users = db.query(User).filter(User.is_active == True).all()
                                #     for user in users:
                                #         if user.email:
                                #             sent = await send_alert_email(event_type, description, user.email)
                                #             if sent:
                                #                 email_sent = True  # Au moins un email envoyé
                                # except Exception as e:
                                #     print(f"⚠ Erreur envoi emails utilisateurs : {e}")
                                
                                # Fallback vers ALERT_EMAIL si aucun utilisateur n'a reçu l'email
                                # if not email_sent:
                                #     email_sent = await send_alert_email(event_type, description)

                                event = SecurityEvent(
                                    event_type=event_type,
                                    description=description,
                                )
                                db.add(event)
                                db.commit()

                                # Déclencher buzzer local sur ESP32
                                await publish_command({"buzzer": True})

                                # Notifier le frontend qu'il doit jouer la musique
                                music_path = get_alert_music_path()
                                if music_path:
                                    payload["play_music"] = True
                                    payload["music_file"] = os.path.basename(music_path)
                                else:
                                    payload["play_music"] = False

                            elif str(message.topic) == TOPIC_ACK:
                                # Messages ACK : mises à jour d'état ESP32 (pas de DB)
                                pass  # Juste forward to WebSocket

                            # Diffusion temps réel → frontend React
                            for ws in active_connections[:]:
                                try:
                                    await ws.send_json(payload)
                                except Exception:
                                    active_connections.remove(ws)

                        except Exception as e:
                            print(f"✗ Erreur traitement message : {e}")
                        finally:
                            db.close()

        except aiomqtt.MqttError as e:
            print(f"✗ Connexion MQTT perdue ({e}). Reconnexion dans 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"✗ Erreur inattendue MQTT : {e}")
            await asyncio.sleep(5)
