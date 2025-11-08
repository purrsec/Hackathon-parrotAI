"""
Gestion de l'état du drone
"""

from typing import Dict, Any
import time


class DroneState:
    """Gère l'état global du drone"""
    
    def __init__(self):
        self.state = {
            "connected": False,
            "state": "idle",  # idle, flying, hovering, landing
            "battery": 100,
            "gps": {"lat": 48.8566, "lon": 2.3522, "alt": 0},
            "home": {"lat": 48.8566, "lon": 2.3522, "alt": 0},
        }
        self.command_history = []
    
    def get_state(self) -> Dict[str, Any]:
        """Retourne l'état actuel du drone"""
        return self.state.copy()
    
    def update_state(self, **kwargs):
        """Met à jour l'état du drone"""
        self.state.update(kwargs)
    
    def update_gps(self, lat: float = None, lon: float = None, alt: float = None):
        """Met à jour la position GPS"""
        if lat is not None:
            self.state["gps"]["lat"] = lat
        if lon is not None:
            self.state["gps"]["lon"] = lon
        if alt is not None:
            self.state["gps"]["alt"] = alt
    
    def add_command_to_history(self, command_id: str, action: str, parameters: Dict[str, Any]):
        """Ajoute une commande à l'historique"""
        self.command_history.append({
            "id": command_id,
            "action": action,
            "parameters": parameters,
            "timestamp": time.time(),
        })
        # Garder seulement les 50 dernières commandes
        if len(self.command_history) > 50:
            self.command_history.pop(0)
    
    def get_history(self, limit: int = 20) -> list:
        """Retourne l'historique des commandes"""
        return self.command_history[-limit:]
    
    def reset(self):
        """Réinitialise l'état du drone"""
        self.state = {
            "connected": True,
            "state": "idle",
            "battery": 100,
            "gps": {"lat": 48.8566, "lon": 2.3522, "alt": 0},
            "home": {"lat": 48.8566, "lon": 2.3522, "alt": 0},
        }
        self.command_history = []

