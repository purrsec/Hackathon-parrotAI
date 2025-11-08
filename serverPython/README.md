# EDTH - Serveur de Contrôle Drone

Serveur FastAPI modulaire pour contrôler un drone Parrot ANAFI via Olympe SDK.

## 📁 Structure du Projet

```
python_controller/
├── main.py                 # Point d'entrée principal
├── config.py               # Configuration (IP, ports, CORS, etc.)
├── requirements.txt        # Dépendances Python
│
├── api/                    # Routes FastAPI
│   ├── __init__.py
│   └── routes.py           # Définition des endpoints
│
├── drone/                  # Logique de contrôle du drone
│   ├── __init__.py
│   ├── state.py            # Gestion de l'état du drone
│   └── controller.py      # Handlers des commandes Olympe
│
└── models/                 # Modèles Pydantic
    ├── __init__.py
    └── command.py          # Command et CommandResponse
```

## 🚀 Installation

### 1. Créer un environnement virtuel

```bash
cd python_controller
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. (Optionnel) Installer Olympe

Pour utiliser avec un vrai drone ou Sphinx :

```bash
# Sur Ubuntu 22.04+ (x64)
pip3 install parrot-olympe

# Ou depuis les sources (voir doc Olympe)
```

## ⚙️ Configuration

### Variables d'environnement

Créez un fichier `.env` (optionnel) :

```env
DRONE_IP=10.202.0.1
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

Ou modifiez directement `config.py`.

## 🏃 Démarrage

### Mode développement

**Option 1 : Exécution directe (recommandé)**

```bash
# Depuis le dossier python_controller
python main.py
```

**Option 2 : Avec uvicorn**

```bash
# Depuis le dossier python_controller
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 3 : Comme module (depuis le répertoire parent)**

```bash
# Depuis le répertoire parent (EDTH)
python -m python_controller.main
```

### Mode production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Le serveur sera accessible sur `http://localhost:8000`

## 📡 Endpoints API

### `POST /cmd`

Exécute une commande drone.

**Body:**
```json
{
  "id": "cmd_123",
  "action": "takeoff",
  "parameters": {
    "alt_m": 50
  }
}
```

**Actions disponibles:**
- `takeoff` - Décollage (paramètres: `alt_m` optionnel)
- `goto` - Navigation GPS (paramètres: `lat`, `lon`, `alt_m`, `orientation_mode` optionnel, `heading` optionnel)
- `circle` - Orbite circulaire (paramètres: `target_lat`, `target_lon`, `alt_m`, `radius_m`, `laps`, `direction`)
- `capture` - Capture photo/vidéo (paramètres: `type`="photo"|"video", `duration_s` pour vidéo)
- `rth` - Retour au point de départ
- `land` - Atterrissage
- `status` - Statut du drone

**Réponse:**
```json
{
  "id": "cmd_123",
  "status": "success",
  "message": "Décollage réussi à 50m",
  "data": {
    "altitude": 50,
    "state": "hovering"
  }
}
```

### `GET /health`

Vérifie l'état du serveur et la connexion au drone.

**Réponse:**
```json
{
  "status": "ok",
  "drone_connected": true,
  "olympe_available": true
}
```

### `GET /history`

Retourne l'historique des dernières commandes (debug).

**Réponse:**
```json
{
  "total": 10,
  "commands": [...],
  "drone_state": {...}
}
```

### `POST /reset`

Réinitialise l'état du drone (debug).

## 🔧 Architecture

### Séparation des responsabilités

1. **`main.py`** : Point d'entrée, configuration FastAPI, cycle de vie
2. **`config.py`** : Configuration centralisée
3. **`api/routes.py`** : Routes HTTP, routage des commandes
4. **`drone/controller.py`** : Logique métier, appels Olympe
5. **`drone/state.py`** : Gestion de l'état (singleton)
6. **`models/command.py`** : Modèles de données Pydantic

### Flux d'exécution

```
Client HTTP
    ↓
POST /cmd
    ↓
api/routes.py (router)
    ↓
drone/controller.py (handler)
    ↓
Olympe SDK (si disponible)
    ↓
drone/state.py (mise à jour état)
    ↓
Réponse JSON
```

## 🧪 Mode Mock

Si Olympe n'est pas disponible, le serveur fonctionne en mode mock :
- Toutes les commandes sont simulées
- L'état du drone est mis à jour localement
- Parfait pour tester l'API sans drone réel

## 📝 Exemples d'utilisation

### Décollage

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "id": "cmd_001",
    "action": "takeoff",
    "parameters": {"alt_m": 50}
  }'
```

### Navigation GPS

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "id": "cmd_002",
    "action": "goto",
    "parameters": {
      "lat": 48.8566,
      "lon": 2.3522,
      "alt_m": 100,
      "orientation_mode": "TO_TARGET"
    }
  }'
```

### Orbite

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "id": "cmd_003",
    "action": "circle",
    "parameters": {
      "target_lat": 48.8566,
      "target_lon": 2.3522,
      "alt_m": 100,
      "radius_m": 50,
      "laps": 1,
      "direction": "CW"
    }
  }'
```

## 🐛 Débogage

### Logs

Les logs sont affichés dans la console avec :
- 📥 Commandes reçues
- 📤 Réponses envoyées
- ⚙️ Exécution des commandes
- ❌ Erreurs

### Historique

Consultez `/history` pour voir les dernières commandes.

### Reset

Utilisez `/reset` pour réinitialiser l'état du drone.

## 🔒 Sécurité

- Le serveur écoute sur `0.0.0.0` par défaut (toutes les interfaces)
- CORS est configuré pour autoriser uniquement les origines spécifiées
- En production, utilisez un reverse proxy (nginx) avec HTTPS

## 📚 Documentation Olympe

Pour plus d'informations sur Olympe SDK :
- [Documentation officielle](https://developer.parrot.com/docs/olympe/)
- [API Reference](https://developer.parrot.com/docs/olympe/arsdkng/olympe.messages.html)

## 🤝 Contribution

Pour ajouter une nouvelle commande :

1. Ajouter le handler dans `drone/controller.py`
2. Ajouter le routage dans `api/routes.py`
3. Documenter dans ce README

## 📄 Licence

Projet développé pour le Hackathon Parrot-2
