from pydantic import BaseModel
from typing import Optional


class CommandSchema(BaseModel):
    # ── Commande automatisation globale ──────────────────────────
    # true  → ESP32 active  l'automatisation (les deux pompes)
    # false → ESP32 désactive l'automatisation
    auto: Optional[bool] = None

    # ── Commandes pompes directes ────────────────────────────────
    # Toujours traitées par l'ESP32, mode auto ou non
    pump_a: Optional[bool] = None   # true=ON  false=OFF
    pump_b: Optional[bool] = None   # true=ON  false=OFF

    # ── Commandes système ────────────────────────────────────────
    mode: Optional[str] = None      # "restart" | "thresholds"

    # ── Seuils automatiques ──────────────────────────────────────
    soil_min: Optional[float] = None
    soil_max: Optional[float] = None
    tank_min: Optional[float] = None
    tank_max: Optional[float] = None

    # ── Sécurité ─────────────────────────────────────────────────
    security:    Optional[bool] = None
    buzzer:      Optional[bool] = None
    alarm:       Optional[bool] = None
    email_alert: Optional[bool] = None


class WifiCommandSchema(BaseModel):
    ssid:     str
    password: Optional[str] = None
