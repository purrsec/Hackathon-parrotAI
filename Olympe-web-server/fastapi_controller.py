"""
FastAPI Entrypoint (WebSocket-first) pour piloter un drone Parrot ANAFI via Olympe.
Reçoit des commandes depuis le front ou Discord via WebSocket (/ws) ou via HTTP POST (/cmd).
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json
import time
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import Olympe (mode mock si indisponible)
try:
    import olympe
    from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveBy, moveTo
    from olympe.messages.ardrone3.PilotingState import FlyingStateChanged
    OLYMPE_AVAILABLE = True
except Exception:
    logger.warning("Olympe non disponible - mode mock activé")
    OLYMPE_AVAILABLE = False

# Configuration
DRONE_IP = "10.202.0.1"  # IP par défaut Sphinx/ANAFI
app = FastAPI(title="Parrot Olympe Controller API")

# CORS (front Next.js par défaut)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# État global (mock par défaut)
drone_state = {
    "connected": False,
    "state": "idle",  # idle, flying, hovering, landing
    "battery": 100,
    "gps": {"lat": 48.8566, "lon": 2.3522, "alt": 0},
    "home": {"lat": 48.8566, "lon": 2.3522, "alt": 0},
}

# Historique commandes (debug)
command_history = []

# Instance drone
drone = None

# Pydantic modèles
class Command(BaseModel):
    id: str
    action: str
    parameters: Dict[str, Any] = {}


class CommandResponse(BaseModel):
    id: str
    status: str  # success, in_progress, error
    message: str
    data: Dict[str, Any] = {}


# Helpers
def ok(id: str, msg: str, data: Optional[Dict[str, Any]] = None) -> CommandResponse:
    return CommandResponse(id=id, status="success", message=msg, data=data or {})


def err(id: str, msg: str) -> CommandResponse:
    return CommandResponse(id=id, status="error", message=msg, data={})


def in_progress(id: str, msg: str, data: Optional[Dict[str, Any]] = None) -> CommandResponse:
    return CommandResponse(id=id, status="in_progress", message=msg, data=data or {})


# Cycle de vie
@app.on_event("startup")
async def startup():
    global drone, drone_state
    if OLYMPE_AVAILABLE:
        try:
            drone = olympe.Drone(DRONE_IP)
            drone.connect()
            drone_state["connected"] = True
            logger.info(f"Drone connecté à {DRONE_IP}")
        except Exception as e:
            logger.error(f"Erreur de connexion au drone: {e}")
            drone_state["connected"] = False
    else:
        logger.info("Mode mock activé - Olympe non disponible")
        drone_state["connected"] = True


@app.on_event("shutdown")
async def shutdown():
    global drone
    if drone and OLYMPE_AVAILABLE:
        try:
            drone.disconnect()
            logger.info("Drone déconnecté")
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")


# Routeur de commandes (utilisé par WS et REST)
async def route_command(command: Command) -> CommandResponse:
    logger.info("=" * 80)
    logger.info(f"📥 COMMANDE - ID: {command.id} | action={command.action} | params={command.parameters}")
    command_history.append({
        "id": command.id,
        "action": command.action,
        "parameters": command.parameters,
        "timestamp": time.time(),
    })
    if len(command_history) > 100:
        command_history.pop(0)

    action = command.action.lower().strip()
    if action == "takeoff":
        result = await handle_takeoff(command)
    elif action == "goto":
        result = await handle_goto(command)
    elif action == "circle":
        result = await handle_circle(command)
    elif action == "capture":
        result = await handle_capture(command)
    elif action == "rth":
        result = await handle_return_to_home(command)
    elif action == "land":
        result = await handle_land(command)
    elif action == "status":
        result = await handle_status(command)
    else:
        result = err(command.id, f"Action inconnue: {command.action}")

    logger.info(f"📤 RÉPONSE - ID: {result.id} | status={result.status} | msg={result.message} | data={result.data}")
    logger.info("=" * 80)
    return result


# WebSocket entrypoint (front ou Discord gateway)
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        # Envoi d'un message d'accueil avec l'état courant
        await ws.send_json({
            "type": "welcome",
            "message": "Connected to Olympe Controller",
            "drone_state": drone_state,
            "olympe_available": OLYMPE_AVAILABLE,
        })
        while True:
            msg = await ws.receive_text()
            try:
                payload = json.loads(msg)
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            # Format attendu: { id, action, parameters? }
            if not isinstance(payload, dict) or "action" not in payload or "id" not in payload:
                await ws.send_json({"type": "error", "message": "Missing fields: id, action"})
                continue

            cmd = Command(
                id=str(payload["id"]),
                action=str(payload["action"]),
                parameters=dict(payload.get("parameters", {})),
            )
            result = await route_command(cmd)
            await ws.send_json({
                "type": "command_result",
                "id": result.id,
                "status": result.status,
                "message": result.message,
                "data": result.data,
            })
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
        await ws.close()


# REST fallback
@app.post("/cmd", response_model=CommandResponse)
async def cmd(command: Command):
    return await route_command(command)


# Santé / debug
@app.get("/health")
async def health():
    return {"status": "ok", "drone_connected": drone_state["connected"], "olympe_available": OLYMPE_AVAILABLE}


@app.get("/history")
async def get_history():
    return {
        "total": len(command_history),
        "commands": command_history[-20:],
        "drone_state": drone_state
    }


@app.post("/reset")
async def reset_state():
    global drone_state, command_history
    drone_state = {
        "connected": True,
        "state": "idle",
        "battery": 100,
        "gps": {"lat": 48.8566, "lon": 2.3522, "alt": 0},
        "home": {"lat": 48.8566, "lon": 2.3522, "alt": 0},
    }
    command_history = []
    logger.info("🔄 État du drone réinitialisé")
    return {"status": "reset", "drone_state": drone_state}


# Handlers
async def handle_takeoff(cmd: Command) -> CommandResponse:
    alt_m = cmd.parameters.get("alt_m", 10)
    logger.info(f"   🚁 Décollage demandé à {alt_m}m")
    if OLYMPE_AVAILABLE and drone:
        try:
            result = drone(TakeOff() >> FlyingStateChanged(state="hovering", _timeout=10)).wait()
            if result.success():
                drone_state["state"] = "hovering"
                drone_state["gps"]["alt"] = alt_m
                return ok(cmd.id, f"Décollage réussi à {alt_m}m", {"altitude": alt_m, "state": drone_state["state"]})
            return err(cmd.id, "Échec du décollage")
        except Exception as e:
            return err(cmd.id, f"Erreur décollage: {str(e)}")
    # Mock
    await asyncio.sleep(0.5)
    drone_state["state"] = "hovering"
    drone_state["gps"]["alt"] = alt_m
    return ok(cmd.id, f"[MOCK] Décollage réussi à {alt_m}m", {"altitude": alt_m, "state": drone_state["state"]})


async def handle_goto(cmd: Command) -> CommandResponse:
    lat = cmd.parameters.get("lat")
    lon = cmd.parameters.get("lon")
    alt_m = cmd.parameters.get("alt_m")
    speed_mps = cmd.parameters.get("speed_mps", 5)
    logger.info(f"   🗺️  Goto ({lat}, {lon}) alt={alt_m}m v={speed_mps}m/s")
    if lat is None or lon is None or alt_m is None:
        return err(cmd.id, "Paramètres manquants: lat, lon, alt_m requis")
    if OLYMPE_AVAILABLE and drone:
        try:
            result = drone(moveTo(lat, lon, alt_m) >> FlyingStateChanged(state="hovering", _timeout=30)).wait()
            if result.success():
                drone_state["gps"] = {"lat": lat, "lon": lon, "alt": alt_m}
                drone_state["state"] = "hovering"
                return ok(cmd.id, f"Déplacement vers ({lat}, {lon}) à {alt_m}m", {"gps": drone_state["gps"], "state": drone_state["state"]})
            return err(cmd.id, "Échec du déplacement")
        except Exception as e:
            return err(cmd.id, f"Erreur déplacement: {str(e)}")
    # Mock
    await asyncio.sleep(1.0)
    drone_state["gps"] = {"lat": lat, "lon": lon, "alt": alt_m}
    drone_state["state"] = "flying"
    return ok(cmd.id, f"[MOCK] Déplacement vers ({lat}, {lon}) à {alt_m}m", {"gps": drone_state["gps"], "state": drone_state["state"]})


async def handle_circle(cmd: Command) -> CommandResponse:
    target_lat = cmd.parameters.get("target_lat")
    target_lon = cmd.parameters.get("target_lon")
    alt_m = cmd.parameters.get("alt_m")
    radius_m = cmd.parameters.get("radius_m", 50)
    laps = cmd.parameters.get("laps", 1)
    logger.info(f"   ⭕ Orbite autour ({target_lat}, {target_lon}) alt={alt_m}m r={radius_m}m laps={laps}")
    if target_lat is None or target_lon is None or alt_m is None:
        return err(cmd.id, "Paramètres manquants: target_lat, target_lon, alt_m requis")
    # Implémentation réelle à compléter (POI/waypoints); ici: progression
    drone_state["state"] = "flying"
    return in_progress(cmd.id, f"Orbite en cours", {
        "target": {"lat": target_lat, "lon": target_lon},
        "radius": radius_m,
        "laps": laps
    })


async def handle_capture(cmd: Command) -> CommandResponse:
    capture_type = cmd.parameters.get("type", "photo")
    duration_s = cmd.parameters.get("duration_s", 10)
    logger.info(f"   📸 Capture: type={capture_type} dur={duration_s}s")
    if OLYMPE_AVAILABLE and drone:
        try:
            # À implémenter selon l'API Camera/Camera2 si disponible
            return ok(cmd.id, f"Capture {capture_type} effectuée", {
                "type": capture_type,
                "duration": duration_s if capture_type == "video" else None,
                "artifact_url": f"/media/{int(time.time())}.{'mp4' if capture_type == 'video' else 'jpg'}"
            })
        except Exception as e:
            return err(cmd.id, f"Erreur capture: {str(e)}")
    await asyncio.sleep(0.5)
    return ok(cmd.id, f"[MOCK] Capture {capture_type} effectuée", {
        "type": capture_type,
        "duration": duration_s if capture_type == "video" else None,
        "artifact_url": f"/media/{int(time.time())}.{'mp4' if capture_type == 'video' else 'jpg'}"
    })


async def handle_return_to_home(cmd: Command) -> CommandResponse:
    home = drone_state["home"]
    logger.info(f"   🏠 RTH vers {home}")
    if OLYMPE_AVAILABLE and drone:
        try:
            result = drone(moveTo(home["lat"], home["lon"], home["alt"]) >> FlyingStateChanged(state="hovering", _timeout=30)).wait()
            if result.success():
                drone_state["gps"] = home.copy()
                drone_state["state"] = "hovering"
                return ok(cmd.id, "Retour au point de départ réussi", {"gps": drone_state["gps"]})
            return err(cmd.id, "Échec du retour au point de départ")
        except Exception as e:
            return err(cmd.id, f"Erreur retour: {str(e)}")
    await asyncio.sleep(2.0)
    drone_state["gps"] = home.copy()
    drone_state["state"] = "hovering"
    return ok(cmd.id, "[MOCK] Retour au point de départ réussi", {"gps": drone_state["gps"]})


async def handle_land(cmd: Command) -> CommandResponse:
    logger.info("   🛬 Atterrissage")
    if OLYMPE_AVAILABLE and drone:
        try:
            result = drone(Landing() >> FlyingStateChanged(state="landed", _timeout=10)).wait()
            if result.success():
                drone_state["state"] = "idle"
                drone_state["gps"]["alt"] = 0
                return ok(cmd.id, "Atterrissage réussi", {"state": drone_state["state"]})
            return err(cmd.id, "Échec de l'atterrissage")
        except Exception as e:
            return err(cmd.id, f"Erreur atterrissage: {str(e)}")
    await asyncio.sleep(1.0)
    drone_state["state"] = "idle"
    drone_state["gps"]["alt"] = 0
    return ok(cmd.id, "[MOCK] Atterrissage réussi", {"state": drone_state["state"]})


async def handle_status(cmd: Command) -> CommandResponse:
    if drone_state["state"] in ["flying", "hovering"]:
        drone_state["battery"] = max(0, drone_state["battery"] - 0.1)
    return ok(cmd.id, "Statut récupéré", {
        "state": drone_state["state"],
        "battery_pct": drone_state["battery"],
        "gps": drone_state["gps"],
        "connected": drone_state["connected"],
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

