import "dotenv/config";
import path from "node:path";
import { fileURLToPath } from "node:url";
import express from "express";
import { Mistral } from "@mistralai/mistralai";
import type { ContentChunk } from "@mistralai/mistralai/models/components";

const MODEL = "mistral-small-latest";

type ChatMessage =
  | { role: "system"; content: string }
  | { role: "user"; content: string }
  | { role: "assistant"; content: string };

function isChatMessage(value: unknown): value is ChatMessage {
  if (typeof value !== "object" || value === null) return false;
  const message = value as Record<string, unknown>;
  return (
    (message.role === "system" ||
      message.role === "user" ||
      message.role === "assistant") &&
    typeof message.content === "string"
  );
}

function contentToText(
  content: string | ContentChunk[] | null | undefined,
): string {
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content
    .filter((chunk) => chunk.type === "text")
    .map((chunk) => ("text" in chunk ? String(chunk.text) : ""))
    .join("");
}

const apiKey = process.env.MISTRAL_API_KEY;
if (!apiKey) {
  console.error(
    "MISTRAL_API_KEY est manquante : copie .env.example en .env puis renseigne ta clé.",
  );
  process.exit(1);
}

const client = new Mistral({ apiKey });

const app = express();
app.use(express.json());

const publicDir = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "public",
);
app.use(express.static(publicDir));

app.post("/api/chat", async (req, res) => {
  const messages = req.body?.messages;
  if (
    !Array.isArray(messages) ||
    messages.length === 0 ||
    !messages.every(isChatMessage)
  ) {
    res.status(400).json({
      error:
        'Corps attendu : { "messages": [{ "role": "user", "content": "..." }] }',
    });
    return;
  }

  try {
    const response = await client.chat.complete({ model: MODEL, messages });
    const reply = contentToText(response.choices?.[0]?.message?.content);
    res.json({ reply });
  } catch (error) {
    console.error(error);
    res.status(502).json({ error: "Appel à l'API Mistral échoué" });
  }
});

const port = Number(process.env.PORT ?? 3000);
app.listen(port, "127.0.0.1", () => {
  console.log(`Chat disponible sur http://127.0.0.1:${port}`);
});
