"""
Routes FastAPI pour l'API drone
"""

import logging
from fastapi import APIRouter

# Imports conditionnels pour supporter exécution directe et import comme module
try:
    from ..models.command import Command, CommandResponse, err
    from ..drone.controller import DroneController
    from ..drone.state import DroneState
except ImportError:
    from models.command import Command, CommandResponse, err
    from drone.controller import DroneController
    from drone.state import DroneState

logger = logging.getLogger(__name__)

router = APIRouter()


def setup_routes(app, drone_controller: DroneController, drone_state: DroneState):
    """Configure les routes de l'API"""
    
    @router.post("/cmd", response_model=CommandResponse)
    async def cmd(command: Command):
        """Endpoint principal pour exécuter des commandes drone"""
        try:
            # Log détaillé de la commande reçue
            logger.info("=" * 80)
            logger.info(f"📥 COMMANDE REÇUE - ID: {command.id}")
            logger.info(f"   Action: {command.action}")
            logger.info(f"   Paramètres: {command.parameters}")
            
            # Ajouter à l'historique
            drone_state.add_command_to_history(command.id, command.action, command.parameters)
            
            action = command.action.lower()
            logger.info(f"   → Traitement de l'action: {action}")
            
            # Router vers le bon handler
            if action == "takeoff":
                result = await drone_controller.handle_takeoff(command)
            elif action == "goto":
                result = await drone_controller.handle_goto(command)
            elif action == "circle":
                result = await drone_controller.handle_circle(command)
            elif action == "capture":
                result = await drone_controller.handle_capture(command)
            elif action == "rth":
                result = await drone_controller.handle_return_to_home(command)
            elif action == "land":
                result = await drone_controller.handle_land(command)
            elif action == "status":
                result = await drone_controller.handle_status(command)
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
    
    @router.get("/health")
    async def health():
        """Endpoint de santé"""
        return {
            "status": "ok",
            "drone_connected": drone_state.state["connected"],
            "olympe_available": drone_controller.olympe_available
        }
    
    @router.get("/history")
    async def get_history():
        """Retourne l'historique des dernières commandes reçues"""
        return {
            "total": len(drone_state.command_history),
            "commands": drone_state.get_history(limit=20),
            "drone_state": drone_state.get_state()
        }
    
    @router.post("/reset")
    async def reset_state():
        """Réinitialise l'état du drone (pour tests)"""
        drone_state.reset()
        logger.info("🔄 État du drone réinitialisé")
        return {"status": "reset", "drone_state": drone_state.get_state()}
    
    # Enregistrer les routes dans l'app
    app.include_router(router)

