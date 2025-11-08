# Architecture du Serveur Drone

## 📐 Vue d'ensemble

Le serveur est organisé en modules séparés pour une meilleure maintenabilité et testabilité.

```
┌─────────────────────────────────────────────────────────┐
│                    main.py                              │
│  Point d'entrée, configuration FastAPI, cycle de vie   │
└──────────────┬──────────────────────────────────────────┘
               │
               ├─────────────────┬──────────────────┐
               │                 │                  │
    ┌──────────▼──────────┐  ┌───▼────────┐  ┌──────▼──────┐
    │   api/routes.py     │  │  config.py │  │ drone/      │
    │   Routes HTTP       │  │  Config    │  │ Controller  │
    └──────────┬──────────┘  └────────────┘  └──────┬──────┘
               │                                     │
               │                              ┌──────▼──────┐
               │                              │ drone/     │
               │                              │ state.py   │
               │                              └────────────┘
               │
    ┌──────────▼──────────┐
    │  models/command.py  │
    │  Modèles Pydantic   │
    └─────────────────────┘
```

## 🔧 Modules

### 1. `main.py` - Point d'entrée

**Responsabilités :**
- Création de l'application FastAPI
- Configuration du middleware CORS
- Initialisation des composants (DroneState, DroneController)
- Gestion du cycle de vie (startup/shutdown)

**Code clé :**
```python
app = FastAPI(title="EDTH Drone Controller API")
drone_state = DroneState()
drone_controller = DroneController(drone_state, drone_ip=DRONE_IP)
setup_routes(app, drone_controller, drone_state)
```

### 2. `config.py` - Configuration

**Responsabilités :**
- Variables d'environnement
- Configuration par défaut
- CORS origins

**Variables :**
- `DRONE_IP` : IP du drone (défaut: 10.202.0.1)
- `API_HOST` : Host du serveur (défaut: 0.0.0.0)
- `API_PORT` : Port du serveur (défaut: 8000)
- `CORS_ORIGINS` : Liste des origines autorisées

### 3. `api/routes.py` - Routes HTTP

**Responsabilités :**
- Définition des endpoints FastAPI
- Routage des commandes vers les handlers
- Logging des requêtes/réponses

**Endpoints :**
- `POST /cmd` : Exécute une commande drone
- `GET /health` : Vérifie l'état du serveur
- `GET /history` : Historique des commandes
- `POST /reset` : Réinitialise l'état

**Flux :**
```
POST /cmd
  ↓
routes.py (router)
  ↓
drone_controller.handle_XXX()
  ↓
Réponse CommandResponse
```

### 4. `drone/state.py` - État du drone

**Responsabilités :**
- Stockage de l'état global du drone
- Historique des commandes
- Méthodes de mise à jour

**État stocké :**
```python
{
    "connected": bool,
    "state": str,  # idle, flying, hovering, landing
    "battery": int,  # 0-100
    "gps": {"lat": float, "lon": float, "alt": float},
    "home": {"lat": float, "lon": float, "alt": float}
}
```

**Méthodes principales :**
- `get_state()` : Retourne l'état actuel
- `update_state(**kwargs)` : Met à jour l'état
- `update_gps(lat, lon, alt)` : Met à jour la position GPS
- `add_command_to_history()` : Ajoute une commande à l'historique
- `reset()` : Réinitialise l'état

### 5. `drone/controller.py` - Contrôleur du drone

**Responsabilités :**
- Gestion de la connexion Olympe
- Exécution des commandes drone
- Handlers pour chaque action

**Handlers disponibles :**
- `handle_takeoff()` : Décollage
- `handle_goto()` : Navigation GPS
- `handle_circle()` : Orbite circulaire
- `handle_capture()` : Capture photo/vidéo
- `handle_return_to_home()` : Retour au point de départ
- `handle_land()` : Atterrissage
- `handle_status()` : Statut du drone

**Mode Mock :**
Si Olympe n'est pas disponible, tous les handlers fonctionnent en mode mock (simulation).

### 6. `models/command.py` - Modèles de données

**Responsabilités :**
- Définition des modèles Pydantic
- Validation des données
- Helpers pour créer des réponses

**Modèles :**
- `Command` : Commande reçue
- `CommandResponse` : Réponse envoyée

**Helpers :**
- `ok(id, msg, data)` : Crée une réponse de succès
- `err(id, msg)` : Crée une réponse d'erreur
- `in_progress(id, msg, data)` : Crée une réponse en cours

## 🔄 Flux d'exécution

### Exemple : Commande `takeoff`

```
1. Client HTTP
   POST /cmd
   {
     "id": "cmd_001",
     "action": "takeoff",
     "parameters": {"alt_m": 50}
   }
   ↓
2. api/routes.py
   - Log de la commande
   - Ajout à l'historique
   - Routage vers handler
   ↓
3. drone/controller.py
   handle_takeoff(cmd)
   - Vérifie Olympe disponible
   - Exécute TakeOff() + moveBy()
   - Met à jour l'état
   ↓
4. drone/state.py
   update_state(state="hovering")
   update_gps(alt=50)
   ↓
5. Réponse JSON
   {
     "id": "cmd_001",
     "status": "success",
     "message": "Décollage réussi à 50m",
     "data": {...}
   }
```

## 🧩 Ajouter une nouvelle commande

### Étape 1 : Ajouter le handler dans `drone/controller.py`

```python
async def handle_ma_commande(self, cmd: Command) -> CommandResponse:
    """Gère ma nouvelle commande"""
    param = cmd.parameters.get("param")
    
    if self.olympe_available and self.drone:
        try:
            # Code Olympe
            result = self.drone(...).wait()
            if result.success():
                return ok(cmd.id, "Commande réussie", {...})
            else:
                return err(cmd.id, "Échec")
        except Exception as e:
            return err(cmd.id, f"Erreur: {str(e)}")
    else:
        # Mode mock
        return ok(cmd.id, "[MOCK] Commande réussie", {...})
```

### Étape 2 : Ajouter le routage dans `api/routes.py`

```python
elif action == "ma_commande":
    result = await drone_controller.handle_ma_commande(command)
```

### Étape 3 : Documenter dans `README.md`

## 🧪 Tests

### Test manuel avec curl

```bash
# Décollage
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"id":"test_001","action":"takeoff","parameters":{"alt_m":50}}'

# Statut
curl http://localhost:8000/health
```

### Test en mode mock

Le serveur fonctionne automatiquement en mode mock si Olympe n'est pas disponible.

## 🔍 Débogage

### Logs

Tous les logs sont affichés dans la console avec des emojis pour faciliter la lecture :
- 📥 Commandes reçues
- 📤 Réponses envoyées
- ⚙️ Exécution des commandes
- ❌ Erreurs

### Historique

Consultez `/history` pour voir les dernières commandes et l'état actuel.

### Reset

Utilisez `/reset` pour réinitialiser l'état du drone.

## 📦 Dépendances

- `fastapi` : Framework web
- `uvicorn` : Serveur ASGI
- `pydantic` : Validation de données
- `olympe` : SDK Parrot (optionnel, pour drone réel)

## 🚀 Déploiement

### Développement

```bash
python main.py
```

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (à venir)

Un Dockerfile peut être ajouté pour faciliter le déploiement.

