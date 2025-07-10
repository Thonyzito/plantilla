// utils/audio.js
import fs from "fs";
import gTTS from "gtts";

export async function createAudio(texto, index) {
  return new Promise((resolve, reject) => {
    const gtts = new gTTS(texto, "es");
    const filePath = `audio_${index}.mp3`;
    gtts.save(filePath, err => {
      if (err) reject(err);
      else resolve();
    });
  });

  // // Comentado: ElevenLabs para usar después
  // const response = await fetch("https://api.elevenlabs.io/v1/text-to-speech/...", { method: "POST", headers: {...}, body: ... });
  // const buffer = await response.arrayBuffer();
  // fs.writeFileSync(`audio_${index}.mp3`, Buffer.from(buffer));
}
