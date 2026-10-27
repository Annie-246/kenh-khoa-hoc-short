// ElevenLabs TTS for the channel voice (Ba Luc, eleven_v4, Vietnamese). Node 18+, no npm install needed.
// Usage (from the project folder):
//   node --env-file="$HOME/.kenh-khoa-hoc-short/.env" <skill>/scripts/tts.mjs script.txt voice.mp3 [voiceId]
import { readFileSync, writeFileSync } from "fs";

const BA_LUC = "KJmTHSk3TjHp87WObL98"; // warm Northern Vietnamese storyteller (Voice Library)
const [inFile = "script.txt", outFile = "voice.mp3", voiceId = BA_LUC] = process.argv.slice(2);
const key = process.env.ELEVENLABS_API_KEY;
if (!key) {
  console.error("Missing ELEVENLABS_API_KEY (put it in ~/.kenh-khoa-hoc-short/.env)");
  process.exit(1);
}
const api = (path, init = {}) =>
  fetch(`https://api.elevenlabs.io${path}`, { ...init, headers: { "xi-api-key": key, "Content-Type": "application/json" } });

const res = await api(`/v1/text-to-speech/${voiceId}?output_format=mp3_44100_128`, {
  method: "POST",
  body: JSON.stringify({
    text: readFileSync(inFile, "utf8"),
    model_id: "eleven_v4",
    language_code: "vi",
    // Low-ish stability = more emotional range for storytelling
    voice_settings: { stability: 0.4, similarity_boost: 0.75 },
  }),
});
if (!res.ok) {
  console.error(`ElevenLabs ${res.status}: ${await res.text()}`);
  process.exit(1);
}
writeFileSync(outFile, Buffer.from(await res.arrayBuffer()));
const sub = await (await api("/v1/user/subscription")).json();
console.log(`Saved ${outFile} | credits used ${sub.character_count}/${sub.character_limit}`);
