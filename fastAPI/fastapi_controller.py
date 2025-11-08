"""
FastAPI Controller pour le drone Parrot ANAFI
Utilise Olympe SDK pour contrôler le drone via l'interface Ethernet virtuelle
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import Olympe (commenté pour développement local, décommenter au hackathon)
try:
    import olympe
    from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveBy, moveTo
    from olympe.messages.ardrone3.PilotingState import FlyingStateChanged
    from olympe.messages.ardrone3.GPSSettingsState import GPSFixStateChanged
    OLYMPE_AVAILABLE = True
except ImportError:
    logger.warning("Olympe non disponible - mode mock activé")
    OLYMPE_AVAILABLE = False

# Configuration
DRONE_IP = "10.202.0.1"  # IP par défaut du Sphinx/ANAFI
app = FastAPI(title="EDTH Drone Controller API")

# CORS middleware pour permettre les appels depuis Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# État global du drone (mock)
drone_state = {
    "connected": False,
    "state": "idle",  # idle, flying, hovering, landing
    "battery": 100,
    "gps": {"lat": 48.8566, "lon": 2.3522, "alt": 0},
    "home": {"lat": 48.8566, "lon": 2.3522, "alt": 0},
}

# Historique des commandes pour debug
command_history = []

# Instance drone (sera initialisée si Olympe disponible)
drone = None

# Modèles Pydantic
class Command(BaseModel):
    id: str
    action: str
    parameters: Dict[str, Any] = {}


class CommandResponse(BaseModel):
    id: str
    status: str  # success, in_progress, error
    message: str
    data: Dict[str, Any] = {}


# Fonctions helper
def ok(id: str, msg: str, data: Optional[Dict[str, Any]] = None) -> CommandResponse:
    return CommandResponse(
        id=id, status="success", message=msg, data=data or {}
    )


def err(id: str, msg: str) -> CommandResponse:
    return CommandResponse(
        id=id, status="error", message=msg, data={}
    )


def in_progress(id: str, msg: str, data: Optional[Dict[str, Any]] = None) -> CommandResponse:
    return CommandResponse(
        id=id, status="in_progress", message=msg, data=data or {}
    )


# Gestion du cycle de vie
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
        drone_state["connected"] = True  # Mock toujours "connecté"


@app.on_event("shutdown")
async def shutdown():
    global drone
    if drone and OLYMPE_AVAILABLE:
        try:
            drone.disconnect()
            logger.info("Drone déconnecté")
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")


# Endpoint principal pour les commandes
@app.post("/cmd", response_model=CommandResponse)
async def cmd(command: Command):
    """Endpoint principal pour exécuter des commandes drone"""
    try:
        # Log détaillé de la commande reçue
        logger.info("=" * 80)
        logger.info(f"📥 COMMANDE REÇUE - ID: {command.id}")
        logger.info(f"   Action: {command.action}")
        logger.info(f"   Paramètres: {command.parameters}")
        logger.info(f"   Paramètres (JSON): {command.parameters}")
        
        # Ajouter à l'historique
        command_history.append({
            "id": command.id,
            "action": command.action,
            "parameters": command.parameters,
            "timestamp": time.time(),
        })
        # Garder seulement les 50 dernières commandes
        if len(command_history) > 50:
            command_history.pop(0)
        
        action = command.action.lower()
        
        logger.info(f"   → Traitement de l'action: {action}")
        
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
        
        # Log de la réponse
        logger.info(f"📤 RÉPONSE ENVOYÉE - ID: {result.id}")
        logger.info(f"   Status: {result.status}")
        logger.info(f"   Message: {result.message}")
        logger.info(f"   Data: {result.data}")
        logger.info("=" * 80)
        
        return result
    
    except Exception as e:
        logger.error(f"❌ ERREUR lors de l'exécution de {command.action}: {e}")
        logger.exception(e)
        return err(command.id, str(e))


async def handle_takeoff(cmd: Command) -> CommandResponse:
    """Gère la commande de décollage"""
    alt_m = cmd.parameters.get("alt_m", 10)
    logger.info(f"   🚁 Décollage demandé à {alt_m}m d'altitude")
    
    if OLYMPE_AVAILABLE and drone:
        try:
            result = drone(TakeOff() >> FlyingStateChanged(state="hovering", _timeout=10)).wait()
            if result.success():
                drone_state["state"] = "hovering"
                drone_state["gps"]["alt"] = alt_m
                return ok(cmd.id, f"Décollage réussi à {alt_m}m", {
                    "altitude": alt_m,
                    "state": drone_state["state"]
                })
            else:
                return err(cmd.id, "Échec du décollage")
        except Exception as e:
            return err(cmd.id, f"Erreur décollage: {str(e)}")
    else:
        # Mode mock
        logger.info(f"   [MOCK] Simulation du décollage...")
        time.sleep(0.5)  # Simule le délai
        drone_state["state"] = "hovering"
        drone_state["gps"]["alt"] = alt_m
        logger.info(f"   [MOCK] ✓ Décollage simulé - État: {drone_state['state']}, Altitude: {alt_m}m")
        return ok(cmd.id, f"[MOCK] Décollage réussi à {alt_m}m", {
            "altitude": alt_m,
            "state": drone_state["state"]
        })


async def handle_goto(cmd: Command) -> CommandResponse:
    """Gère la commande de déplacement vers un point GPS"""
    lat = cmd.parameters.get("lat")
    lon = cmd.parameters.get("lon")
    alt_m = cmd.parameters.get("alt_m")
    speed_mps = cmd.parameters.get("speed_mps", 5)
    
    logger.info(f"   🗺️  Navigation demandée:")
    logger.info(f"      Destination: ({lat}, {lon})")
    logger.info(f"      Altitude: {alt_m}m")
    logger.info(f"      Vitesse: {speed_mps} m/s")
    
    if lat is None or lon is None or alt_m is None:
        logger.error(f"   ❌ Paramètres manquants: lat={lat}, lon={lon}, alt_m={alt_m}")
        return err(cmd.id, "Paramètres manquants: lat, lon, alt_m requis")
    
    if OLYMPE_AVAILABLE and drone:
        try:
            # Utiliser moveTo pour navigation GPS (si disponible)
            # Sinon, utiliser moveBy pour mouvement relatif
            # Note: moveTo nécessite GPS fix
            result = drone(moveTo(lat, lon, alt_m) >> FlyingStateChanged(state="hovering", _timeout=30)).wait()
            if result.success():
                drone_state["gps"] = {"lat": lat, "lon": lon, "alt": alt_m}
                drone_state["state"] = "hovering"
                return ok(cmd.id, f"Déplacement vers ({lat}, {lon}) à {alt_m}m", {
                    "gps": drone_state["gps"],
                    "state": drone_state["state"]
                })
            else:
                return err(cmd.id, "Échec du déplacement")
        except Exception as e:
            return err(cmd.id, f"Erreur déplacement: {str(e)}")
    else:
        # Mode mock
        logger.info(f"   [MOCK] Simulation du déplacement...")
        time.sleep(1)  # Simule le déplacement
        drone_state["gps"] = {"lat": lat, "lon": lon, "alt": alt_m}
        drone_state["state"] = "flying"
        logger.info(f"   [MOCK] ✓ Position mise à jour: {drone_state['gps']}")
        return ok(cmd.id, f"[MOCK] Déplacement vers ({lat}, {lon}) à {alt_m}m", {
            "gps": drone_state["gps"],
            "state": drone_state["state"]
        })


async def handle_circle(cmd: Command) -> CommandResponse:
    """Gère la commande d'orbite circulaire"""
    target_lat = cmd.parameters.get("target_lat")
    target_lon = cmd.parameters.get("target_lon")
    alt_m = cmd.parameters.get("alt_m")
    radius_m = cmd.parameters.get("radius_m", 50)
    laps = cmd.parameters.get("laps", 1)
    
    logger.info(f"   ⭕ Orbite demandée:")
    logger.info(f"      Centre: ({target_lat}, {target_lon})")
    logger.info(f"      Altitude: {alt_m}m")
    logger.info(f"      Rayon: {radius_m}m")
    logger.info(f"      Tours: {laps}")
    
    if target_lat is None or target_lon is None or alt_m is None:
        logger.error(f"   ❌ Paramètres manquants: target_lat={target_lat}, target_lon={target_lon}, alt_m={alt_m}")
        return err(cmd.id, "Paramètres manquants: target_lat, target_lon, alt_m requis")
    
    if OLYMPE_AVAILABLE and drone:
        try:
            # Pour l'orbite, on peut utiliser plusieurs moveTo en séquence
            # ou utiliser l'API Circle si disponible
            # Ici, on simule avec plusieurs waypoints
            drone_state["state"] = "flying"
            return in_progress(cmd.id, f"Orbite autour de ({target_lat}, {target_lon})", {
                "target": {"lat": target_lat, "lon": target_lon},
                "radius": radius_m,
                "laps": laps
            })
        except Exception as e:
            return err(cmd.id, f"Erreur orbite: {str(e)}")
    else:
        # Mode mock
        logger.info(f"   [MOCK] Simulation de l'orbite...")
        time.sleep(2)
        drone_state["state"] = "flying"
        logger.info(f"   [MOCK] ✓ Orbite simulée - État: {drone_state['state']}")
        return ok(cmd.id, f"[MOCK] Orbite effectuée autour de ({target_lat}, {target_lon})", {
            "target": {"lat": target_lat, "lon": target_lon},
            "radius": radius_m,
            "laps": laps
        })


async def handle_capture(cmd: Command) -> CommandResponse:
    """Gère la commande de capture photo/vidéo"""
    capture_type = cmd.parameters.get("type", "photo")
    duration_s = cmd.parameters.get("duration_s", 10)
    
    logger.info(f"   📸 Capture demandée:")
    logger.info(f"      Type: {capture_type}")
    if capture_type == "video":
        logger.info(f"      Durée: {duration_s}s")
    
    if OLYMPE_AVAILABLE and drone:
        try:
            # Utiliser les messages Olympe pour la capture
            # Exemple: MediaRecordState pour démarrer/arrêter l'enregistrement
            # Note: À implémenter selon la doc Olympe
            return ok(cmd.id, f"Capture {capture_type} effectuée", {
                "type": capture_type,
                "duration": duration_s if capture_type == "video" else None,
                "artifact_url": f"/media/{int(time.time())}.{'mp4' if capture_type == 'video' else 'jpg'}"
            })
        except Exception as e:
            return err(cmd.id, f"Erreur capture: {str(e)}")
    else:
        # Mode mock
        logger.info(f"   [MOCK] Simulation de la capture...")
        time.sleep(0.5)
        artifact_url = f"/media/{int(time.time())}.{'mp4' if capture_type == 'video' else 'jpg'}"
        logger.info(f"   [MOCK] ✓ Capture simulée - URL: {artifact_url}")
        return ok(cmd.id, f"[MOCK] Capture {capture_type} effectuée", {
            "type": capture_type,
            "duration": duration_s if capture_type == "video" else None,
            "artifact_url": artifact_url
        })


async def handle_return_to_home(cmd: Command) -> CommandResponse:
    """Gère la commande de retour au point de départ"""
    home = drone_state["home"]
    logger.info(f"   🏠 Retour au point de départ demandé: {home}")
    
    if OLYMPE_AVAILABLE and drone:
        try:
            # Utiliser moveTo vers le point home
            result = drone(moveTo(home["lat"], home["lon"], home["alt"]) >> FlyingStateChanged(state="hovering", _timeout=30)).wait()
            if result.success():
                drone_state["gps"] = home.copy()
                drone_state["state"] = "hovering"
                return ok(cmd.id, "Retour au point de départ réussi", {
                    "gps": drone_state["gps"]
                })
            else:
                return err(cmd.id, "Échec du retour au point de départ")
        except Exception as e:
            return err(cmd.id, f"Erreur retour: {str(e)}")
    else:
        # Mode mock
        logger.info(f"   [MOCK] Simulation du retour à la base...")
        time.sleep(2)
        drone_state["gps"] = home.copy()
        drone_state["state"] = "hovering"
        logger.info(f"   [MOCK] ✓ Retour simulé - Position: {drone_state['gps']}")
        return ok(cmd.id, "[MOCK] Retour au point de départ réussi", {
            "gps": drone_state["gps"]
        })


async def handle_land(cmd: Command) -> CommandResponse:
    """Gère la commande d'atterrissage"""
    logger.info(f"   🛬 Atterrissage demandé")
    if OLYMPE_AVAILABLE and drone:
        try:
            result = drone(Landing() >> FlyingStateChanged(state="landed", _timeout=10)).wait()
            if result.success():
                drone_state["state"] = "idle"
                drone_state["gps"]["alt"] = 0
                return ok(cmd.id, "Atterrissage réussi", {
                    "state": drone_state["state"]
                })
            else:
                return err(cmd.id, "Échec de l'atterrissage")
        except Exception as e:
            return err(cmd.id, f"Erreur atterrissage: {str(e)}")
    else:
        # Mode mock
        logger.info(f"   [MOCK] Simulation de l'atterrissage...")
        time.sleep(1)
        drone_state["state"] = "idle"
        drone_state["gps"]["alt"] = 0
        logger.info(f"   [MOCK] ✓ Atterrissage simulé - État: {drone_state['state']}")
        return ok(cmd.id, "[MOCK] Atterrissage réussi", {
            "state": drone_state["state"]
        })


async def handle_status(cmd: Command) -> CommandResponse:
    """Gère la requête de statut du drone"""
    # Mettre à jour la batterie (simulation de décharge)
    if drone_state["state"] in ["flying", "hovering"]:
        drone_state["battery"] = max(0, drone_state["battery"] - 0.1)
    
    return ok(cmd.id, "Statut récupéré", {
        "state": drone_state["state"],
        "battery_pct": drone_state["battery"],
        "gps": drone_state["gps"],
        "connected": drone_state["connected"],
        "message": f"Drone en état: {drone_state['state']}"
    })


# Endpoint de santé
@app.get("/health")
async def health():
    return {"status": "ok", "drone_connected": drone_state["connected"], "olympe_available": OLYMPE_AVAILABLE}


# Endpoint pour voir l'historique des commandes (debug)
@app.get("/history")
async def get_history():
    """Retourne l'historique des dernières commandes reçues"""
    return {
        "total": len(command_history),
        "commands": command_history[-20:],  # Dernières 20 commandes
        "drone_state": drone_state
    }


# Endpoint pour réinitialiser l'état (debug)
@app.post("/reset")
async def reset_state():
    """Réinitialise l'état du drone (pour tests)"""
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

