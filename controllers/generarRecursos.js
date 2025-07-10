// controllers/generarRecursos.js
const fs = require("fs");
const path = require("path");
const axios = require("axios");
const { execSync } = require("child_process");
const googleTTS = require("google-tts-api");

const mkdir = (dir) => !fs.existsSync(dir) && fs.mkdirSync(dir, { recursive: true });

async function generarRecursos() {
  const env = fs.readFileSync("env_vars.env", "utf-8").split("\n").reduce((acc, line) => {
    const [k, v] = line.split("=");
    if (k && v) acc[k.trim()] = v.trim();
    return acc;
  }, {});

  const guiones = fs.readFileSync("guiones.txt", "utf-8").split("\n").filter(Boolean);
  const etiquetas = fs.readFileSync("etiquetas.txt", "utf-8").split("\n").filter(Boolean);
  const pares = guiones.map((linea, i) => ({ texto: linea, etiqueta: etiquetas[i] || "technology" }));

  const isVideo = env.modo_generacion === "video";
  const PEXELS_API = env.PEXELS_API_KEY;
  const videoPaths = [];
  const audioPaths = [];

  if (isVideo) mkdir("clips");
  else mkdir("imagenes");

  mkdir("audios");

  for (let i = 0; i < pares.length; i++) {
    const { texto, etiqueta } = pares[i];
    const query = encodeURIComponent(etiqueta.toLowerCase());
    let recursos = [];

    const searchUrl = isVideo
      ? `https://api.pexels.com/videos/search?query=${query}&orientation=portrait&size=small&per_page=15`
      : `https://api.pexels.com/v1/search?query=${query}&orientation=portrait&size=small&per_page=15`;

    const fallbackUrl = isVideo
      ? `https://api.pexels.com/videos/search?query=technology&orientation=portrait&size=small&per_page=15`
      : `https://api.pexels.com/v1/search?query=technology&orientation=portrait&size=small&per_page=15`;

    try {
      const res = await axios.get(searchUrl, { headers: { Authorization: PEXELS_API } });
      recursos = isVideo ? res.data.videos : res.data.photos;
      if (recursos.length === 0) {
        const fallback = await axios.get(fallbackUrl, { headers: { Authorization: PEXELS_API } });
        recursos = isVideo ? fallback.data.videos : fallback.data.photos;
      }
    } catch (err) {
      console.log(`❌ Error al buscar en Pexels: ${err.message}`);
      continue;
    }

    const seleccionados = recursos.slice(0, 3);
    for (let j = 0; j < seleccionados.length; j++) {
      const recurso = seleccionados[j];
      const ext = isVideo ? ".mp4" : ".jpg";
      const outputPath = isVideo
        ? `clips/clip${i}_${j}${ext}`
        : `imagenes/img${i}${ext}`;
      const url = isVideo
        ? recurso.video_files[0].link
        : recurso.src.medium;

      const buffer = (await axios.get(url, { responseType: "arraybuffer" })).data;
      fs.writeFileSync(outputPath, buffer);
      if (isVideo) videoPaths.push(outputPath);
    }

    // 🎙 Audio con gTTS
    const gttsUrl = googleTTS.getAudioUrl(texto, { lang: 'es', slow: false });
    const audioFile = `audios/audio${i}.mp3`;
    const audioBuffer = (await axios.get(gttsUrl, { responseType: "arraybuffer" })).data;
    fs.writeFileSync(audioFile, audioBuffer);
    audioPaths.push(audioFile);

    // 🔉 (opcional) ElevenLabs - comentado por ahora
    /*
    const audio = await axios.post(
      'https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb',
      {
        text: texto,
        model_id: 'eleven_multilingual_v2',
        voice_settings: { stability: 0.5, similarity_boost: 0.5 }
      },
      {
        headers: {
          "xi-api-key": env.ELEVEN_API_KEY,
          "Content-Type": "application/json"
        },
        responseType: "arraybuffer"
      }
    );
    fs.writeFileSync(audioFile, audio.data);
    */
  }

  return { audioPaths, videoPaths };
}

module.exports = generarRecursos;
