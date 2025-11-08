# Archive

Ce dossier contient du code legacy qui n'est plus utilisé dans l'architecture actuelle, mais conservé pour référence historique.

## Contenu

### `apps/cli/`
Scripts CLI d'origine pour tester Olympe directement :
- `poi_inspection.py` : Inspection complète de POI (référence pour l'implémentation actuelle)
- `goto_poi.py` : Navigation vers un POI
- `olympe_sim_smoke.py` : Tests de fumée avec simulateur
- `olympe_simple_smoke.py` : Tests de base Olympe

**Note** : `poi_inspection.py` reste une référence utile pour comprendre les API Olympe (RTH, landing, POI inspection, etc.).

### `core/world_map/`
Utilitaires de conversion de coordonnées :
- `coordinate_converter.py` : Conversion GPS ↔ coordonnées locales
- `coordinate_example.py` : Exemples d'utilisation
- `example_usage.py` : Démos
- `add_to_map.py` : Ajout de POI

## Pourquoi archivé ?

L'architecture actuelle utilise :
- **FastAPI WebSocket Server** au lieu de scripts CLI individuels
- **Mission DSL + Executor** qui gère les conversions de coordonnées en interne
- **NLP Processor (Mistral AI)** pour la génération de missions

Ces fichiers étaient utiles pour le prototypage initial mais ne sont plus nécessaires pour le système de production.

## Récupération

Si vous avez besoin de restaurer ces fichiers :

```bash
# Exemple : restaurer coordinate_converter.py
cp archive/core/world_map/coordinate_converter.py core/world_map/
```

Ou consultez l'historique Git pour retrouver les versions d'origine.

---

**Date d'archivage** : 2025-11-08  
**Raison** : Simplification de l'architecture et élimination du code legacy

