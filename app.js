import express from "express";
import path from "path";
import bodyParser from "body-parser";
import fs from "fs";
import { generarRecursos } from "./controllers/generarRecursos.js";
import { crearFinal } from "./controllers/crearFinal.js";

const app=express(), PORT=process.env.PORT||3000;
app.use(bodyParser.json(), express.static("public"));
app.get("/",(_,r)=>r.sendFile(path.join(__dirname,"public/index.html")));

app.post("/generar",async(req,res)=>{
  try {
    const { eleven_api, pexels_api, modo, guiones, etiquetas }=req.body;
    await generarRecursos({ eleven_api, pexels_api, modo, guiones, etiquetas });
    await crearFinal(modo);
    res.json({success:true, logs:"✅ Finalizado"});
  } catch(e){
    res.status(500).json({success:false,error:e.message});
  }
});

app.get("/descargar_video",(req,res)=>{
  fs.existsSync("video_completo.mp4")?
    res.download("video_completo.mp4"):
    res.status(404).send("No existe");
});

app.get("/descargar_carrusel",(req,res)=>{
  fs.existsSync("carrusel_imagenes.zip")?
    res.download("carrusel_imagenes.zip"):
    res.status(404).send("No existe");
});

app.listen(PORT,()=>console.log(`Escuchando en :${PORT}`));
