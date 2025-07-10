import fs from "fs";
import https from "https";

export async function createAudio(texto, index) {
  return new Promise((resolve, reject) => {
    const url = `https://translate.google.com/translate_tts?ie=UTF-8&q=${encodeURIComponent(texto)}&tl=es&client=tw-ob`;
    const filePath = `audio_${index}.mp3`;

    const file = fs.createWriteStream(filePath);
    https.get(url, res => {
      res.pipe(file);
      file.on("finish", () => file.close(resolve));
    }).on("error", reject);
  });

  // // Comentado: ElevenLabs
  // const response = await fetch("https://api.elevenlabs.io/...", {...});
  // const buffer = await response.arrayBuffer();
  // fs.writeFileSync(`audio_${index}.mp3`, Buffer.from(buffer));
}
