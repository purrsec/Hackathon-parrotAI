# Cahier des charges - Hackathon Parrot-2
## Interface conversationnelle pour missions autonomes de drones

---

## 1. CONTEXTE DU PROJET

### 1.1 Objectif du hackathon
Créer une interface conversationnelle permettant de contrôler un drone Parrot ANAFI via langage naturel, pour exécuter des missions autonomes sans écrire de code.

### 1.2 Cas d'usage ciblés
- **Inspection de zones** : "Inspecte cette zone en mode photogrammétrie"
- **Tracking d'objets** : "Suis cet objet en mouvement"
- **Patrouilles automatiques** : "Survole le périmètre nord"
- **Évitement d'obstacles** : Gestion automatique via CV embarquée

### 1.3 Contraintes techniques identifiées
- ✅ SDK Parrot mature (Olympe, Ground SDK, Air SDK)
- ✅ CV embarquée disponible (tracking, obstacle avoidance)
- ⚠️ **Contrainte majeure** : Développement en aveugle
  - Simulateur Sphinx uniquement disponible sur le PC du hackathon
  - Nécessité de coder et tester localement sans accès au simulateur
  - Intégration finale à faire sur place

---

## 2. ARCHITECTURE TECHNIQUE

### 2.1 Principe de découplage
```
[Chatbot Interface] ←→ [API Standard JSON] ←→ [Drone Controller]
     (Dev chez toi)                              (Test au hackathon)
```

**Avantage** : Développement et tests parallèles sans dépendance au simulateur.

### 2.2 Stack technologique

#### Frontend = cahatbot avec tool + acces IA (openAI ou Claude)
- React + TailwindCSS

#### Backend / Contrôleur drone
- **Python** : Langage du SDK Olympe
- **Olympe SDK** : Contrôle du drone ANAFI
- **FastAPI/Flask** : Serveur API pour recevoir les commandes

#### Environnement de test local
- **Mock Drone** : Simulateur léger en Python reproduisant les réponses Olympe
- Permet de tester toute la logique NLP → Commandes sans le vrai simulateur

---

## 3. SPÉCIFICATIONS FONCTIONNELLES

### 3.1 Flux utilisateur
1. **Utilisateur** tape une commande en français : 
   - "Décolle et survole la zone nord"
   - "Suis cette personne"
   - "Inspecte ce bâtiment en prenant des photos"

2. **IA (Claude ou OpenAI)** parse et structure la commande :
   ```json
   {
     "intent": "patrol",
     "action": "takeoff_and_move",
     "parameters": {
       "zone": "north",
       "altitude": 10,
       "speed": 2
     }
   }
   ```

3. **Backend** traduit en appels Olympe SDK :
   ```python
   drone.takeoff()
   drone.move_to(lat, lon, altitude)
   ```

4. **Retour visuel** : Statut en temps réel dans l'interface
   - Position GPS
   - Altitude
   - Batterie
   - État de la mission
   - Stream vidéo

### 3.2 Commandes prioritaires (MVP) A vérifier si c'est les vraies commandes Olympe

| Commande utilisateur | Intent | API Olympe | Complexité |
|---------------------|--------|------------|-----------|
| "Décolle" | `takeoff` | `drone.takeoff()` | ⭐ Facile |
| "Atterris" | `land` | `drone.land()` | ⭐ Facile |
| "Va au point X,Y" | `move_to` | `drone.move_to(lat, lon, alt)` | ⭐⭐ Moyen |
| "Suis cet objet" | `track_object` | Mode Cameraman SDK | ⭐⭐⭐ Difficile |
| "Inspecte cette zone" | `inspect_area` | Flight Plan photogrammetry | ⭐⭐⭐ Difficile |
| "Retourne à la base" | `return_home` | `drone.return_to_home()` | ⭐ Facile |

### 3.3 Gestion des erreurs
- **Commande ambiguë** : L'IA demande des précisions
  - User : "Va là-bas"
  - Bot : "Peux-tu préciser les coordonnées ou une direction (nord/sud) ?"
  
- **Erreur drone** : Affichage explicite
  - Batterie faible (<20%)
  - GPS perdu
  - Obstacle détecté

---

## 4. PROTOCOLE DE COMMUNICATION

### 4.1 Format JSON standardisé

#### Commande → Drone
```json
{
  "id": "cmd_001",
  "timestamp": "2025-11-07T14:30:00Z",
  "action": "takeoff",
  "parameters": {
    "altitude": 10
  }
}
```

#### Réponse Drone → Interface
```json
{
  "id": "cmd_001",
  "status": "success|in_progress|error",
  "data": {
    "altitude": 10.2,
    "battery": 85,
    "gps": {"lat": 48.8566, "lon": 2.3522}
  },
  "message": "Décollage réussi"
}
```

### 4.2 Actions supportées (API Contract)

```typescript
interface DroneAction {
  // Mouvements de base
  takeoff: {}
  land: {}
  move_to: { lat: number, lon: number, altitude: number }
  move_relative: { forward: number, right: number, up: number }
  
  // Missions avancées
  start_tracking: { target_type: "person" | "vehicle" | "object" }
  start_inspection: { area: Polygon, pattern: "grid" | "orbit" }
  start_patrol: { waypoints: [lat, lon][] }
  
  // Contrôle
  pause: {}
  resume: {}
  return_home: {}
  emergency_stop: {}
}
```

---

## 5. PLAN DE DÉVELOPPEMENT

### 5.1 Chez toi (Avant le hackathon)

#### Jour 1 : Setup + Mock
- [ ] Créer l'architecture de projet
- [ ] Développer le **Mock Drone** Python
  - Simule les réponses Olympe
  - Logs détaillés pour debug
- [ ] Créer l'interface React basique
- [ ] Intégrer l'API Claude pour parsing NLP

#### Jour 2 : Logique métier
- [ ] Implémenter le mapping Intent → Actions
- [ ] Tester les scénarios principaux avec le mock
- [ ] Gérer les cas d'erreur
- [ ] Ajouter le feedback temps réel

#### Jour 3 : Polish
- [ ] Documentation du code
- [ ] Préparer le template Olympe (structure prête à remplir)
- [ ] Tests de charge (latence IA, commandes rapides)

### 5.2 Au hackathon (Jour J)

#### Phase 1 : Intégration (2h)
1. Cloner le projet sur leur PC
2. Installer Olympe + Sphinx
3. Remplacer `mock_drone.py` par `olympe_drone.py`
4. Tester `takeoff()` / `land()` sur le simulateur

#### Phase 2 : Validation (2h)
5. Tester chaque commande du MVP
6. Ajuster les paramètres (vitesse, altitude) selon le simulateur
7. Debugging des edge cases

#### Phase 3 : Démo (1h)
8. Préparer le scénario de démo
9. Vidéo de backup au cas où

---

## 6. RISQUES ET MITIGATION

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|-----------|
| Mock trop différent d'Olympe | ⚠️ Moyen | Moyen | Consulter la doc Olympe pour alignement |
| Latence API Claude | ⚠️ Faible | Faible | Cache des commandes fréquentes |
| Simulateur bugué au hackathon | 🔴 Élevé | Faible | Vidéo de démo avec mock en backup |
| Parsing NLP imprécis | ⚠️ Moyen | Moyen | Fallback sur commandes structurées |
| Pas assez de temps d'intégration | 🔴 Élevé | Moyen | **Architecture découplée = priorité #1** |

---

## 7. CRITÈRES DE SUCCÈS

### MVP (Minimum Viable Product)
✅ Chatbot comprend 5 commandes de base  
✅ Drone décolle/atterrit via commande vocale  
✅ Affichage du statut en temps réel  
✅ Gestion d'1 cas d'erreur (ex: batterie faible)

### Version idéale (si temps)
✅ Tracking d'objet fonctionnel  
✅ Inspection de zone (photogrammétrie)  
✅ Stream vidéo dans l'interface  
✅ Historique des commandes avec replay

---

## 8. LIVRABLES ATTENDUS

### Code
- Repository GitHub avec :
  - `/chatbot-interface` (React)
  - `/drone-controller` (Python Mock + Template Olympe)
  - `/docs` (Ce cahier des charges + API doc)
  - `README.md` avec procédure d'installation

### Documentation
- Guide d'intégration Olympe (5 min setup)
- Vidéo démo du mock (fallback)
- Présentation pitch (3 slides max)

### Au hackathon
- Démo live de 5 min
- Code fonctionnel sur leur simulateur

---

## 9. QUESTIONS EN SUSPENS

- [ ] Quelle infrastructure OVHcloud utiliser pour héberger l'API ? (Voir roadmap fournie)
- [ ] Besoin de compute GPU pour le parsing NLP ou CPU suffit ?
- [ ] Stream vidéo nécessaire dans le MVP ou nice-to-have ?
- [ ] Accès WiFi/réseau au hackathon pour les appels API Claude ?

---

## 10. NEXT STEPS IMMÉDIATS

1. **Valider ce cahier des charges**
2. **Choisir la stack** : 
   - React + FastAPI ?
   - Autre combo ?
3. **Je te code le starter kit** :
   - Mock Drone Python
   - Interface React + Claude API
   - Template Olympe
4. **Tu testes en local** avec le mock
5. **Intégration finale** au hackathon

---

**Prêt à démarrer ?** Dis-moi si tu valides cette approche ou si tu veux ajuster des points ! 🚀