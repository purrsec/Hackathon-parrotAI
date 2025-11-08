# 📋 Commandes à Implémenter dans le Serveur Python

Liste des commandes Olympe à ajouter au serveur FastAPI pour supporter tous les scénarios.

---

## ✅ Déjà Implémentées

- `takeoff` → `TakeOff()`
- `goto` → `moveTo()`
- `circle` → (simulé, à implémenter avec `Circle()`)
- `capture` → (simulé, à implémenter avec MediaRecordState)
- `rth` → `NavigateHome(start=1)`
- `land` → `Landing()`
- `status` → (partiel, à améliorer)

---

## 🚨 Urgence et Sécurité (Priorité Haute)

### `emergency`
**Action :** Coupe les moteurs immédiatement
**Olympe :** `Emergency()`
**Paramètres :** Aucun
**Réponse :** `FlyingStateChanged(state='emergency')`

```python
async def handle_emergency(cmd: Command) -> CommandResponse:
    if OLYMPE_AVAILABLE and drone:
        try:
            result = drone(Emergency() >> FlyingStateChanged(state="emergency", _timeout=5)).wait()
            if result.success():
                drone_state["state"] = "emergency"
                return ok(cmd.id, "Arrêt d'urgence activé")
        except Exception as e:
            return err(cmd.id, f"Erreur arrêt d'urgence: {str(e)}")
    else:
        # Mock
        drone_state["state"] = "emergency"
        return ok(cmd.id, "[MOCK] Arrêt d'urgence activé")
```

---

## 🎯 Navigation Avancée (Priorité Haute)

### `moveBy`
**Action :** Mouvement relatif
**Olympe :** `moveBy(dX, dY, dZ, dPsi)`
**Paramètres :** `{dX: float, dY: float, dZ: float, dPsi: float}`
**Réponse :** `moveByEnd()`

```python
async def handle_move_by(cmd: Command) -> CommandResponse:
    dX = cmd.parameters.get("dX", 0.0)
    dY = cmd.parameters.get("dY", 0.0)
    dZ = cmd.parameters.get("dZ", 0.0)
    dPsi = cmd.parameters.get("dPsi", 0.0)
    
    if OLYMPE_AVAILABLE and drone:
        try:
            result = drone(moveBy(dX, dY, dZ, dPsi) >> moveByEnd(_timeout=30)).wait()
            if result.success():
                return ok(cmd.id, f"Mouvement relatif effectué: dX={dX}, dY={dY}, dZ={dZ}, dPsi={dPsi}")
        except Exception as e:
            return err(cmd.id, f"Erreur moveBy: {str(e)}")
    else:
        # Mock
        time.sleep(1)
        return ok(cmd.id, f"[MOCK] Mouvement relatif effectué")
```

### `moveTo` amélioré
**Action :** Navigation GPS avec orientation
**Olympe :** `moveTo(lat, lon, alt, orientation_mode, heading)`
**Paramètres :** `{lat: float, lon: float, alt: float, orientation_mode?: string, heading?: float}`

```python
# Améliorer handle_goto pour supporter orientation_mode
orientation_mode_map = {
    "NONE": olympe.enums.ardrone3.Piloting.MoveTo_Orientation_mode.NONE,
    "TO_TARGET": olympe.enums.ardrone3.Piloting.MoveTo_Orientation_mode.TO_TARGET,
    "HEADING_START": olympe.enums.ardrone3.Piloting.MoveTo_Orientation_mode.HEADING_START,
    "HEADING_DURING": olympe.enums.ardrone3.Piloting.MoveTo_Orientation_mode.HEADING_DURING,
}
```

---

## 📍 Point Of Interest (Priorité Moyenne)

### `startPilotedPOI`
**Action :** Démarrer un POI piloté
**Olympe :** `StartPilotedPOIV2(lat, lon, alt, mode)`
**Paramètres :** `{lat: float, lon: float, alt: float, mode: "locked_gimbal" | "locked_once_gimbal" | "free_gimbal"}`

```python
async def handle_start_piloted_poi(cmd: Command) -> CommandResponse:
    lat = cmd.parameters.get("lat")
    lon = cmd.parameters.get("lon")
    alt = cmd.parameters.get("alt")
    mode_str = cmd.parameters.get("mode", "locked_gimbal")
    
    mode_map = {
        "locked_gimbal": olympe.enums.ardrone3.Piloting.StartPilotedPOIV2_Mode.locked_gimbal,
        "locked_once_gimbal": olympe.enums.ardrone3.Piloting.StartPilotedPOIV2_Mode.locked_once_gimbal,
        "free_gimbal": olympe.enums.ardrone3.Piloting.StartPilotedPOIV2_Mode.free_gimbal,
    }
    mode = mode_map.get(mode_str)
    
    if OLYMPE_AVAILABLE and drone:
        try:
            result = drone(StartPilotedPOIV2(lat, lon, alt, mode) >> PilotedPOIV2(status="RUNNING", _timeout=10)).wait()
            if result.success():
                return ok(cmd.id, f"POI démarré sur ({lat}, {lon})")
        except Exception as e:
            return err(cmd.id, f"Erreur POI: {str(e)}")
    else:
        return ok(cmd.id, f"[MOCK] POI démarré")
```

### `stopPilotedPOI`
**Action :** Arrêter le POI
**Olympe :** `StopPilotedPOI()`

---

## 🎮 Pilotage Manuel (Priorité Moyenne)

### `pcmd`
**Action :** Commande de pilotage manuel
**Olympe :** `PCMD(flag, roll, pitch, yaw, gaz)`
**Paramètres :** `{flag: int, roll: int, pitch: int, yaw: int, gaz: int, duration_ms?: int}`

```python
async def handle_pcmd(cmd: Command) -> CommandResponse:
    flag = cmd.parameters.get("flag", 1)
    roll = cmd.parameters.get("roll", 0)
    pitch = cmd.parameters.get("pitch", 0)
    yaw = cmd.parameters.get("yaw", 0)
    gaz = cmd.parameters.get("gaz", 0)
    duration_ms = cmd.parameters.get("duration_ms", 1000)
    
    if OLYMPE_AVAILABLE and drone:
        try:
            # Envoyer PCMD toutes les 50ms pendant duration_ms
            start_time = time.time()
            while (time.time() - start_time) * 1000 < duration_ms:
                drone.set_piloting_pcmd(flag, roll, pitch, yaw, gaz)
                time.sleep(0.05)
            return ok(cmd.id, "Pilotage manuel effectué")
        except Exception as e:
            return err(cmd.id, f"Erreur PCMD: {str(e)}")
    else:
        return ok(cmd.id, "[MOCK] Pilotage manuel effectué")
```

---

## ⚙️ Configuration (Priorité Basse)

### `setMaxAltitude`
**Action :** Définir l'altitude maximale
**Olympe :** `MaxAltitude(current)`

### `setMaxDistance`
**Action :** Définir la distance maximale
**Olympe :** `MaxDistance(value)`

### `enableGeofence`
**Action :** Activer/désactiver le geofencing
**Olympe :** `NoFlyOverMaxDistance(shouldNotFlyOver)`

### `setMaxVerticalSpeed`
**Action :** Définir la vitesse verticale maximale
**Olympe :** `MaxVerticalSpeed(current)`

### `setMaxRotationSpeed`
**Action :** Définir la vitesse de rotation maximale
**Olympe :** `MaxRotationSpeed(current)`

### `setMaxTilt`
**Action :** Définir l'inclinaison maximale
**Olympe :** `MaxTilt(current)`

---

## 📊 Monitoring Amélioré (Priorité Moyenne)

### `getStatus` amélioré
**Action :** Récupérer tous les états du drone
**Olympe :** Écouter plusieurs événements

```python
async def handle_status(cmd: Command) -> CommandResponse:
    status_data = {
        "state": drone_state["state"],
        "battery": drone_state["battery"],
        "gps": drone_state["gps"],
    }
    
    if OLYMPE_AVAILABLE and drone:
        # Lire les états Olympe
        try:
            # FlyingStateChanged
            # GpsLocationChanged
            # SpeedChanged
            # AttitudeChanged
            # AltitudeChanged
            # WindStateChanged
            # VibrationLevelChanged
            # IcingLevelChanged
            # AlertStateChanged
            # ReturnHomeBatteryCapacity
            pass
        except Exception as e:
            logger.error(f"Erreur lecture états: {e}")
    
    return ok(cmd.id, "Statut récupéré", status_data)
```

---

## 🔄 Annulation (Priorité Basse)

### `cancelMoveBy`
**Action :** Annuler un mouvement relatif
**Olympe :** `CancelMoveBy()`

### `cancelMoveTo`
**Action :** Annuler une navigation GPS
**Olympe :** `CancelMoveTo()`

---

## 🚁 Décollage Avancé (Priorité Basse)

### `userTakeOff`
**Action :** Préparer un décollage utilisateur (thrown takeoff)
**Olympe :** `UserTakeOff(state=1)`

### `smartTakeOffLand`
**Action :** Décollage/Atterrissage intelligent
**Olympe :** `SmartTakeOffLand()`

---

## 📸 Capture Améliorée (Priorité Moyenne)

### `capture` amélioré
**Action :** Capture photo/vidéo avec contrôle réel
**Olympe :** MediaRecordState (start/stop)

```python
async def handle_capture(cmd: Command) -> CommandResponse:
    capture_type = cmd.parameters.get("type", "photo")
    duration_s = cmd.parameters.get("duration_s", 10)
    
    if OLYMPE_AVAILABLE and drone:
        try:
            if capture_type == "photo":
                # Utiliser MediaRecordState pour photo
                result = drone(MediaRecordState(video=0, photo=1)).wait()
            elif capture_type == "video":
                # Démarrer l'enregistrement
                result = drone(MediaRecordState(video=1, photo=0)).wait()
                if result.success():
                    time.sleep(duration_s)
                    # Arrêter l'enregistrement
                    result = drone(MediaRecordState(video=0, photo=0)).wait()
            
            if result.success():
                return ok(cmd.id, f"Capture {capture_type} effectuée")
        except Exception as e:
            return err(cmd.id, f"Erreur capture: {str(e)}")
    else:
        # Mock
        return ok(cmd.id, f"[MOCK] Capture {capture_type} effectuée")
```

---

## 🎯 Circle Amélioré (Priorité Moyenne)

### `circle` amélioré
**Action :** Orbite avec direction
**Olympe :** `Circle(direction)`

```python
async def handle_circle(cmd: Command) -> CommandResponse:
    target_lat = cmd.parameters.get("target_lat")
    target_lon = cmd.parameters.get("target_lon")
    alt_m = cmd.parameters.get("alt_m")
    radius_m = cmd.parameters.get("radius_m", 50)
    laps = cmd.parameters.get("laps", 1)
    direction = cmd.parameters.get("direction", "CW")  # CW, CCW, default
    
    if OLYMPE_AVAILABLE and drone:
        try:
            # Aller au centre de l'orbite
            result = drone(moveTo(target_lat, target_lon, alt_m) >> FlyingStateChanged(state="hovering", _timeout=30)).wait()
            
            # Configurer le rayon
            drone(CirclingRadius(value=radius_m)).wait()
            
            # Faire l'orbite
            direction_enum = {
                "CW": olympe.enums.ardrone3.Piloting.Circle_Direction.CW,
                "CCW": olympe.enums.ardrone3.Piloting.Circle_Direction.CCW,
                "default": olympe.enums.ardrone3.Piloting.Circle_Direction.default,
            }.get(direction)
            
            for _ in range(laps):
                result = drone(Circle(direction=direction_enum) >> FlyingStateChanged(state="hovering", _timeout=30)).wait()
            
            return ok(cmd.id, f"Orbite effectuée")
        except Exception as e:
            return err(cmd.id, f"Erreur orbite: {str(e)}")
```

---

## 📝 Template pour Ajouter une Nouvelle Commande

```python
async def handle_nouvelle_commande(cmd: Command) -> CommandResponse:
    """Gère la nouvelle commande"""
    param1 = cmd.parameters.get("param1")
    param2 = cmd.parameters.get("param2")
    
    logger.info(f"   🔧 Nouvelle commande:")
    logger.info(f"      Param1: {param1}")
    logger.info(f"      Param2: {param2}")
    
    if param1 is None:
        logger.error(f"   ❌ Paramètre manquant: param1")
        return err(cmd.id, "Paramètre manquant: param1 requis")
    
    if OLYMPE_AVAILABLE and drone:
        try:
            # Code Olympe réel
            result = drone(CommandeOlympe(param1, param2) >> EventAttendu(_timeout=10)).wait()
            if result.success():
                return ok(cmd.id, "Commande réussie", {"data": "..."})
            else:
                return err(cmd.id, "Échec de la commande")
        except Exception as e:
            return err(cmd.id, f"Erreur: {str(e)}")
    else:
        # Mode mock
        logger.info(f"   [MOCK] Simulation de la commande...")
        time.sleep(1)
        logger.info(f"   [MOCK] ✓ Commande simulée")
        return ok(cmd.id, "[MOCK] Commande réussie", {"data": "..."})
```

Puis ajouter dans `cmd()` :
```python
elif action == "nouvelle_commande":
    return await handle_nouvelle_commande(command)
```

---

## 🎯 Ordre d'Implémentation Recommandé

### Phase 1 (MVP - Déjà fait)
- ✅ takeoff, goto, land, rth, capture, status

### Phase 2 (Fonctionnalités essentielles)
1. `emergency` - Arrêt d'urgence
2. `moveBy` - Mouvement relatif
3. `circle` amélioré - Orbite réelle
4. `capture` amélioré - Vidéo réelle

### Phase 3 (Fonctionnalités avancées)
5. `startPilotedPOI` / `stopPilotedPOI` - POI
6. `pcmd` - Pilotage manuel
7. `getStatus` amélioré - Monitoring complet
8. `cancelMoveBy` / `cancelMoveTo` - Annulation

### Phase 4 (Configuration)
9. `setMaxAltitude` / `setMaxDistance` - Limites
10. `enableGeofence` - Geofencing
11. `setMaxVerticalSpeed` / `setMaxRotationSpeed` - Vitesses

---

**Total : 20+ commandes à implémenter** 🚀

