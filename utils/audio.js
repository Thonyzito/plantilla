import gTTS from "gtts";
import fs from "fs";

export async function createAudio(texto, index) {
  return new Promise((resolve, reject) => {
    const gtts = new gTTS(texto, "es");
    const filePath = `audio_${index}.mp3`;
    gtts.save(filePath, err => {
      if (err) reject(err);
      else resolve();
    });
  });

  // // Comentado: ElevenLabs
  // const response = await fetch("https://api.elevenlabs.io/...", {...});
  // const buffer = await response.arrayBuffer();
  // fs.writeFileSync(`audio_${index}.mp3`, Buffer.from(buffer));
}
