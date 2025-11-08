# 🧪 Scénarios de Test - EDTH Drone Control

Ce document liste tous les scénarios de test possibles pour valider le système, même si certaines fonctions ne sont pas encore implémentées.

---

## 📋 Scénarios de Base (Déjà implémentés)

### ✅ 1. Mission de reconnaissance simple
**Commande utilisateur :** "Va voir si la centrale de Fessenheim a été touchée"

**Outils utilisés :**
- `getCoordonnees` → Coordonnées de la centrale
- `getEtatInitial` → Paramètres par défaut
- `getZoneInterdite` → Zones à éviter

**Plan de vol généré :**
1. `takeOff` (50m)
2. `goTo` (vers la centrale)
3. `circle` (orbite autour)
4. `capture` (photo)
5. `rth` (retour à la base)
6. `land` (atterrissage)

**Status :** ✅ Implémenté et testé

---

### ✅ 2. Décollage simple
**Commande utilisateur :** "Décolle à 30 mètres"

**Plan de vol :**
1. `takeOff` (30m)

**Status :** ✅ Implémenté

---

### ✅ 3. Navigation vers un point
**Commande utilisateur :** "Va aux coordonnées 48.8566, 2.3522 à 100 mètres d'altitude"

**Plan de vol :**
1. `takeOff` (100m)
2. `goTo` (48.8566, 2.3522, 100m)
3. `land`

**Status :** ✅ Implémenté

---

### ✅ 4. Capture photo
**Commande utilisateur :** "Prends une photo"

**Plan de vol :**
1. `capture` (type: photo)

**Status :** ✅ Implémenté

---

## 🚀 Scénarios Avancés (À implémenter)

### 🔄 5. Mission avec waypoints multiples
**Commande utilisateur :** "Inspecte les 3 centrales : Fessenheim, Cattenom et Gravelines"

**Outils nécessaires :**
- `getCoordonnees` (x3)
- `planMissionRecon` (avec waypoints multiples)

**Plan de vol attendu :**
1. `takeOff`
2. `goTo` (Fessenheim)
3. `circle` + `capture`
4. `goTo` (Cattenom)
5. `circle` + `capture`
6. `goTo` (Gravelines)
7. `circle` + `capture`
8. `rth`
9. `land`

**Fonctions Olympe :** `moveTo` avec plusieurs destinations

---

### 🎥 6. Capture vidéo avec durée
**Commande utilisateur :** "Enregistre une vidéo de 30 secondes de la centrale"

**Plan de vol :**
1. `takeOff`
2. `goTo` (centrale)
3. `capture` (type: video, duration_s: 30)
4. `rth`
5. `land`

**Fonctions Olympe :** MediaRecordState (démarrer/arrêter)

---

### ⭕ 7. Orbite avec paramètres personnalisés
**Commande utilisateur :** "Fais 3 tours autour de la centrale avec un rayon de 200 mètres à 80 mètres d'altitude"

**Plan de vol :**
1. `takeOff` (80m)
2. `goTo` (centrale)
3. `circle` (radius_m: 200, laps: 3, alt_m: 80)
4. `capture`
5. `rth`
6. `land`

**Fonctions Olympe :** `Circle` avec direction (CW/CCW)

---

### 🏠 8. Retour à la base automatique
**Commande utilisateur :** "Retourne à la base maintenant"

**Plan de vol :**
1. `rth`

**Fonctions Olympe :** `NavigateHome(start=1)`

**Status :** ⚠️ Partiellement implémenté (utilise moveTo vers home)

---

### 🛑 9. Atterrissage d'urgence
**Commande utilisateur :** "Atterris immédiatement"

**Plan de vol :**
1. `land`

**Fonctions Olympe :** `Landing()`

**Status :** ✅ Implémenté

---

### 🚨 10. Arrêt d'urgence
**Commande utilisateur :** "ARRÊT D'URGENCE"

**Plan de vol :**
1. `emergency` (coupe les moteurs)

**Fonctions Olympe :** `Emergency()`

**Status :** ❌ Non implémenté

---

## 🎯 Scénarios de Point Of Interest (POI)

### 📍 11. POI avec gimbal verrouillé
**Commande utilisateur :** "Regarde la centrale de Fessenheim pendant que je pilote"

**Plan de vol :**
1. `takeOff`
2. `goTo` (centrale)
3. `startPilotedPOI` (latitude, longitude, altitude, mode: locked_gimbal)
4. (utilisateur peut piloter normalement, gimbal reste pointé)
5. `stopPilotedPOI`
6. `rth`
7. `land`

**Fonctions Olympe :** `StartPilotedPOIV2(mode=locked_gimbal)`, `StopPilotedPOI()`

**Status :** ❌ Non implémenté

---

### 📍 12. POI avec gimbal libre après verrouillage initial
**Commande utilisateur :** "Regarde la centrale puis laisse-moi contrôler la caméra"

**Plan de vol :**
1. `startPilotedPOI` (mode: locked_once_gimbal)
2. (gimbal verrouillé puis libre)

**Fonctions Olympe :** `StartPilotedPOIV2(mode=locked_once_gimbal)`

**Status :** ❌ Non implémenté

---

## 🎮 Scénarios de Pilotage Manuel

### 🕹️ 13. Mouvement relatif (moveBy)
**Commande utilisateur :** "Avance de 10 mètres, puis va à droite de 5 mètres"

**Plan de vol :**
1. `takeOff`
2. `moveBy` (dX: 10, dY: 0, dZ: 0)
3. `moveBy` (dX: 0, dY: 5, dZ: 0)
4. `land`

**Fonctions Olympe :** `moveBy(dX, dY, dZ, dPsi)`

**Status :** ❌ Non implémenté (actuellement utilise moveTo)

---

### 🕹️ 14. Mouvement relatif avec rotation
**Commande utilisateur :** "Avance de 20 mètres en tournant de 45 degrés"

**Plan de vol :**
1. `moveBy` (dX: 20, dY: 0, dZ: 0, dPsi: 45°)

**Fonctions Olympe :** `moveBy` avec dPsi

**Status :** ❌ Non implémenté

---

### 🕹️ 15. Pilotage manuel (PCMD)
**Commande utilisateur :** "Pilote manuellement : roule à droite, tangue vers l'avant"

**Plan de vol :**
1. `takeOff`
2. `PCMD` (roll: +50, pitch: +30, yaw: 0, gaz: 0)
3. (maintenir pendant X secondes)
4. `land`

**Fonctions Olympe :** `PCMD(flag, roll, pitch, yaw, gaz)`

**Status :** ❌ Non implémenté

---

## ⚙️ Scénarios de Configuration

### 🔧 16. Configuration de l'altitude maximale
**Commande utilisateur :** "Limite l'altitude maximale à 120 mètres"

**Plan de vol :**
1. `setMaxAltitude` (120m)

**Fonctions Olympe :** `MaxAltitude(current=120)`

**Status :** ❌ Non implémenté

---

### 🔧 17. Configuration de la distance maximale
**Commande utilisateur :** "Ne va pas plus loin que 500 mètres de la base"

**Plan de vol :**
1. `setMaxDistance` (500m)
2. `enableGeofence` (true)

**Fonctions Olympe :** `MaxDistance(value=500)`, `NoFlyOverMaxDistance(shouldNotFlyOver=1)`

**Status :** ❌ Non implémenté

---

### 🔧 18. Configuration de la vitesse
**Commande utilisateur :** "Limite la vitesse verticale à 2 m/s"

**Plan de vol :**
1. `setMaxVerticalSpeed` (2 m/s)

**Fonctions Olympe :** `MaxVerticalSpeed(current=2)`

**Status :** ❌ Non implémenté

---

### 🔧 19. Mode extérieur/intérieur
**Commande utilisateur :** "Active le mode extérieur"

**Plan de vol :**
1. `setOutdoorMode` (true)

**Fonctions Olympe :** `Outdoor(outdoor=1)`

**Status :** ❌ Non implémenté

---

## 📊 Scénarios de Monitoring

### 📈 20. Vérification du statut complet
**Commande utilisateur :** "Donne-moi le statut complet du drone"

**Plan de vol :**
1. `getStatus` (retourne : état, batterie, GPS, vitesse, attitude, etc.)

**Fonctions Olympe :** 
- `FlyingStateChanged`
- `GpsLocationChanged`
- `SpeedChanged`
- `AttitudeChanged`
- `AltitudeChanged`
- `BatteryStateChanged` (si disponible)

**Status :** ⚠️ Partiellement implémenté (seulement état, batterie, GPS)

---

### 📈 21. Monitoring en temps réel
**Commande utilisateur :** "Affiche la position GPS en temps réel pendant le vol"

**Plan de vol :**
1. `takeOff`
2. `goTo` (destination)
3. (streaming de `GpsLocationChanged` toutes les X secondes)
4. `land`

**Fonctions Olympe :** Écoute continue de `GpsLocationChanged`

**Status :** ❌ Non implémenté

---

### 📈 22. Vérification de la batterie avant mission
**Commande utilisateur :** "As-tu assez de batterie pour aller à Fessenheim et revenir ?"

**Plan de vol :**
1. `getStatus` (batterie actuelle)
2. `getCoordonnees` (Fessenheim)
3. Calcul de la distance
4. Vérification `ReturnHomeBatteryCapacity`
5. Réponse : "Oui" ou "Non, batterie insuffisante"

**Fonctions Olympe :** `ReturnHomeBatteryCapacity`

**Status :** ❌ Non implémenté

---

## 🌪️ Scénarios de Conditions Météo

### 💨 23. Détection du vent
**Commande utilisateur :** "Quel est l'état du vent ?"

**Plan de vol :**
1. `getWindState` (retourne : ok, warning, critical)

**Fonctions Olympe :** `WindStateChanged`

**Status :** ❌ Non implémenté

---

### ❄️ 24. Détection du givrage
**Commande utilisateur :** "Y a-t-il du givre sur les hélices ?"

**Plan de vol :**
1. `getIcingLevel` (retourne : ok, warning, critical)

**Fonctions Olympe :** `IcingLevelChanged`

**Status :** ❌ Non implémenté

---

### 📳 25. Détection des vibrations
**Commande utilisateur :** "Les vibrations sont-elles normales ?"

**Plan de vol :**
1. `getVibrationLevel` (retourne : ok, warning, critical)

**Fonctions Olympe :** `VibrationLevelChanged`

**Status :** ❌ Non implémenté

---

## 🚨 Scénarios d'Urgence et Sécurité

### ⚠️ 26. Alerte batterie faible
**Commande utilisateur :** "Quel est le niveau d'alerte de la batterie ?"

**Plan de vol :**
1. `getAlertState` (retourne : none, low_battery, critical_battery, etc.)

**Fonctions Olympe :** `AlertStateChanged`

**Status :** ❌ Non implémenté

---

### ⚠️ 27. Atterrissage forcé automatique
**Commande utilisateur :** "Y a-t-il un atterrissage forcé prévu ?"

**Plan de vol :**
1. `getForcedLandingInfo` (retourne : raison, délai)

**Fonctions Olympe :** `ForcedLandingAutoTrigger`

**Status :** ❌ Non implémenté

---

### ⚠️ 28. Avertissement de vol stationnaire
**Commande utilisateur :** "Peux-tu maintenir le vol stationnaire ici ?"

**Plan de vol :**
1. `getHoveringWarning` (retourne : problèmes GPS, lumière, altitude)

**Fonctions Olympe :** `HoveringWarning`

**Status :** ❌ Non implémenté

---

## 🎯 Scénarios de Navigation Avancée

### 🧭 29. Navigation avec orientation vers la cible
**Commande utilisateur :** "Va à la centrale en te dirigeant vers elle"

**Plan de vol :**
1. `takeOff`
2. `goTo` (centrale, orientation_mode: TO_TARGET)
3. `land`

**Fonctions Olympe :** `moveTo` avec `orientation_mode=TO_TARGET`

**Status :** ⚠️ Partiellement implémenté (moveTo sans orientation_mode)

---

### 🧭 30. Navigation avec cap fixe
**Commande utilisateur :** "Va à la centrale en gardant un cap de 45 degrés"

**Plan de vol :**
1. `goTo` (centrale, orientation_mode: HEADING_DURING, heading: 45)

**Fonctions Olympe :** `moveTo` avec `orientation_mode=HEADING_DURING`

**Status :** ❌ Non implémenté

---

### 🧭 31. Navigation avec orientation avant départ
**Commande utilisateur :** "Oriente-toi vers le nord puis va à la centrale"

**Plan de vol :**
1. `goTo` (centrale, orientation_mode: HEADING_START, heading: 0)

**Fonctions Olympe :** `moveTo` avec `orientation_mode=HEADING_START`

**Status :** ❌ Non implémenté

---

## 🔄 Scénarios d'Annulation

### ❌ 32. Annulation de mouvement relatif
**Commande utilisateur :** "Annule le mouvement en cours"

**Plan de vol :**
1. `cancelMoveBy`

**Fonctions Olympe :** `CancelMoveBy()`

**Status :** ❌ Non implémenté

---

### ❌ 33. Annulation de navigation GPS
**Commande utilisateur :** "Arrête d'aller à la destination"

**Plan de vol :**
1. `cancelMoveTo`

**Fonctions Olympe :** `CancelMoveTo()`

**Status :** ❌ Non implémenté

---

## 🎬 Scénarios de Décollage Avancé

### 🚁 34. Décollage utilisateur (thrown takeoff)
**Commande utilisateur :** "Prépare-toi pour un décollage lancé"

**Plan de vol :**
1. `userTakeOff` (state: 1)
2. (attendre `UserTakeoffReady`)
3. (utilisateur lance le drone)
4. (décollage automatique)

**Fonctions Olympe :** `UserTakeOff(state=1)`, `UserTakeoffReady`

**Status :** ❌ Non implémenté

---

### 🚁 35. Décollage/Atterrissage intelligent
**Commande utilisateur :** "Décolle ou atterris selon ton état actuel"

**Plan de vol :**
1. `smartTakeOffLand` (décolle si au sol, atterrit si en vol)

**Fonctions Olympe :** `SmartTakeOffLand()`

**Status :** ❌ Non implémenté

---

## 📸 Scénarios de Capture Avancée

### 🎥 36. Capture vidéo longue durée
**Commande utilisateur :** "Enregistre 2 minutes de vidéo pendant que tu fais une orbite"

**Plan de vol :**
1. `takeOff`
2. `goTo` (cible)
3. `capture` (type: video, duration_s: 120) - démarre
4. `circle` (pendant l'enregistrement)
5. `capture` (stop) - arrête
6. `rth`
7. `land`

**Fonctions Olympe :** MediaRecordState (start/stop)

**Status :** ⚠️ Partiellement implémenté (capture vidéo sans durée réelle)

---

### 📷 37. Séquence de photos multiples
**Commande utilisateur :** "Prends 5 photos à intervalles de 10 secondes"

**Plan de vol :**
1. `takeOff`
2. `goTo` (cible)
3. `capture` (photo) - photo 1
4. (attendre 10s)
5. `capture` (photo) - photo 2
6. (attendre 10s)
7. ... (répéter 5 fois)
8. `rth`
9. `land`

**Status :** ⚠️ Possible avec boucle, pas encore implémenté

---

## 🗺️ Scénarios de Mission Complexe

### 🎯 38. Mission de patrouille
**Commande utilisateur :** "Patrouille autour du périmètre de la centrale avec 4 points de passage"

**Plan de vol :**
1. `takeOff`
2. `goTo` (point 1)
3. `capture`
4. `goTo` (point 2)
5. `capture`
6. `goTo` (point 3)
7. `capture`
8. `goTo` (point 4)
9. `capture`
10. `rth`
11. `land`

**Status :** ⚠️ Possible avec planMissionRecon amélioré

---

### 🎯 39. Mission de reconnaissance avec grille
**Commande utilisateur :** "Scanne la zone en grille de 3x3"

**Plan de vol :**
1. `takeOff`
2. (générer 9 waypoints en grille)
3. Pour chaque waypoint :
   - `goTo` (waypoint)
   - `capture` (photo)
4. `rth`
5. `land`

**Status :** ❌ Non implémenté (nécessite planMissionRecon avec pattern "grid")

---

### 🎯 40. Mission avec évitement de zones
**Commande utilisateur :** "Va à la centrale en évitant la zone interdite au nord"

**Plan de vol :**
1. `getZoneInterdite` (récupère les zones)
2. `planMissionRecon` (avec évitement)
3. `takeOff`
4. `goTo` (en contournant les zones)
5. `circle` + `capture`
6. `rth`
7. `land`

**Status :** ⚠️ Partiellement implémenté (getZoneInterdite existe mais pas l'évitement)

---

## 🔍 Scénarios de Diagnostic

### 🔬 41. Vérification du GPS
**Commande utilisateur :** "As-tu un fix GPS ?"

**Plan de vol :**
1. `getGpsStatus` (retourne : fix, pas de fix, précision)

**Fonctions Olympe :** `GpsLocationChanged` (latitude/longitude = 500.0 si pas de fix)

**Status :** ⚠️ Partiellement implémenté (dans getStatus)

---

### 🔬 42. Vérification du magnétomètre
**Commande utilisateur :** "Le magnétomètre fonctionne-t-il correctement ?"

**Plan de vol :**
1. `getHeadingLockedState` (retourne : ok, warning, critical)

**Fonctions Olympe :** `HeadingLockedStateChanged`

**Status :** ❌ Non implémenté

---

### 🔬 43. Vérification de l'altitude au sol
**Commande utilisateur :** "Quelle est ton altitude par rapport au sol ?"

**Plan de vol :**
1. `getAltitudeAboveGround` (retourne l'altitude au-dessus du sol)

**Fonctions Olympe :** `AltitudeAboveGroundChanged`

**Status :** ❌ Non implémenté

---

## 🎛️ Scénarios de Configuration Avancée

### ⚙️ 44. Configuration du mode banked turn
**Commande utilisateur :** "Active le mode virage incliné"

**Plan de vol :**
1. `setBankedTurn` (true)

**Fonctions Olympe :** `BankedTurn(value=1)`

**Status :** ❌ Non implémenté

---

### ⚙️ 45. Configuration de l'inclinaison maximale
**Commande utilisateur :** "Limite l'inclinaison à 30 degrés"

**Plan de vol :**
1. `setMaxTilt` (30)

**Fonctions Olympe :** `MaxTilt(current=30)`

**Status :** ❌ Non implémenté

---

### ⚙️ 46. Configuration de la vitesse de rotation
**Commande utilisateur :** "Limite la vitesse de rotation à 50 degrés par seconde"

**Plan de vol :**
1. `setMaxRotationSpeed` (50)

**Fonctions Olympe :** `MaxRotationSpeed(current=50)`

**Status :** ❌ Non implémenté

---

## 🎪 Scénarios de Démonstration

### 🎬 47. Démo complète "Inspection de centrale"
**Commande utilisateur :** "Fais une inspection complète de la centrale de Fessenheim : décolle, va-y, fais une orbite, prends des photos et des vidéos, puis reviens"

**Plan de vol :**
1. `takeOff` (50m)
2. `goTo` (Fessenheim, 50m)
3. `circle` (radius: 100m, laps: 2)
4. `capture` (photo)
5. `capture` (video, 30s)
6. `circle` (radius: 50m, laps: 1)
7. `capture` (photo)
8. `rth`
9. `land`
10. `getStatus` (rapport final)

**Status :** ✅ Possible avec les fonctions actuelles

---

### 🎬 48. Démo "Mission multi-sites"
**Commande utilisateur :** "Inspecte les 3 centrales principales : Fessenheim, Cattenom et Gravelines"

**Plan de vol :**
1. `takeOff`
2. Pour chaque centrale :
   - `goTo` (centrale)
   - `circle` + `capture`
3. `rth`
4. `land`

**Status :** ⚠️ Possible mais nécessite amélioration de planMissionRecon

---

### 🎬 49. Démo "Urgence"
**Commande utilisateur :** "Batterie faible détectée, retourne immédiatement à la base et atterris"

**Plan de vol :**
1. `getStatus` (détecte batterie faible)
2. `rth` (immédiat)
3. `land` (dès retour)

**Status :** ⚠️ Possible avec amélioration de getStatus

---

### 🎬 50. Démo "POI avec pilotage"
**Commande utilisateur :** "Regarde la centrale pendant que je te pilote manuellement"

**Plan de vol :**
1. `takeOff`
2. `goTo` (près de la centrale)
3. `startPilotedPOI` (centrale, mode: locked_gimbal)
4. (utilisateur peut piloter avec PCMD)
5. `stopPilotedPOI`
6. `land`

**Status :** ❌ Nécessite POI et PCMD

---

## 📝 Guide d'Utilisation

### Pour tester un scénario :

1. **Scénarios ✅ (Implémentés)** : Testez directement dans le chatbot
2. **Scénarios ⚠️ (Partiellement)** : Testez mais certaines fonctions peuvent ne pas fonctionner
3. **Scénarios ❌ (Non implémentés)** : Le chatbot peut générer un plan mais le serveur Python retournera une erreur

### Ordre recommandé de test :

1. **Phase 1** : Tester tous les scénarios ✅
2. **Phase 2** : Implémenter et tester les scénarios ⚠️
3. **Phase 3** : Implémenter les scénarios ❌ prioritaires
4. **Phase 4** : Tester tous les scénarios au hackathon avec Olympe réel

---

## 🎯 Scénarios Prioritaires pour le Hackathon

### Must Have (MVP)
1. ✅ Mission de reconnaissance simple (#1)
2. ✅ Décollage/Atterrissage (#2, #9)
3. ✅ Navigation GPS (#3)
4. ✅ Capture photo (#4)
5. ✅ Retour à la base (#8)

### Should Have
6. ⚠️ Capture vidéo (#6)
7. ⚠️ Orbite personnalisée (#7)
8. ⚠️ Statut complet (#20)
9. ❌ Arrêt d'urgence (#10)
10. ❌ POI basique (#11)

### Nice to Have
11. ❌ Mouvement relatif (#13)
12. ❌ Configuration altitude max (#16)
13. ❌ Monitoring temps réel (#21)
14. ❌ Mission multi-sites (#48)

---

**Total : 50 scénarios de test** 🎉

