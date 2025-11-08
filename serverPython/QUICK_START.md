# 🚀 Guide de Démarrage Rapide

## Installation

```bash
cd python_controller
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Démarrage

```bash
# Activer le venv si pas déjà fait
source venv/bin/activate

# Lancer le serveur (depuis le dossier python_controller)
python main.py
```

Le serveur sera accessible sur `http://localhost:8000`

## Test rapide

```bash
# Vérifier que le serveur fonctionne
curl http://localhost:8000/health

# Tester un décollage
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"id":"test_001","action":"takeoff","parameters":{"alt_m":50}}'
```

## Structure des fichiers

- `main.py` : Point d'entrée
- `config.py` : Configuration
- `api/routes.py` : Routes HTTP
- `drone/controller.py` : Logique drone
- `drone/state.py` : État du drone
- `models/command.py` : Modèles de données

Voir `ARCHITECTURE.md` pour plus de détails.

