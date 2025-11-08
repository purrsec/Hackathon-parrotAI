# Olympe Web Server - Message Gateway

**Passerelle de réception** pour messages utilisateur en langage naturel.

## Architecture Simplifiée

```
Utilisateur (Next.js/Discord)
      ↓ (langage naturel: "va inspecter la tour")
fastapi_entrypoint.py ← REÇOIT SEULEMENT
      ↓
Module Python séparé (NLP → Olympe)
      ↓
Olympe Driver → Drone/Simulator
```

**Rôle de FastAPI:** Réception et validation uniquement.  
**Traitement:** Fait par un autre module Python local.

## Fichiers

### ✅ `fastapi_entrypoint.py` (IMPLÉMENTÉ)
Point d'entrée unique - Reçoit les messages en **langage naturel** via:
- **WebSocket** `/ws` - Communication temps réel bidirectionnelle
- **REST API** `POST /message` - Messages HTTP simples

**Responsabilités:**
- ✅ Réception de messages en langage naturel
- ✅ Validation minimale (message non vide)
- ✅ Logging structuré
- ✅ Confirmation de réception
- ✅ Historique des messages

**Ce que ça NE fait PAS:**
- ❌ Pas d'analyse NLP
- ❌ Pas de traduction en commandes Olympe
- ❌ Pas d'exécution sur le drone

### ✅ `test_message_gateway.py` (IMPLÉMENTÉ)
Script de test pour envoyer des messages au gateway.

### 🔜 Module de traitement (séparé)

Le traitement des messages sera fait par un **module Python séparé** qui:
1. **Écoute** les messages reçus par FastAPI (via queue/pubsub/callback)
2. **Parse** le langage naturel (LLM/NLP)
3. **Traduit** en commandes Olympe
4. **Exécute** sur le drone/simulateur
5. **Renvoie** les résultats au client

#### Composants à développer (hors FastAPI):
- `nlp_parser/` - Traitement du langage naturel
- `olympe_driver/` - Wrapper Olympe
- `mission_planner/` - Planification de trajectoires
- `safety/` - Règles de sécurité (geofence, batterie, etc.)

## Démarrage

### Développement
```bash
cd Olympe-web-server
uvicorn fastapi_entrypoint:app --reload --port 8000
```

### Production
```bash
uvicorn fastapi_entrypoint:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (à venir)
```bash
docker build -t olympe-api .
docker run -p 8000:8000 olympe-api
```

## Format des messages

### Message utilisateur (entrant)
```json
{
  "id": "msg-12345",
  "message": "va inspecter la tour Eiffel à 30 mètres",
  "source": "discord",
  "user_id": "user-789",
  "metadata": {
    "channel": "drone-commands",
    "timestamp": 1699459200
  }
}
```

### Réponse (sortante)
```json
{
  "id": "msg-12345",
  "status": "received",
  "message": "Message reçu: 'va inspecter la tour Eiffel à 30 mètres'",
  "timestamp": "2025-11-08T17:30:00"
}
```

**Note:** La réponse indique seulement que le message a été reçu. Le traitement réel se fait de manière asynchrone.

## Endpoints

### WebSocket: `/ws`
Communication bidirectionnelle temps réel.

**Avantages:**
- Télémétrie en continu
- Notifications instantanées
- Latence minimale

### REST API

#### `POST /message`
Envoyer un message en langage naturel.

#### `GET /health`
État du service (uptime, disponibilité).

#### `GET /history`
Historique des 20 derniers messages reçus.

#### `POST /reset` (debug)
Réinitialiser l'historique du service.

## Tests

### Test automatique avec Python
```bash
cd Olympe-web-server
python test_message_gateway.py
```

### Test WebSocket (avec websocat)
```bash
# Installation
cargo install websocat

# Connexion
websocat ws://localhost:8000/ws

# Envoyer un message
{"id": "test-1", "message": "va inspecter la tour", "source": "api"}
```

### Test REST (avec curl)
```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-1",
    "message": "décolle à 10 mètres",
    "source": "api",
    "user_id": "test-user"
  }'
```

### Test avec Python
```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Recevoir le message d'accueil
        welcome = await websocket.recv()
        print(f"< {welcome}")
        
        # Envoyer une commande
        cmd = {
            "id": "test-1",
            "action": "takeoff",
            "parameters": {"alt_m": 10}
        }
        await websocket.send(json.dumps(cmd))
        
        # Recevoir la réponse
        response = await websocket.recv()
        print(f"< {response}")

asyncio.run(test_websocket())
```

## TODO - Prochaines étapes

### Phase 1: Message Gateway ✅ (FAIT)
- [x] `fastapi_entrypoint.py` - Réception messages
- [x] Validation Pydantic
- [x] WebSocket + REST
- [x] Logging
- [x] Historique
- [x] Script de test

### Phase 2: Module de traitement (à faire - hors FastAPI)
- [ ] Créer module `nlp_parser/`
- [ ] Intégration LLM pour parsing
- [ ] Créer `olympe_driver/` wrapper
- [ ] Connexion drone/simulateur
- [ ] Traduction message → commandes Olympe

### Phase 3: Exécution et sécurité
- [ ] Module `mission_planner/`
- [ ] Module `safety/` (geofence, batterie, etc.)
- [ ] Gestion états et télémétrie
- [ ] Retour résultats au client

### Phase 4: Production
- [ ] Configuration (env vars)
- [ ] Logging avancé (fichiers)
- [ ] Tests unitaires
- [ ] Docker
- [ ] CI/CD

## Configuration

Variables d'environnement (à implémenter):
```bash
DRONE_IP=10.202.0.1
OLYMPE_MODE=simulator  # simulator | real
MAX_ALTITUDE_M=120
MIN_BATTERY_PCT=20
GEOFENCE_ENABLED=true
LOG_LEVEL=INFO
```

## Sécurité

⚠️ **Important:**
- Toujours tester en simulateur d'abord
- Vérifier la batterie avant vol
- Respecter les réglementations aériennes
- Garder une ligne de vue visuelle
- Avoir un plan d'urgence (RTH, atterrissage)

## Ressources

- [Olympe Documentation](https://developer.parrot.com/docs/olympe/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
