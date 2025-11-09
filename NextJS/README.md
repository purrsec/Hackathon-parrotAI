# Parrot AI - Chatbot Next.js

Interface web moderne pour contrôler un drone Parrot via langage naturel.

## 🚀 Démarrage rapide

### Installation des dépendances

```bash
cd NextJS
npm install
```

### Configuration

Créez un fichier `.env.local` à la racine du dossier NextJS (optionnel) :

```env
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

Par défaut, l'application se connecte à `ws://localhost:8000/ws`.

### Lancer l'application

```bash
npm run dev
```

L'application sera accessible sur [http://localhost:3000](http://localhost:3000)

## 📋 Prérequis

- Node.js 18+ 
- Le serveur FastAPI doit être lancé sur le port 8000 (`Olympe-web-server`)

## 🎨 Fonctionnalités

- ✅ Interface de chat moderne style ChatGPT/Ollama
- ✅ Connexion WebSocket temps réel
- ✅ Gestion des messages utilisateur et assistant
- ✅ Affichage des missions DSL générées
- ✅ Confirmation de mission (Yes/No)
- ✅ Indicateur de statut de connexion
- ✅ Mode sombre automatique (selon préférences système)
- ✅ Design responsive

## 💬 Utilisation

1. **Démarrer le serveur FastAPI** :
   ```bash
   cd Olympe-web-server
   uvicorn fastapi_entrypoint:app --reload --port 8000
   ```

2. **Démarrer l'application Next.js** :
   ```bash
   cd NextJS
   npm run dev
   ```

3. **Ouvrir le navigateur** sur http://localhost:3000

4. **Envoyer des commandes** en langage naturel, par exemple :
   - "va inspecter la tour à 30 mètres"
   - "décolle à 10 mètres"
   - "va au point d'intérêt 1"

5. **Confirmer les missions** en tapant "yes" ou "oui" quand une mission est proposée

## 🏗️ Structure du projet

```
NextJS/
├── app/
│   ├── layout.tsx          # Layout principal
│   ├── page.tsx            # Page d'accueil
│   └── globals.css         # Styles globaux
├── components/
│   └── ChatInterface.tsx   # Composant de chat principal
├── types/
│   └── chat.ts             # Types TypeScript
└── package.json
```

## 🔧 Technologies utilisées

- **Next.js 14** - Framework React
- **TypeScript** - Typage statique
- **TailwindCSS** - Styles utilitaires
- **Lucide React** - Icônes
- **WebSocket API** - Communication temps réel

## 📝 Format des messages

### Message utilisateur (envoyé au serveur)
```json
{
  "id": "msg-1234567890-abc123",
  "message": "va inspecter la tour",
  "source": "nextjs",
  "user_id": "user-abc123"
}
```

### Message serveur (reçu)
```json
{
  "type": "message_processed",
  "id": "msg-1234567890-abc123",
  "status": "processed",
  "message": "Mission DSL created successfully",
  "mission_dsl": {
    "missionId": "mission-123",
    "understanding": "Inspecter la tour",
    "segments": [...]
  }
}
```

## 🐛 Dépannage

### L'application ne se connecte pas au serveur

1. Vérifiez que le serveur FastAPI est bien lancé sur le port 8000
2. Vérifiez l'URL WebSocket dans `.env.local` ou dans le code
3. Vérifiez la console du navigateur pour les erreurs

### Les messages ne s'affichent pas

1. Vérifiez la connexion WebSocket (indicateur en bas de l'interface)
2. Vérifiez la console du navigateur pour les erreurs
3. Vérifiez que le format des messages correspond à ce que le serveur attend

## 📚 Documentation

Pour plus d'informations sur le serveur FastAPI, consultez :
- `Olympe-web-server/README.md`
