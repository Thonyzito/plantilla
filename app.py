# app.py
from flask import Flask, request, send_file, jsonify, send_from_directory
import subprocess, os

app = Flask(__name__, static_folder="public")

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

modo_actual = ""

@app.route('/generar', methods=['POST'])
def generar():
    data = request.json

    eleven_api = data.get("eleven_api", "")
    pexels_api = data.get("pexels_api", "")
    modo = data.get("modo", "video")
    guiones = data.get("guiones", "")
    etiquetas = data.get("etiquetas", "")

    try:
        with open("env_vars.env", "w") as f:
            f.write(f"ELEVEN_API_KEY={eleven_api}\nPEXELS_API_KEY={pexels_api}\nmodo_generacion={modo}")
        with open("guiones.txt", "w") as f:
            f.write(guiones)
        with open("etiquetas.txt", "w") as f:
            f.write(etiquetas)

        global modo_actual
        modo_actual = modo

        result = subprocess.run(["python3", "generar.py"], capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"success": False, "error": result.stderr})

        return jsonify({"success": True, "logs": result.stdout})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/descargar_video')
def descargar_video():
    path = "video_completo.mp4"
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Archivo no encontrado", 404


@app.route('/descargar_carrusel')
def descargar_carrusel():
    path = "carrusel_imagenes.zip"
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Archivo no encontrado", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
