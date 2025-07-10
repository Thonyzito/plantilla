import fs from "fs";
import { createAudio } from "../utils/audio.js";
import { descargarDesdePexels } from "../utils/pexels.js";

export async function generarRecursos({ eleven_api, pexels_api, modo, guiones, etiquetas }) {
  fs.writeFileSync("guiones.txt", guiones);
  fs.writeFileSync("etiquetas.txt", etiquetas);
  fs.writeFileSync("env_vars.env", `ELEVEN_API_KEY=${eleven_api}\nPEXELS_API_KEY=${pexels_api}\nmodo_generacion=${modo}`);

  const guionesArray = guiones.split("\n").filter(x => x.trim() !== "");

  for (let i = 0; i < guionesArray.length; i++) {
    const texto = guionesArray[i];
    await createAudio(texto, i);
    await descargarDesdePexels(texto, i);
  }

  console.log("✅ Recursos descargados y audios generados");
}
