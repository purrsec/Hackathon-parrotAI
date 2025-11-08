Olympe-web-server
=================

But
---
- Entrypoint unique: reçoit les messages depuis le Front (NextJS) ou Discord.
- Supporte WebSocket (`/ws`) pour échanges bi-directionnels et POST (`/cmd`) en fallback.
- Route les commandes vers Olympe (drone/simu) et intègre l’NLP/LLM côté serveur.

Notes
-----
- Pensez à définir `DRONE_IP` (ex: `10.202.0.1` en simulation).
- Voir `fastapi_controller.py` pour l’API et `nlp_router.py` pour l’interprétation NL.

Message contract (MVP)
----------------------
- WebSocket/POST commande:
  ```json
  { "id": "req-123", "action": "takeoff", "parameters": { "alt_m": 10 } }
  ```
- NLP côté serveur:
  ```json
  { "id": "req-124", "action": "nlp", "parameters": { "text": "décolle à 10m puis RTH" } }
  ```
- Réponse:
  ```json
  { "id": "req-124", "status": "success|error|in_progress", "message": "...", "data": { ... } }
  ```

