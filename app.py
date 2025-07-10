# app.py
from PIL import Image, ImageDraw, ImageFont
import gradio as gr

def poner_marca(imagenes, texto):
    resultados = []
    for img_file in imagenes:
        img = Image.open(img_file.name).convert("RGBA")
        marca = Image.new("RGBA", img.size)
        draw = ImageDraw.Draw(marca)
        font = ImageFont.load_default()
        draw.text((10, 10), texto, fill=(255, 255, 255, 128), font=font)
        resultado = Image.alpha_composite(img, marca).convert("RGB")
        resultados.append(resultado)
    return resultados

demo = gr.Interface(
    fn=poner_marca,
    inputs=[
        gr.File(file_types=["image"], file_count="multiple", label="Sube varias imágenes"),
        gr.Textbox(label="Texto de marca de agua")
    ],
    outputs=gr.Gallery(label="Imágenes con marca")
)

demo.launch(server_name="0.0.0.0", server_port=7860)
