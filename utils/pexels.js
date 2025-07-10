import fs from "fs";
import https from "https";

export async function downloadFromPexels(texto, etiqueta, idx, modo){
  const key=fs.readFileSync("env_vars.env","utf-8").split("\n").find(l=>l.startsWith("PEXELS_API_KEY")).split("=")[1];
  const q=encodeURIComponent(etiqueta||"technology");
  const url=modo==="video"
    ? `https://api.pexels.com/videos/search?query=${q}&orientation=portrait&size=small&per_page=3`
    : `https://api.pexels.com/v1/search?query=${q}&orientation=portrait&size=small&per_page=3`;
  const opts={headers:{"Authorization":key}};
  const data=await new Promise((r,f)=>https.get(url,opts,res=>{
    let b="";res.on("data",c=>b+=c);res.on("end",()=>r(JSON.parse(b)));
  }).on("error",f));
  const item=modo==="video"?data.videos?.[0]:data.photos?.[0];
  if(!item)return;
  const fileUrl=modo==="video"?item.video_files[0].link:item.src.medium;
  const ext=modo==="video"?".mp4":".jpg";
  const path=`${modo==="video"?"clips":"imagenes"}/${modo==="video"?"clip":"img"}${idx}${ext}`;
  fs.mkdirSync(modo==="video"?"clips":"imagenes",{recursive:true});
  await new Promise((r,f)=>https.get(fileUrl,res=>{
    const file=fs.createWriteStream(path);
    res.pipe(file);file.on("finish",()=>file.close(r));
  }).on("error",f));
}
