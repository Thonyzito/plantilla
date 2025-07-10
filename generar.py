# generar.py
import os, json, requests, random, urllib.parse, zipfile
from gtts import gTTS
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip
import whisper

from PIL import Image, ImageDraw, ImageFont
import cv2
import textwrap
import subprocess

# Leer entradas
with open("env_vars.env") as f:
    lines = f.read().strip().splitlines()
    env = dict(line.split("=", 1) for line in lines)

ELEVEN_API_KEY = env.get("ELEVEN_API_KEY", "")
PEXELS_API_KEY = env.get("PEXELS_API_KEY", "")
modo_generacion = env.get("modo_generacion", "video")

with open("guiones.txt") as f:
    guiones_text = f.read().strip().splitlines()
with open("etiquetas.txt") as f:
    etiquetas_text = f.read().strip().splitlines()

guiones = list(zip(guiones_text, etiquetas_text))
video_paths = []
audio_paths = []
os.makedirs("clips", exist_ok=True)
os.makedirs("audios", exist_ok=True)
os.makedirs("imagenes", exist_ok=True)

if modo_generacion == "video":
    for i, (texto, etiqueta) in enumerate(guiones):
        query = urllib.parse.quote(etiqueta.strip().lower())
        r = requests.get(f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&size=small&per_page=5",
                         headers={"Authorization": PEXELS_API_KEY})
        videos = r.json().get('videos', [])

        if not videos:
            r = requests.get(f"https://api.pexels.com/v1/search?query=technology&orientation=portrait&size=small&per_page=5",
                             headers={"Authorization": PEXELS_API_KEY})
            fotos = r.json().get('photos', [])
            for idx, recurso in enumerate(fotos[:3]):
                link = recurso['src']['small']
                path = f"clips/clip{i}_{idx}.jpg"
                with open(path, "wb") as f: f.write(requests.get(link).content)
                video_paths.append(path)
        else:
            for idx, recurso in enumerate(videos[:3]):
                video_file = sorted(recurso['video_files'], key=lambda x: x['height'])[0]
                link = video_file['link']
                path = f"clips/clip{i}_{idx}.mp4"
                with open(path, "wb") as f: f.write(requests.get(link).content)
                video_paths.append(path)

        audio_file = f"audios/audio{i}.mp3"
        gTTS(text=texto, lang="es").save(audio_file)
        audio_paths.append(audio_file)

elif modo_generacion == "carrusel":
    for i, (texto, etiqueta) in enumerate(guiones):
        query = urllib.parse.quote(etiqueta.strip().lower())
        r = requests.get(f"https://api.pexels.com/v1/search?query={query}&orientation=portrait&size=small&per_page=5",
                         headers={"Authorization": PEXELS_API_KEY})
        fotos = r.json().get("photos", [])
        if not fotos: continue
        img_url = fotos[0]['src']['medium']
        img_path = f"imagenes/img{i}.jpg"
        with open(img_path, "wb") as f: f.write(requests.get(img_url).content)

        img_cv = cv2.imread(img_path)
        h, w = img_cv.shape[:2]
        side = min(h, w)
        img_cv = img_cv[(h - side)//2:(h + side)//2, (w - side)//2:(w + side)//2]
        img_cv = cv2.resize(img_cv, (1080, 1080))
        img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)).convert("RGBA")
        draw = ImageDraw.Draw(img_pil)

        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(font_path, 60)
        wrapped = textwrap.wrap(texto, width=25)
        y = 500 - len(wrapped) * 40
        for line in wrapped:
            w = draw.textlength(line, font=font)
            x = (1080 - w)//2
            draw.text((x, y), line, font=font, fill=(255,255,255))
            y += 80

        img_pil.convert("RGB").save(f"imagen_{i}.jpg")

    with zipfile.ZipFile("carrusel_imagenes.zip", 'w') as zipf:
        for i in range(len(guiones)):
            path = f"imagen_{i}.jpg"
            if os.path.exists(path):
                zipf.write(path)

else:
    print("Modo no reconocido")
    exit()

if modo_generacion == "video":
    model = whisper.load_model("small")
    final_clips = []

    for i in range(len(audio_paths)):
        audio_path = audio_paths[i]
        clip_paths = video_paths[i*3:i*3+3]

        result = model.transcribe(audio_path)
        duracion = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]).strip())

        subclips = []
        for path in clip_paths:
            if path.endswith(".jpg"):
                c = ImageClip(path, duration=duracion/3).resize(height=854).crop(x_center=240, width=480)
            else:
                base = VideoFileClip(path).resize(height=854)
                if base.w < 480:
                    base = base.on_color(size=(480, 854), color=(0,0,0), pos=("center","center"))
                else:
                    base = base.crop(x_center=base.w//2, width=480)
                c = base.subclip(0, min(base.duration, duracion/3))
            subclips.append(c)

        full_clip = concatenate_videoclips(subclips)
        temp_path = f"temp{i}.mp4"
        full_clip.write_videofile(temp_path, codec="libx264", audio=False)
        full_clip.close()

        final_path = f"final{i}.mp4"
        ffmpeg_cmd = f"ffmpeg -y -i {temp_path} -i {audio_path} -c:v libx264 -c:a aac -shortest {final_path}"
        subprocess.run(ffmpeg_cmd, shell=True)

        if os.path.exists(final_path):
            final_clips.append(VideoFileClip(final_path))

    if final_clips:
        final = concatenate_videoclips(final_clips, method="compose")
        final.write_videofile("video_completo.mp4", codec="libx264", audio_codec="aac")
