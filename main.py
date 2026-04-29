from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import auth, sensors, irrigation, security, history, websocket
from app.services.mqtt_service import start_mqtt
import asyncio
import os

# Création des tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Agri Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Dossier music/ servi en statique pour le frontend ──
# Placez vos fichiers MP3 dans le dossier "music/" à la racine du backend
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")
os.makedirs(MUSIC_DIR, exist_ok=True)
app.mount("/music", StaticFiles(directory=MUSIC_DIR), name="music")

# ── Routers ──
app.include_router(auth.router,      prefix="/api/auth",       tags=["auth"])
app.include_router(sensors.router,   prefix="/api/sensors",    tags=["sensors"])
app.include_router(irrigation.router,prefix="/api/irrigation", tags=["irrigation"])
app.include_router(security.router,  prefix="/api/security",   tags=["security"])
app.include_router(history.router,   prefix="/api/history",    tags=["history"])
app.include_router(websocket.router, prefix="/api/ws",         tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_mqtt())

@app.get("/")
def root():
    return {
        "message": "Smart Agri Backend v2 — MQTT + WebSocket + PostgreSQL",
        "music_dir": MUSIC_DIR,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
