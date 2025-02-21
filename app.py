from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔑 API Key de Google Drive
API_KEY = "AIzaSyDLDfuBZO74G3ilpzH4S_DPpQPxrGK7Rj8"  # Reemplaza con tu API Key

# 📂 ID de la carpeta de Google Drive
FOLDER_ID = "1GJ9SwhmqYR7KDC4J6P-DV_lj_IIwjZaN"  # Reemplaza con tu Folder ID

def obtener_texto_docs():
    """Extrae texto de documentos de Google Docs en una carpeta."""
    query_drive = f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.document'"
    url = f"https://www.googleapis.com/drive/v3/files?q={query_drive}&key={API_KEY}&fields=files(id, name)"

    response = requests.get(url)
    archivos = response.json().get("files", [])

    if not archivos:
        return []

    resultados = []

    for archivo in archivos:
        file_id = archivo["id"]
        file_name = archivo["name"]

        # Exportar contenido del documento como texto
        url_export = f"https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType=text/plain&key={API_KEY}"
        response = requests.get(url_export)

        if response.status_code == 200:
            contenido = response.text
            resultados.append({"nombre": file_name, "contenido": contenido[:1000]})  # Limita a 1000 caracteres
        else:
            resultados.append({"nombre": file_name, "contenido": "Error al extraer contenido"})

    return resultados

# ✅ Nueva ruta para obtener documentos de Google Docs
@app.route('/get_docs', methods=['GET'])
def get_docs():
    """API para obtener documentos de Google Docs."""
    data = obtener_texto_docs()
    return jsonify(data)

# ✅ Ruta original para obtener PDFs
@app.route("/get_pdfs", methods=["GET"])
def get_pdfs():
    pdfs = obtener_pdfs()
    return jsonify({"pdfs": pdfs})

# ✅ Ruta original para buscar y leer un PDF relevante según la pregunta del usuario
@app.route("/buscar_pdf", methods=["POST"])
def buscar_pdf():
    data = request.json
    pregunta = data.get("pregunta")
    
    if not pregunta:
        return jsonify({"error": "Se requiere una pregunta"}), 400
    
    pdf_url = buscar_pdf_relevante(pregunta)
    
    if pdf_url:
        contenido = descargar_y_leer_pdf(pdf_url)
        return jsonify({"pdf_url": pdf_url, "contenido": contenido[:1000]})  # Limitamos la salida
    else:
        return jsonify({"error": "No se encontró un PDF relevante"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
