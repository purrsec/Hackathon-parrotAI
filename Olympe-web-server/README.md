Olympe-web-server
=================

But
---
- Recevoir des requêtes HTTP (POST) et relayer les commandes vers le drone/la simulation via Olympe.
- Exposer des endpoints simples pour le smoke test et le pilotage basique.

Notes
-----
- Pensez à définir `DRONE_IP` (ex: `10.202.0.1` en simulation).
- Voir `fastapi_controller.py` pour les routes.

