# EDTH - Chatbot Drone Control

Interface conversationnelle pour contrôler un drone Parrot ANAFI via langage naturel, utilisant Azure OpenAI ou MistralAI et Next.js.

## 🚀 Fonctionnalités

- Chatbot conversationnel avec Azure OpenAI (par défaut) ou MistralAI
- Contrôle du drone via outils (tools) avec validation Zod
- Interface React moderne et responsive
- Backend FastAPI Python avec support Olympe SDK
- Mode mock pour développement local
- Switch facile entre Azure OpenAI et MistralAI

## 📋 Prérequis

- Node.js 18+ et npm/yarn
- Python 3.9+
- Clé API Azure OpenAI OU MistralAI
- (Optionnel) Olympe SDK pour contrôle réel du drone

## 🛠️ Installation

### Frontend (Next.js)

```bash
# Installer les dépendances
npm install

# Créer le fichier .env.local
cp .env.example .env.local
# Éditer .env.local et ajouter vos clés API :
# - USE_AZURE_OPENAI=true (par défaut) ou false pour MistralAI
# - AZURE_OPENAI_ENDPOINT et AZURE_OPENAI_API_KEY (si Azure OpenAI)
# - MISTRAL_API_KEY (si MistralAI)

# Lancer le serveur de développement
npm run dev
```

Le frontend sera accessible sur http://localhost:3000

### Backend (FastAPI)

```bash
cd ../serverPython

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python main.py
```

Le backend sera accessible sur http://localhost:8000

## 🎯 Utilisation

1. **Lancez le backend FastAPI** (dans un terminal) :
   ```bash
   cd ../serverPython
   source venv/bin/activate
   python main.py
   ```

2. **Lancez le frontend Next.js** (dans un autre terminal) :
   ```bash
   cd Chatbot
   npm run dev
   ```

3. Ouvrez http://localhost:3000 dans votre navigateur
4. Commencez à chatter avec le bot !

### Exemples de commandes

- "Va voir si la centrale de Fessenheim a été touchée"
- "Décolle à 50 mètres d'altitude"
- "Prends une photo"
- "Retourne à la base"
- "Atterris"

## 🏗️ Architecture

```
[Next.js Frontend] ←→ [Azure OpenAI / MistralAI] ←→ [Tools Executor] ←→ [FastAPI Backend] ←→ [Olympe SDK] ←→ [Drone]
```

## ⚙️ Configuration AI Provider

Le système supporte deux providers AI :

### Azure OpenAI (par défaut)

```env
USE_AZURE_OPENAI=true
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/openai/deployments/your-deployment/chat/completions?api-version=2025-01-01-preview
AZURE_OPENAI_API_KEY=your-api-key
```

### MistralAI

```env
USE_AZURE_OPENAI=false
MISTRAL_API_KEY=your-mistral-api-key
```

Pour switcher entre les deux, modifiez simplement `USE_AZURE_OPENAI` dans votre `.env.local`.

### Structure du projet

```
EDTH/
├── app/                    # Next.js app directory
│   ├── api/chat/          # API route pour le chatbot
│   ├── page.tsx           # Page principale
│   └── layout.tsx         # Layout
├── components/            # Composants React
│   ├── ChatMessage.tsx
│   └── ChatInput.tsx
├── lib/
│   └── tools/             # Définitions et exécution des outils
│       ├── schemas.ts     # Schémas Zod
│       ├── definitions.ts # Définitions pour MistralAI
│       └── executor.ts    # Exécuteur des outils
├── serverPython/          # Backend FastAPI
│   ├── main.py
│   ├── config.py
│   ├── api/
│   ├── drone/
│   ├── models/
│   └── requirements.txt
└── package.json
```

## 🔧 Outils disponibles

- `getCoordonnees`: Résout un nom de site en coordonnées GPS
- `getEtatInitial`: Récupère les paramètres par défaut
- `planMissionRecon`: Planifie une mission de reconnaissance
- `takeOff`: Fait décoller le drone
- `goTo`: Déplace le drone vers un point GPS
- `circle`: Fait effectuer une orbite
- `capture`: Prend une photo ou vidéo
- `returnToHome`: Retour au point de départ
- `land`: Atterrissage
- `getStatus`: Récupère l'état du drone

## 🧪 Mode Mock

Le backend fonctionne en mode mock si Olympe n'est pas disponible, permettant de tester toute l'application sans drone réel.

## 📝 Notes

- Pour utiliser avec un vrai drone, installez Olympe SDK et configurez l'IP du drone dans `serverPython/config.py`
- Les coordonnées des centrales sont stockées dans `lib/tools/executor.ts`
- Le format JSON des commandes suit le contrat défini dans `doc/cahier des charges.md`
- Le plan de vol est généré automatiquement et exécuté séquentiellement
- Voir le README principal à la racine du projet pour une vue d'ensemble complète

## 🐛 Dépannage

- Vérifiez que le backend FastAPI est lancé avant le frontend
- Vérifiez vos clés API dans `.env.local` (Azure OpenAI ou MistralAI selon votre choix)
- Vérifiez que `USE_AZURE_OPENAI` est correctement configuré (true/false)
- Consultez les logs du backend pour les erreurs Olympe

## 📄 Licence

Projet développé pour le Hackathon Parrot-2

