"""
Modèles de commande pour l'API
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional


class Command(BaseModel):
    """Modèle pour une commande drone"""
    id: str
    action: str
    parameters: Dict[str, Any] = {}


class CommandResponse(BaseModel):
    """Modèle pour la réponse d'une commande"""
    id: str
    status: str  # success, in_progress, error
    message: str
    data: Dict[str, Any] = {}


def ok(id: str, msg: str, data: Optional[Dict[str, Any]] = None) -> CommandResponse:
    """Helper pour créer une réponse de succès"""
    return CommandResponse(
        id=id, status="success", message=msg, data=data or {}
    )


def err(id: str, msg: str) -> CommandResponse:
    """Helper pour créer une réponse d'erreur"""
    return CommandResponse(
        id=id, status="error", message=msg, data={}
    )


def in_progress(id: str, msg: str, data: Optional[Dict[str, Any]] = None) -> CommandResponse:
    """Helper pour créer une réponse en cours"""
    return CommandResponse(
        id=id, status="in_progress", message=msg, data=data or {}
    )

