import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { generarContenido } from "./generar.js";
import { generarRecursos } from "./controllers/generarRecursos.js";
import bodyParser from "body-parser";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, "public")));

app.get("/", (_, res) => {
  res.sendFile(path.join(__dirname, "public/index.html"));
});

app.post("/generar", async (req, res) => {
  try {
    const { eleven_api, pexels_api, modo, guiones, etiquetas } = req.body;

    await generarRecursos({ eleven_api, pexels_api, modo, guiones, etiquetas });

    const result = await generarContenido({ modo });

    res.json({ success: true, logs: result });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get("/descargar_video", (_, res) => {
  const path = "./video_completo.mp4";
  if (fs.existsSync(path)) res.download(path);
  else res.status(404).send("Archivo no encontrado");
});

app.get("/descargar_carrusel", (_, res) => {
  const path = "./carrusel_imagenes.zip";
  if (fs.existsSync(path)) res.download(path);
  else res.status(404).send("Archivo no encontrado");
});

app.listen(PORT, () => {
  console.log(`✅ Servidor activo en http://localhost:${PORT}`);
});
