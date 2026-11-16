# AI Roleplay — app locale

Application de roleplay IA pour usage personnel. Serveur FastAPI local + interface web.

## Installation

```bash
cd ai-roleplay
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Crée un fichier `.env` à la racine :

```
MISTRAL_API_KEY=ta_clé_api
```

## Lancement

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Puis ouvre http://127.0.0.1:8000 dans ton navigateur.

## Fonctionnalités

- Plusieurs personnages avec nom, description et prompt système
- Conversations persistantes (JSON dans `data/`)
- Choix du modèle Mistral
- Création/édition de personnages depuis l'interface
