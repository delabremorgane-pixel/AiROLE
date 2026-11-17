# Chat Mistral (minimal, TypeScript)

App web minimale en TypeScript : un serveur Express appelle l'API Mistral via le
SDK TypeScript officiel [`@mistralai/mistralai`](https://www.npmjs.com/package/@mistralai/mistralai)
avec le modèle `mistral-small-latest`, et sert une interface de chat simple.

La clé `MISTRAL_API_KEY` ne quitte jamais le serveur : le navigateur appelle
uniquement `POST /api/chat`, c'est le serveur qui contacte l'API Mistral.

## Prérequis

- Node.js >= 20 et npm

## Installation

Depuis la racine du dépôt :

```bash
cd mistral-chat
npm install
cp .env.example .env
# puis édite .env et renseigne ta clé :
# MISTRAL_API_KEY=ta_cle_api_mistral
```

La clé se trouve dans la [console Mistral](https://console.mistral.ai/api-keys/).

## Lancer en local (mode développement)

```bash
npm run dev
```

Puis ouvre http://localhost:3000

## Lancer en local (mode buildé)

```bash
npm run build
npm start
```

Toujours sur http://localhost:3000

## Structure

- `src/server.ts` — serveur Express + appel au SDK Mistral (clé côté serveur uniquement)
- `public/` — interface de chat en HTML/CSS/JS vanilla, sans étape de build
- `POST /api/chat` — entrée : `{ "messages": [{ "role": "user" | "assistant" | "system", "content": "..." }] }`, sortie : `{ "reply": "..." }`

## Variables d'environnement

| Variable          | Rôle                                                                | Obligatoire |
| ----------------- | ------------------------------------------------------------------- | ----------- |
| `MISTRAL_API_KEY` | Clé API Mistral (lue uniquement côté serveur, via `.env`)           | oui         |
| `PORT`            | Port d'écoute (défaut : 3000)                                       | non         |

`.env` est ignoré par git : ne commite jamais ta clé.
