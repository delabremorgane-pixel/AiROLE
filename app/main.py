import json
import os
import uuid
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

load_dotenv()

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

CHARACTERS_FILE = DATA_DIR / "characters.json"
CHATS_DIR = DATA_DIR / "chats"
CHATS_DIR.mkdir(exist_ok=True)

DEFAULT_MODEL = os.environ.get("MISTRAL_MODEL", "mistral-small-latest")


def _read_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class Character(BaseModel):
    id: str
    name: str
    description: str = ""
    system_prompt: str


class CharacterIn(BaseModel):
    name: str
    description: str = ""
    system_prompt: str


class Message(BaseModel):
    role: str
    content: str


class ChatMessageIn(BaseModel):
    content: str
    model: Optional[str] = None


class Chat(BaseModel):
    id: str
    character_id: str
    title: str
    messages: List[Message] = []


app = FastAPI(title="AI Roleplay")


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/api/characters")
def list_characters():
    return _read_json(CHARACTERS_FILE, [])


@app.post("/api/characters", status_code=201)
def create_character(char_in: CharacterIn):
    characters = _read_json(CHARACTERS_FILE, [])
    char = Character(id=uuid.uuid4().hex[:12], **char_in.model_dump())
    characters.append(char.model_dump())
    _write_json(CHARACTERS_FILE, characters)
    return char


@app.put("/api/characters/{char_id}")
def update_character(char_id: str, char_in: CharacterIn):
    characters = _read_json(CHARACTERS_FILE, [])
    for i, c in enumerate(characters):
        if c["id"] == char_id:
            c.update(char_in.model_dump())
            _write_json(CHARACTERS_FILE, characters)
            return c
    raise HTTPException(404, "Personnage introuvable")


@app.delete("/api/characters/{char_id}")
def delete_character(char_id: str):
    characters = _read_json(CHARACTERS_FILE, [])
    remaining = [c for c in characters if c["id"] != char_id]
    if len(remaining) == len(characters):
        raise HTTPException(404, "Personnage introuvable")
    _write_json(CHARACTERS_FILE, remaining)
    return {"ok": True}


@app.get("/api/chats")
def list_chats():
    chats = []
    for p in CHATS_DIR.glob("*.json"):
        data = _read_json(p, None)
        if data:
            data["messages"] = []
            chats.append(data)
    chats.sort(key=lambda c: c.get("created_at", ""), reverse=True)
    return chats


@app.post("/api/chats", status_code=201)
def create_chat(character_id: str):
    characters = _read_json(CHARACTERS_FILE, [])
    char = next((c for c in characters if c["id"] == character_id), None)
    if not char:
        raise HTTPException(404, "Personnage introuvable")
    chat = {
        "id": uuid.uuid4().hex[:12],
        "character_id": character_id,
        "title": f"Roleplay avec {char['name']}",
        "created_at": __import__("time").time(),
        "messages": [],
    }
    _write_json(CHATS_DIR / f"{chat['id']}.json", chat)
    return chat


@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: str):
    chat = _read_json(CHATS_DIR / f"{chat_id}.json", None)
    if not chat:
        raise HTTPException(404, "Conversation introuvable")
    return chat


@app.delete("/api/chats/{chat_id}")
def delete_chat(chat_id: str):
    p = CHATS_DIR / f"{chat_id}.json"
    if not p.exists():
        raise HTTPException(404, "Conversation introuvable")
    p.unlink()
    return {"ok": True}


@app.post("/api/chats/{chat_id}/messages")
def send_message(chat_id: str, msg: ChatMessageIn):
    chat = _read_json(CHATS_DIR / f"{chat_id}.json", None)
    if not chat:
        raise HTTPException(404, "Conversation introuvable")
    characters = _read_json(CHARACTERS_FILE, [])
    char = next((c for c in characters if c["id"] == chat["character_id"]), None)
    if not char:
        raise HTTPException(404, "Personnage introuvable")

    chat["messages"].append({"role": "user", "content": msg.content})

    from mistralai import Mistral

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise HTTPException(500, "MISTRAL_API_KEY manquante. Crée un fichier .env avec ta clé.")

    client = Mistral(api_key=api_key)
    messages = [{"role": "system", "content": char["system_prompt"]}] + chat["messages"]
    try:
        response = client.chat.complete(
            model=msg.model or DEFAULT_MODEL,
            messages=messages,
        )
    except Exception as e:
        raise HTTPException(502, f"Erreur API Mistral : {e}")

    reply = response.choices[0].message.content
    chat["messages"].append({"role": "assistant", "content": reply})
    _write_json(CHATS_DIR / f"{chat['id']}.json", chat)
    return {"reply": reply}
