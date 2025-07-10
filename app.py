# app.py
import gradio as gr
import os, zipfile
import subprocess
import urllib.parse
import random
import requests
import json
from gtts import gTTS
from moviepy.editor import *
from faster_whisper import WhisperModel

# Variables globales
ELEVEN_API_KEY = ""
PEXELS_API_KEY = ""
modo_generacion = "carrusel"
guiones = []

# ===================== BLOQUE 4 ===================== #
def crear_ass(segmentos, nombre="subs.ass"):
    with open(nombre, "w", encoding="utf-8") as f:
        f.write("""[Script Info]
ScriptType: v4.00+
PlayResX: 480
PlayResY: 854

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Impact,40,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
        for seg in segmentos:
            for word in seg.words:
                texto = word.word.strip().upper().replace("¡", "").replace("!", "").replace("¿", "").replace("?", "")
                if texto:
                    duracion = word.end - word.start
                    dur_por_letra = duracion / len(texto)
                    for i in range(len(texto)):
                        start = word.start + i * dur_por_letra
                        end = start + dur_por_letra
                        parcial = texto[:i+1]
                        def t(t): return f"{int(t//3600)}:{int((t%3600)//60):02}:{int(t%60):02}.{int((t-int(t))*100):02}"
                        f.write(f"Dialogue: 0,{t(start)},{t(end)},Default,,0,0,0,,{parcial}\n")
    return nombre

# ===================== BLOQUES 1 a 5 ===================== #
def ejecutar_todo(eleven_key, pexels_key, modo, guiones_texto, etiquetas_texto):
    global ELEVEN_API_KEY, PEXELS_API_KEY, modo_generacion, guiones
    ELEVEN_API_KEY = eleven_key
    PEXELS_API_KEY = pexels_key
    modo_generacion = modo

    guiones_lines = guiones_texto.strip().splitlines()
    etiquetas_lines = etiquetas_texto.strip().splitlines()
    guiones = list(zip(guiones_lines, etiquetas_lines))

    video_paths = []
    audio_paths = []
    max_resources = 3

    if modo_generacion == "video":
        os.makedirs("clips", exist_ok=True)
        os.makedirs("audios", exist_ok=True)

        for i, (texto, etiqueta) in enumerate(guiones):
            query_encoded = urllib.parse.quote(etiqueta.strip().lower())
            r = requests.get(f"https://api.pexels.com/videos/search?query={query_encoded}&orientation=portrait&size=small&per_page=15", headers={"Authorization": PEXELS_API_KEY})
            videos = json.loads(r.content).get('videos', [])
            if not videos:
                r = requests.get(f"https://api.pexels.com/videos/search?query=technology&orientation=portrait&size=small&per_page=15", headers={"Authorization": PEXELS_API_KEY})
                videos = json.loads(r.content).get('videos', [])

            if videos:
                seleccionados = random.sample(videos, min(len(videos), max_resources))
            else:
                r = requests.get(f"https://api.pexels.com/v1/search?query={query_encoded}&orientation=portrait&size=small&per_page=15", headers={"Authorization": PEXELS_API_KEY})
                fotos = json.loads(r.content).get('photos', [])
                if not fotos:
                    continue
                seleccionados = random.sample(fotos, min(len(fotos), max_resources))

            for idx, recurso in enumerate(seleccionados):
                if videos:
                    video_files = sorted(recurso['video_files'], key=lambda x: x['height'])
                    link = video_files[0]['link']
                    ext = ".mp4"
                else:
                    link = recurso['src']['small']
                    ext = ".jpg"
                file_path = f"clips/clip{i}_{idx}{ext}"
                with open(file_path, "wb") as f:
                    f.write(requests.get(link).content)
                video_paths.append(file_path)

            audio_file = f"audios/audio{i}.mp3"
            tts = gTTS(text=texto, lang="es", tld="com", slow=False)
            tts.save(audio_file)
            audio_paths.append(audio_file)

        model = WhisperModel("small", device="cpu")
        clips_final = []

        for i in range(len(audio_paths)):
            audio_path = audio_paths[i]
            subclip_paths = video_paths[i*3:i*3+3]
            if len(subclip_paths) < 3:
                continue

            result, _ = model.transcribe(audio_path, word_timestamps=True)
            ass_file = crear_ass(result, f"subs{i}.ass")
            duracion = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries','format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]).strip())
            subclips = []

            for path in subclip_paths[:3]:
                try:
                    if path.endswith(".jpg"):
                        c = ImageClip(path, duration=2).resize(height=854).crop(x_center=480//2, width=480)
                    else:
                        base = VideoFileClip(path).resize(height=854)
                        if base.w < 480:
                            base = base.on_color(size=(480, 854), color=(0, 0, 0), pos=("center", "center"))
                        else:
                            base = base.crop(x_center=base.w // 2, width=480)
                        c = base
                    subclips.append(c)
                except: pass

            if not subclips:
                continue

            dur_per_clip = duracion / 3
            recortados = []
            for c in subclips[:3]:
                if c.duration >= dur_per_clip:
                    recortados.append(c.subclip(0, dur_per_clip))
                else:
                    rep = int(dur_per_clip // c.duration) + 1
                    combinado = concatenate_videoclips([c] * rep).subclip(0, dur_per_clip)
                    recortados.append(combinado)

            full_clip = concatenate_videoclips(recortados)
            temp_path = f"temp{i}.mp4"
            full_clip.write_videofile(temp_path, codec="libx264", audio=False)
            full_clip.close()
            final_path = f"final{i}.mp4"
            ffmpeg_cmd = f'ffmpeg -y -i {temp_path} -i {audio_path} -vf "ass=subs{i}.ass" -c:v libx264 -c:a aac -shortest {final_path}'
            result = subprocess.run(ffmpeg_cmd, shell=True)

            if os.path.exists(final_path):
                clips_final.append(VideoFileClip(final_path))

        if clips_final:
            final = concatenate_videoclips(clips_final, method="compose")
            final.write_videofile("video_completo.mp4", codec="libx264", audio_codec="aac")

    elif modo_generacion == "carrusel":
        from PIL import Image, ImageDraw, ImageFont
        import cv2
        import numpy as np
        import textwrap

        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        for i, (texto, etiqueta) in enumerate(guiones):
            img_path = f"imagenes/img{i}.jpg"
            if not os.path.exists(img_path): continue
            img_cv = cv2.imread(img_path)
            h, w = img_cv.shape[:2]
            lado = min(h, w)
            x = (w - lado) // 2
            y = (h - lado) // 2
            img_cv = img_cv[y:y+lado, x:x+lado]
            img_cv = cv2.resize(img_cv, (1080, 1080))
            img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)).convert("RGBA")
            draw = ImageDraw.Draw(img_pil, "RGBA")
            contenido = texto.strip()
            font = ImageFont.truetype(font_path, 64)
            wrapped = textwrap.wrap(contenido, width=25)
            y_text = 500
            for line in wrapped:
                w_line = draw.textlength(line, font=font)
                x_line = (1080 - w_line) // 2
                draw.text((x_line, y_text), line, font=font, fill=(255, 255, 255, 255))
                y_text += 80
            img_pil.convert("RGB").save(f"imagen_{i}.jpg")

    # BLOQUE 5 - Descargar resultados
    if modo_generacion == "video":
        if os.path.exists("video_completo.mp4"):
            return gr.File.update(value="video_completo.mp4", visible=True)
        else:
            return "❌ No se encontró el archivo de video para descargar."
    elif modo_generacion == "carrusel":
        zip_filename = "carrusel_imagenes.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            i = 0
            while True:
                img_file = f"imagen_{i}.jpg"
                if not os.path.exists(img_file):
                    break
                zipf.write(img_file)
                i += 1
        if os.path.exists(zip_filename):
            return gr.File.update(value=zip_filename, visible=True)
        else:
            return "❌ No se pudo crear el archivo ZIP."

# ===================== INTERFAZ GRADIO ===================== #
with gr.Blocks() as demo:
    gr.Markdown("## 🎬 Generador automático de carruseles o reels")
    eleven_input = gr.Textbox(label="🔐 ElevenLabs API Key", type="password")
    pexels_input = gr.Textbox(label="📷 Pexels API Key", type="password")
    modo_input = gr.Radio(["video", "carrusel"], label="Modo de generación", value="carrusel")
    guiones_box = gr.Textbox(label="📝 Guiones (uno por línea)", lines=5)
    etiquetas_box = gr.Textbox(label="🏷️ Etiquetas (una por línea, en inglés)", lines=5)
    ejecutar = gr.Button("🚀 Iniciar")
    output_file = gr.File(label="Descargar resultado", visible=False)

    ejecutar.click(
        fn=ejecutar_todo,
        inputs=[eleven_input, pexels_input, modo_input, guiones_box, etiquetas_box],
        outputs=output_file
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
