import fs from "fs";
import https from "https";

export async function createAudio(texto,index){
  return new Promise((r,rej)=>{
    const url=`https://translate.google.com/translate_tts?ie=UTF-8&q=${encodeURIComponent(texto)}&tl=es&client=tw-ob`;
    const file=fs.createWriteStream(`audios/audio${index}.mp3`);
    https.get(url,res=>{
      res.pipe(file);
      file.on("finish",()=>file.close(r));
    }).on("error",rej);
  });
}
