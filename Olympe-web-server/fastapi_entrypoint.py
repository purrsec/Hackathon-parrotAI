"""
FastAPI Entrypoint - Point d'entrée pour messages utilisateur en langage naturel.

Responsabilités:
- Recevoir les messages en LANGAGE NATUREL depuis Discord/Next.js
- Valider le format minimal (message non vide)
- Logger les messages entrants
- Passer au module de traitement (NLP → Olympe)

Architecture:
    Utilisateur (Discord/Next.js)
         ↓ (langage naturel: "va inspecter la tour")
    FastAPI Entrypoint (ce fichier) ← REÇOIT SEULEMENT
         ↓ 
    NLP/Parser Module → Olympe Driver → Drone/Simulator
    (traduction + exécution)

Note: FastAPI NE FAIT PAS l'exécution Olympe, juste la réception des messages.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, Literal
from contextlib import asynccontextmanager
import json
import time
import logging
from datetime import datetime

# ============================================================================
# Configuration du logging
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Lifespan - Startup/Shutdown avec contexte moderne
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application avec lifespan context manager.
    
    Cette approche moderne remplace @app.on_event("startup") et @app.on_event("shutdown").
    """
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 FastAPI Message Gateway - Starting up")
    logger.info("=" * 80)
    logger.info("📋 Rôle: Réception de messages en langage naturel")
    logger.info("   - WebSocket: /ws")
    logger.info("   - REST API: POST /message")
    logger.info("   - Health: GET /health")
    logger.info("=" * 80)
    logger.info("📌 Note: Le traitement (NLP → Olympe) sera fait")
    logger.info("         par un module Python séparé")
    logger.info("=" * 80)
    
    yield  # L'application tourne
    
    # Shutdown
    logger.info("=" * 80)
    logger.info("🛑 FastAPI Message Gateway - Shutting down")
    logger.info(f"   Total messages reçus: {len(message_history)}")
    logger.info("=" * 80)

# ============================================================================
# Application FastAPI
# ============================================================================
app = FastAPI(
    title="Parrot Drone Controller API",
    description="WebSocket + REST API pour contrôler un drone Parrot via Olympe",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Autoriser les requêtes depuis le front Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Dev server alternatif
        "*"  # À restreindre en production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Modèles Pydantic - Validation des messages
# ============================================================================

class UserMessage(BaseModel):
    """
    Message utilisateur en langage naturel depuis Discord/Next.js.
    
    Format:
    {
        "id": "msg-123",
        "message": "va inspecter la tour Eiffel",
        "source": "discord",
        "user_id": "user-456"
    }
    """
    id: str = Field(..., description="Identifiant unique du message")
    message: str = Field(..., description="Message en langage naturel de l'utilisateur")
    source: Literal["discord", "nextjs", "api"] = Field(
        default="api",
        description="Source du message"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="ID de l'utilisateur (si disponible)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Métadonnées additionnelles (channel, timestamp, etc.)"
    )
    
    @field_validator('id')
    @classmethod
    def id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('id ne peut pas être vide')
        return v.strip()
    
    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('message ne peut pas être vide')
        return v.strip()


class MessageResponse(BaseModel):
    """
    Réponse après réception d'un message utilisateur.
    
    Format:
    {
        "id": "msg-123",
        "status": "received",
        "message": "Message reçu et en cours de traitement",
        "timestamp": "2025-11-08T17:30:00"
    }
    
    Note: Cette réponse indique juste que le message a été reçu.
    Le traitement réel (NLP + Olympe) se fait de manière asynchrone.
    """
    id: str = Field(..., description="ID du message original")
    status: Literal["received", "error", "rejected"] = Field(
        ...,
        description="Statut de la réception"
    )
    message: str = Field(..., description="Message de confirmation/erreur")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp ISO 8601"
    )


class HealthResponse(BaseModel):
    """État de santé du service"""
    status: str
    olympe_available: bool
    drone_connected: bool
    uptime_seconds: float


# ============================================================================
# État global (temporaire - à déplacer dans un module state)
# ============================================================================

# Métadonnées du service
service_start_time = time.time()

# Historique des messages (debug/audit)
message_history: list[Dict[str, Any]] = []
MAX_HISTORY_SIZE = 100

# ============================================================================
# Helpers - Construction de réponses
# ============================================================================

def received_response(msg_id: str, confirmation_msg: str) -> MessageResponse:
    """Réponse de réception réussie"""
    return MessageResponse(
        id=msg_id,
        status="received",
        message=confirmation_msg
    )


def error_response(msg_id: str, error_msg: str) -> MessageResponse:
    """Réponse d'erreur"""
    return MessageResponse(
        id=msg_id,
        status="error",
        message=error_msg
    )


def rejected_response(msg_id: str, reason: str) -> MessageResponse:
    """Réponse pour message rejeté (validation, etc.)"""
    return MessageResponse(
        id=msg_id,
        status="rejected",
        message=reason
    )


# ============================================================================
# Message Router - Traite les messages utilisateur
# ============================================================================

async def route_message(user_message: UserMessage) -> MessageResponse:
    """
    Router principal - Reçoit les messages en langage naturel.
    
    Cette fonction ne fait QUE recevoir et logger.
    Le traitement réel (NLP → Olympe) sera fait par un autre module.
    
    Args:
        user_message: Message utilisateur validé
        
    Returns:
        MessageResponse: Confirmation de réception
    """
    # Logging du message entrant
    logger.info("=" * 80)
    logger.info(f"📥 MESSAGE IN - ID: {user_message.id}")
    logger.info(f"   Source: {user_message.source}")
    logger.info(f"   User ID: {user_message.user_id or 'anonymous'}")
    logger.info(f"   Message: {user_message.message}")
    if user_message.metadata:
        logger.info(f"   Metadata: {user_message.metadata}")
    
    # Enregistrer dans l'historique
    _add_to_history(user_message)
    
    # TODO: Passer au module de traitement (NLP + Olympe)
    # Pour l'instant, on confirme juste la réception
    logger.info("📋 TODO: Passer le message au module de traitement NLP/Olympe")
    
    # Confirmation de réception
    result = received_response(
        user_message.id,
        f"Message reçu: '{user_message.message[:50]}...'" if len(user_message.message) > 50 
        else f"Message reçu: '{user_message.message}'"
    )
    
    # Logging de la réponse
    logger.info(f"📤 RESPONSE OUT - ID: {result.id}")
    logger.info(f"   Status: {result.status}")
    logger.info("=" * 80)
    
    return result


def _add_to_history(user_message: UserMessage) -> None:
    """Ajoute un message à l'historique (debug/audit)"""
    message_history.append({
        "id": user_message.id,
        "message": user_message.message,
        "source": user_message.source,
        "user_id": user_message.user_id,
        "metadata": user_message.metadata,
        "timestamp": datetime.now().isoformat(),
    })
    
    # Limiter la taille de l'historique
    if len(message_history) > MAX_HISTORY_SIZE:
        message_history.pop(0)


# ============================================================================
# WebSocket Endpoint - Canal de communication temps réel
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket pour recevoir des messages utilisateur en langage naturel.
    
    Format des messages entrants (JSON):
    {
        "id": "msg-123",
        "message": "va inspecter la tour Eiffel",
        "source": "discord",
        "user_id": "user-456"
    }
    
    Format des messages sortants (JSON):
    {
        "type": "message_received" | "error" | "welcome",
        "id": "msg-123",
        "status": "received",
        "message": "Message reçu: ...",
        "timestamp": "2025-11-08T17:30:00"
    }
    """
    await websocket.accept()
    client_id = f"ws-{id(websocket)}"
    logger.info(f"✅ WebSocket connecté: {client_id}")
    
    try:
        # Message d'accueil
        await websocket.send_json({
            "type": "welcome",
            "message": "Connected to Parrot Drone Message Gateway",
            "api_version": "1.0.0",
            "note": "Envoyez des messages en langage naturel",
            "timestamp": datetime.now().isoformat()
        })
        
        # Boucle de réception des messages
        while True:
            # Recevoir le message
            raw_message = await websocket.receive_text()
            
            # Parser le JSON
            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON invalide: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Invalid JSON: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            # Valider le format
            if not isinstance(payload, dict):
                await websocket.send_json({
                    "type": "error",
                    "message": "Message must be a JSON object",
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            if "id" not in payload or "message" not in payload:
                await websocket.send_json({
                    "type": "error",
                    "message": "Missing required fields: 'id' and 'message'",
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            # Créer le message utilisateur validé
            try:
                user_message = UserMessage(
                    id=str(payload["id"]),
                    message=str(payload["message"]),
                    source=payload.get("source", "api"),
                    user_id=payload.get("user_id"),
                    metadata=dict(payload.get("metadata", {}))
                )
            except Exception as e:
                logger.error(f"❌ Validation failed: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Validation error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            # Router le message
            result = await route_message(user_message)
            
            # Envoyer la réponse
            await websocket.send_json({
                "type": "message_received",
                "id": result.id,
                "status": result.status,
                "message": result.message,
                "timestamp": result.timestamp
            })
    
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket déconnecté: {client_id}")
    except Exception as e:
        logger.error(f"❌ Erreur WebSocket: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Internal error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        except Exception:
            pass
        await websocket.close()


# ============================================================================
# REST Endpoints - Alternative HTTP pour messages simples
# ============================================================================

@app.post("/message", response_model=MessageResponse)
async def post_message(user_message: UserMessage):
    """
    Endpoint REST pour envoyer un message en langage naturel.
    
    Usage:
        POST /message
        Content-Type: application/json
        
        {
            "id": "msg-123",
            "message": "va inspecter la tour Eiffel",
            "source": "nextjs",
            "user_id": "user-456"
        }
    
    Returns:
        MessageResponse avec status/message/timestamp
    """
    return await route_message(user_message)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check - État du service.
    
    Returns:
        - status: "ok" | "degraded" | "error"
        - olympe_available: bool (à implémenter)
        - drone_connected: bool (à implémenter)
        - uptime_seconds: float
    """
    uptime = time.time() - service_start_time
    
    return HealthResponse(
        status="ok",
        olympe_available=False,  # TODO: À implémenter dans le module Olympe
        drone_connected=False,  # TODO: À implémenter dans le module Olympe
        uptime_seconds=uptime
    )


@app.get("/history")
async def get_message_history():
    """
    Historique des messages reçus (debug/audit).
    
    Returns:
        - total: nombre total de messages
        - messages: liste des 20 derniers messages
    """
    return {
        "total": len(message_history),
        "messages": message_history[-20:],  # 20 derniers
        "timestamp": datetime.now().isoformat()
    }


@app.post("/reset")
async def reset_service():
    """
    Reset l'historique du service (debug uniquement).
    
    ⚠️  À désactiver en production!
    """
    global message_history
    message_history.clear()
    
    logger.warning("🔄 Service state reset!")
    
    return {
        "status": "reset",
        "message": "Message history cleared",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Main - Démarrage direct avec Uvicorn
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Uvicorn server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

