import fs from "fs";
import {createAudio} from "../utils/audio.js";
import {downloadFromPexels} from "../utils/pexels.js";

export async function generarRecursos({eleven_api, pexels_api, modo, guiones, etiquetas}) {
  fs.writeFileSync("env_vars.env",`ELEVEN_API_KEY=${eleven_api}\nPEXELS_API_KEY=${pexels_api}\nmodo_generacion=${modo}`);
  fs.writeFileSync("guiones.txt",guiones);
  fs.writeFileSync("etiquetas.txt",etiquetas);
  const lines=guiones.split("\n").filter(x=>x.trim());
  fs.mkdirSync("audios",{recursive:true});
  for(let i=0;i<lines.length;i++){
    await createAudio(lines[i],i);
    await downloadFromPexels(lines[i], etiquetas.split("\n")[i]||"",i,modo);
  }
}
