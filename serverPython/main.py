"""
Point d'entrée principal du serveur drone
"""

import sys
from pathlib import Path

# Si exécuté directement (pas comme module), ajouter le répertoire au path
if __name__ == "__main__":
    # Ajouter le répertoire parent au path pour permettre les imports absolus
    sys.path.insert(0, str(Path(__file__).parent))

# Imports conditionnels selon le mode d'exécution
try:
    # Essayer d'abord les imports relatifs (si importé comme module)
    from .config import CORS_ORIGINS, API_HOST, API_PORT, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT, DRONE_IP
    from .drone.state import DroneState
    from .drone.controller import DroneController
    from .api.routes import setup_routes
except ImportError:
    # Si échec, utiliser les imports absolus (si exécuté directement)
    from config import CORS_ORIGINS, API_HOST, API_PORT, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT, DRONE_IP
    from drone.state import DroneState
    from drone.controller import DroneController
    from api.routes import setup_routes

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(title="EDTH Drone Controller API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser l'état du drone et le contrôleur
drone_state = DroneState()
drone_controller = DroneController(drone_state, drone_ip=DRONE_IP)

# Configurer les routes
setup_routes(app, drone_controller, drone_state)


@app.on_event("startup")
async def startup():
    """Initialisation au démarrage"""
    logger.info("🚀 Démarrage du serveur drone...")
    drone_controller.connect()


@app.on_event("shutdown")
async def shutdown():
    """Nettoyage à l'arrêt"""
    logger.info("🛑 Arrêt du serveur drone...")
    drone_controller.disconnect()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)

