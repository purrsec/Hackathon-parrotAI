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
from natural_language_processor import get_nlp_processor
from mission_executor import get_drone_identity, execute_mission, check_olympe_ready
import asyncio
from mission_executor import get_drone_identity

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
# Global NLP Processor Instance
# ============================================================================

nlp_processor = None

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
    global nlp_processor
    
    logger.info("=" * 80)
    logger.info("🚀 FastAPI Message Gateway - Starting up")
    logger.info("=" * 80)
    logger.info("📋 Rôle: Réception de messages en langage naturel")
    logger.info("   - WebSocket: /ws")
    logger.info("   - REST API: POST /message")
    logger.info("   - Health: GET /health")
    logger.info("=" * 80)
    logger.info("🤖 Initializing NLP Processor with Mistral...")
    
    try:
        nlp_processor = get_nlp_processor()
        logger.info("✅ NLP Processor initialized successfully")
        logger.info("   - Mistral client configured")
        logger.info("   - POI data loaded from industrial_city.json")
    except Exception as e:
        logger.error(f"❌ Failed to initialize NLP Processor: {e}")
        nlp_processor = None
    
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
    # Confirmation fields
    is_confirmation: bool = Field(
        default=False,
        description="True si c'est une réponse de confirmation (yes/no)"
    )
    confirmation_for: Optional[str] = Field(
        default=None,
        description="ID de la mission à confirmer/annuler"
    )
    confirmation_value: Optional[bool] = Field(
        default=None,
        description="True pour yes/oui, False pour no/non"
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
    Réponse après traitement d'un message utilisateur.
    
    Format:
    {
        "id": "msg-123",
        "status": "processed",
        "message": "Mission DSL créée avec succès",
        "mission_dsl": {...},
        "timestamp": "2025-11-08T17:30:00"
    }
    
    Note: Cette réponse inclut maintenant le mission DSL généré par le NLP.
    """
    id: str = Field(..., description="ID du message original")
    status: Literal["processed", "error", "rejected"] = Field(
        ...,
        description="Statut du traitement"
    )
    message: str = Field(..., description="Message de confirmation/erreur")
    mission_dsl: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Mission DSL générée par le NLP (si succès)"
    )
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
pending_missions: dict[str, Dict[str, Any]] = {}

# ============================================================================
# Helpers - Construction de réponses
# ============================================================================

def processed_response(msg_id: str, confirmation_msg: str, mission_dsl: Dict[str, Any] = None) -> MessageResponse:
    """Réponse de traitement réussi avec mission DSL"""
    return MessageResponse(
        id=msg_id,
        status="processed",
        message=confirmation_msg,
        mission_dsl=mission_dsl
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
    Router principal - Reçoit les messages en langage naturel et les traite avec NLP.
    
    Processus:
    1. Log le message entrant
    2. Enregistre dans l'historique
    3. Traite avec le NLP processor pour générer une mission DSL
    4. Retourne la mission générée ou l'erreur
    
    Args:
        user_message: Message utilisateur validé
        
    Returns:
        MessageResponse: Réponse avec mission DSL ou erreur
    """
    total_start = time.perf_counter()
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
    
    # Vérifier que le NLP processor est disponible
    if nlp_processor is None:
        logger.error("❌ NLP Processor not initialized")
        result = error_response(
            user_message.id,
            "NLP Processor not available. Check server logs."
        )
    else:
        try:
            # Traiter le message avec le NLP processor
            logger.info("🤖 Processing with NLP Processor...")
            nlp_start = time.perf_counter()
            mission_dsl = await nlp_processor.process_user_message(user_message.message)
            nlp_elapsed_ms = (time.perf_counter() - nlp_start) * 1000.0
            logger.info(f"⏱️ NLP processing time: {nlp_elapsed_ms:.1f} ms")
            
            # Vérifier s'il y a une erreur dans la réponse
            if "error" in mission_dsl:
                logger.error(f"❌ NLP Processing error: {mission_dsl.get('error')}")
                result = error_response(
                    user_message.id,
                    f"NLP Error: {mission_dsl.get('error')}"
                )
            else:
                logger.info("✅ Mission DSL generated successfully")
                result = processed_response(
                    user_message.id,
                    "Mission DSL created successfully",
                    mission_dsl
                )
        
        except Exception as e:
            logger.error(f"❌ Error during NLP processing: {str(e)}", exc_info=True)
            result = error_response(
                user_message.id,
                f"Processing error: {str(e)}"
            )
    
    # Logging de la réponse
    logger.info(f"📤 RESPONSE OUT - ID: {result.id}")
    logger.info(f"   Status: {result.status}")
    if result.mission_dsl:
        logger.info(f"   Mission ID: {result.mission_dsl.get('missionId', 'N/A')}")
        logger.info(f"   Segments: {len(result.mission_dsl.get('segments', []))}")
    total_elapsed_ms = (time.perf_counter() - total_start) * 1000.0
    logger.info(f"⏱️ Total route time: {total_elapsed_ms:.1f} ms")
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
            
            # Contrôle: Confirmation d'exécution de mission (Yes/No)
            try:
                message_text = str(payload.get("message", "")).strip().lower()
                is_confirmation = ("confirm" in payload) or (message_text in ("yes", "no", "oui", "non"))
                if is_confirmation:
                    if "id" not in payload:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Confirmation requires 'id' of the mission message",
                            "timestamp": datetime.now().isoformat()
                        })
                        continue
                    confirm_id = str(payload["id"])
                    pending = pending_missions.get(confirm_id)
                    if not pending:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"No pending mission for id={confirm_id}",
                            "timestamp": datetime.now().isoformat()
                        })
                        continue
                    # Determine confirmation value
                    confirm_flag = payload.get("confirm")
                    if isinstance(confirm_flag, str):
                        confirm_flag = confirm_flag.strip().lower() in ("yes", "oui", "y", "true", "1")
                    elif isinstance(confirm_flag, bool):
                        confirm_flag = bool(confirm_flag)
                    else:
                        confirm_flag = message_text in ("yes", "oui", "y")
                    
                    if not confirm_flag:
                        # Cancel mission
                        pending_missions.pop(confirm_id, None)
                        await websocket.send_json({
                            "type": "mission_cancelled",
                            "id": confirm_id,
                            "message": "Mission cancelled by user",
                            "timestamp": datetime.now().isoformat()
                        })
                        continue
                    
                    # Confirmation accepted → lancer l'exécution en arrière-plan
                    # Vérifier readiness Olympe/Drone avant démarrage
                    ready, reason = await asyncio.to_thread(check_olympe_ready)
                    if not ready:
                        await websocket.send_json({
                            "type": "mission_execution_blocked",
                            "id": confirm_id,
                            "reason": reason,
                            "message": "Olympe/Drone not ready. Start Sphinx or connect to the drone, then retry.",
                            "timestamp": datetime.now().isoformat()
                        })
                        continue
                    
                    await websocket.send_json({
                        "type": "mission_execution_starting",
                        "id": confirm_id,
                        "message": "Mission execution started",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    mission_to_run = pending_missions.pop(confirm_id)["mission_dsl"]
                    
                    async def _run_and_stream():
                        try:
                            result = await asyncio.to_thread(execute_mission, mission_to_run, False)
                            await websocket.send_json({
                                "type": "mission_execution_result",
                                "id": confirm_id,
                                "status": result.get("status", "unknown"),
                                "report": result,
                                "timestamp": datetime.now().isoformat()
                            })
                        except Exception as exec_err:
                            logger.error(f"Mission execution error: {exec_err}", exc_info=True)
                            await websocket.send_json({
                                "type": "mission_execution_result",
                                "id": confirm_id,
                                "status": "error",
                                "report": {"errors": [str(exec_err)]},
                                "timestamp": datetime.now().isoformat()
                            })
                    
                    asyncio.create_task(_run_and_stream())
                    continue
            except Exception as control_err:
                logger.error(f"Control handling error: {control_err}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "message": f"Control handling error: {str(control_err)}",
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
                    source=payload.get("source", "websocket"),
                    user_id=payload.get("user_id"),
                    metadata=dict(payload.get("metadata", {})),
                    is_confirmation=payload.get("is_confirmation", False),
                    confirmation_for=payload.get("confirmation_for"),
                    confirmation_value=payload.get("confirmation_value")
                )
            except Exception as e:
                logger.error(f"❌ Validation failed: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Validation error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
                continue
            
            # Vérifier si c'est une réponse de confirmation (via le champ dédié)
            if user_message.is_confirmation:
                # Vérifier que l'ID de mission est fourni
                if not user_message.confirmation_for:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Missing confirmation_for field",
                        "timestamp": datetime.now().isoformat()
                    })
                    continue
                
                # Vérifier que la mission existe
                mission_id = str(user_message.confirmation_for)
                if mission_id not in pending_missions:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"No pending mission found with ID: {mission_id}",
                        "timestamp": datetime.now().isoformat()
                    })
                    continue
                
                mission_data = pending_missions[mission_id]
                
                if user_message.confirmation_value:
                    # L'utilisateur confirme - exécuter la mission
                    logger.info(f"✅ User confirmed mission execution: {mission_id}")
                    
                    await websocket.send_json({
                        "type": "mission_confirmed",
                        "id": mission_id,
                        "message": "Mission confirmed! Executing...",
                        "status": "executing",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # TODO: Appeler le mission executor ici
                    # from mission_executor import execute_mission
                    # await execute_mission(mission_data["mission_dsl"])
                    
                    # Retirer de la liste des missions en attente
                    del pending_missions[mission_id]
                    
                else:
                    # L'utilisateur refuse - annuler la mission
                    logger.info(f"❌ User cancelled mission: {mission_id}")
                    
                    await websocket.send_json({
                        "type": "mission_cancelled",
                        "id": mission_id,
                        "message": "Mission cancelled by user",
                        "status": "cancelled",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Retirer de la liste des missions en attente
                    del pending_missions[mission_id]
                
                continue  # Ne pas traiter comme un message normal
            
            # Router le message normal
            result = await route_message(user_message)
            
            # Envoyer la réponse avec mission DSL si disponible
            response_json = {
                "type": "message_processed",
                "id": result.id,
                "status": result.status,
                "message": result.message,
                "timestamp": result.timestamp
            }
            
            # Ajouter la mission DSL si elle existe
            if result.mission_dsl:
                response_json["mission_dsl"] = result.mission_dsl
            
            await websocket.send_json(response_json)
            
            # Si une mission a été générée, envoyer un prompt de confirmation utilisateur
            if result.mission_dsl and result.status == "processed":
                try:
                    # Stocker la mission en attente d'exécution
                    pending_missions[str(result.id)] = {
                        "mission_dsl": result.mission_dsl,
                        "created_at": datetime.now().isoformat(),
                        "source_message": payload
                    }
                    # Récupérer l'identité du drone (best-effort)
                    try:
                        identity = get_drone_identity()
                    except Exception:
                        identity = {"id": "unknown", "ip": "unknown"}
                    
                    await websocket.send_json({
                        "type": "mission_confirmation",
                        "id": result.id,
                        "drone_id": identity.get("id", "unknown"),
                        "drone_ip": identity.get("ip", "unknown"),
                        "message": "Mission loaded on drone. Ready to execute? (Yes/No)",
                        "ready": "No",
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.error(f"❌ Failed to send mission confirmation: {e}", exc_info=True)
    
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

