# 🚁 ParrotAI - Quick Start Guide

Guide de démarrage rapide pour lancer le système complet de contrôle de drone par langage naturel.

---

## 📋 Prérequis

- **Parrot Sphinx** : Simulateur de drone installé
- **Unreal Engine 4** : Environnement 3D (monde industrial-city)
- **Python 3.12+** avec `uv` installé
- **Mistral API Key** : Configurée dans l'environnement

---

## 🚀 Démarrage du système complet

Le système nécessite **4 terminaux** pour fonctionner :

### Terminal 1 : Simulateur Sphinx 🔧

Lance le simulateur Parrot Sphinx avec le drone ANAFI Ai :

```bash
sphinx "/opt/parrot-sphinx/usr/share/sphinx/drones/anafi_ai.drone"::name="drone_1"::pose="120 120 2 0 0 200"::firmware="https://firmware.parrot.com/Versions/anafi2/pc/%23latest/images/anafi2-pc.ext2.zip"
```

**Paramètres** :
- `name="drone_1"` : ID du drone
- `pose="120 120 2 0 0 200"` : Position initiale (x y z roll pitch yaw)
- Firmware : ANAFI 2 PC (dernière version)

**Attendez** : Le message `Drone is ready` avant de continuer.

---

### Terminal 2 : Monde Unreal Engine 🌍

Lance l'environnement 3D industrial-city :

```bash
parrot-ue4-industrial-city
```

**Attendez** : Que le monde soit complètement chargé (vous verrez le drone dans l'environnement).

---

### Terminal 3 : Serveur FastAPI + Olympe 🖥️

Lance le serveur qui traite les commandes en langage naturel :

```bash
cd Olympe-web-server
FAST_MISSION_DSL_MODEL=mistral-tiny-latest FAST_MISSION_MAX_TOKENS=900 uv run fastapi_entrypoint.py
```

**Variables d'environnement** :
- `FAST_MISSION_DSL_MODEL` : Modèle Mistral à utiliser (tiny-latest = rapide + économique)
- `FAST_MISSION_MAX_TOKENS` : Limite de tokens pour la génération

**Attendez** : Le message `Application startup complete` et `Uvicorn running on http://0.0.0.0:8000`

---

### Terminal 4 : Client de test / Chat 💬

Lance le client de test en ligne de commande :

```bash
cd client_debug
uv run chat_client.py
```

**Attendez** : Le message `Connected to ws://localhost:8000/ws`

---

## 🎮 Utilisation

Une fois tous les terminaux lancés, vous pouvez envoyer des commandes en langage naturel :

### Exemples de commandes

```
Visit a building and come back home
```
→ Visite 1 seul POI

```
Visit all buildings
```
→ Visite tous les POI disponibles

```
Inspect the Advertising Board at 40 meters altitude
```
→ Inspection spécifique avec altitude personnalisée

```
Fly over the Ventilation Pipes then return home
```
→ Vol au-dessus d'un POI spécifique

### Workflow

1. **Tapez votre commande** dans le chat client
2. Le serveur **génère une mission DSL** via Mistral
3. Vous voyez le **résumé de la mission** avec :
   - 🤖 Understanding : Ce que le drone va faire
   - 📋 Mission DSL : Les segments de la mission
4. **Confirmez** en tapant `yes` ou `oui`
5. Le drone **exécute la mission** dans le simulateur
6. Vous recevez un **rapport d'exécution** avec le statut

---

## 🗺️ Points d'intérêt (POI) disponibles

D'après `maps/industrial_city.json` :

1. **Advertising Board**
   - Latitude: 48.87882157897949
   - Longitude: 2.368181582689285
   - Altitude: 19m

2. **Ventilation Pipes**
   - Latitude: 48.87881527709961
   - Longitude: 2.3665938951969148
   - Altitude: 20m

**Obstacle Box** : Zone restreinte entre 0-15m d'altitude

---

## ⚙️ Configuration avancée

### Variables d'environnement optionnelles

```bash
# Modèle Mistral
FAST_MISSION_DSL_MODEL=mistral-tiny-latest   # Par défaut: mistral-medium-latest
FAST_MISSION_MAX_TOKENS=900                   # Par défaut: 600

# Timeouts
TIMEOUT_SEC=25                                # Par défaut: 25s
MOVE_TIMEOUT_SEC=120                          # Par défaut: 120s
RTH_TIMEOUT_SEC=300                           # Par défaut: 300s

# Drone
DRONE_IP=10.202.0.1                           # Par défaut: 10.202.0.1
```

### Mode strict

```bash
STRICT=1  # Arrête la mission au premier échec (par défaut)
STRICT=0  # Continue même si un segment échoue
```

---

## 🐛 Dépannage

### Le drone ne répond pas
- ✅ Vérifiez que Sphinx affiche `Drone is ready`
- ✅ Vérifiez que le monde UE4 est chargé
- ✅ Vérifiez l'IP du drone : `DRONE_IP=10.202.0.1`

### Erreur "Connection failed"
- ✅ Sphinx doit être lancé AVANT le serveur Olympe
- ✅ Vérifiez le firewall (port 8000 pour FastAPI)

### "POI state unavailable"
- ⚠️ C'est un WARNING normal dans le simulateur
- ✅ L'inspection fonctionne quand même

### Le drone crashe dans un bâtiment
- ✅ Altitude par défaut : 30m (safe clearance au-dessus de l'obstacle box à 15m)
- ✅ Demandez une altitude plus haute : "at 40 meters altitude"

### Landing échoue après RTH
- ✅ Déjà corrigé : Le système détecte si le drone est déjà au sol

---

## 📚 Architecture

```
User Input (Natural Language)
    ↓
FastAPI WebSocket Server
    ↓
NLP Processor (Mistral AI)
    ↓
Mission DSL (JSON)
    ↓
Mission Executor (Olympe)
    ↓
Parrot Sphinx Simulator
    ↓
Unreal Engine 4 (Visualization)
```

---

## 🔗 Fichiers importants

- `Olympe-web-server/fastapi_entrypoint.py` : Serveur WebSocket principal
- `Olympe-web-server/natural_language_processor.py` : Traduction NL → Mission DSL
- `Olympe-web-server/mission_executor.py` : Exécution des missions sur le drone
- `client_debug/chat_client.py` : Client de test en terminal
- `maps/industrial_city.json` : Définition des POI et obstacles
- `archive/apps/cli/poi_inspection.py` : Script de référence pour POI inspection (archivé)

---

## 📝 Notes

- **Altitude de sécurité** : 30m par défaut (obstacle box max = 15m)
- **RTH automatique** : Return-to-home avec atterrissage automatique activé
- **Timeout RTH** : 300 secondes (5 minutes) par défaut
- **Logs verbeux** : Olympe en mode WARNING (moins de spam dans les logs)

---

## ✨ Fonctionnalités

✅ Traitement en langage naturel (via Mistral AI)  
✅ Génération automatique de missions DSL  
✅ Confirmation utilisateur avant exécution  
✅ Inspection de POI avec rotation  
✅ Return-to-home automatique  
✅ Gestion des erreurs et safety fallbacks  
✅ Rapport d'exécution détaillé  
✅ Support singulier/pluriel ("a building" vs "all buildings")  

---

Bon vol ! 🚁✨

