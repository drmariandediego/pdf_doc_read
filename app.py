import os
from flask import Flask, jsonify, send_file
from flask_cors
import requests

app = Flask(__name__)
CORS(app)  # 🔥 Habilita CORS en toda la API

# 🔑 API Key y Folder ID desde las variables de entorno de Render
API_KEY = os.getenv("API_KEY")  
FOLDER_ID = os.getenv("FOLDER_ID")  

def obtener_texto_docs():
    """Obtiene TODO el texto de TODOS los Google Docs en la carpeta de Google Drive."""
    documentos = []
    page_token = ""

    while True:
        query_drive = f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.document'"
        url = f"https://www.googleapis.com/drive/v3/files?q={query_drive}&key={API_KEY}&fields=nextPageToken, files(id, name)&pageSize=100"

        if page_token:
            url += f"&pageToken={page_token}"

        response = requests.get(url)

        print("🔍 API RESPONSE:", response.json())  # 👀 Ver respuesta en logs de Render

        if response.status_code != 200:
            return [{"error": f"Error en la API: {response.json()}"}]

        data = response.json()
        archivos = data.get("files", [])

        if archivos:
            for archivo in archivos:
                file_id = archivo["id"]
                file_name = archivo["name"]

                # Exportar el contenido del Google Doc como texto
                url_export = f"https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType=text/plain&key={API_KEY}"
                response = requests.get(url_export)

                if response.status_code == 200:
                    contenido = response.text

                    # 🔥 Solución para caracteres mal formateados (ISO-8859-1 → UTF-8)
                    contenido = contenido.encode("latin1").decode("utf-8", errors="ignore")

                    documentos.append({"nombre": file_name, "contenido": contenido})  # 🔥 SIN LÍMITE DE 1000 CARACTERES
                else:
                    documentos.append({"nombre": file_name, "contenido": "Error al extraer contenido"})

        # Si hay más páginas, seguimos iterando
        page_token = data.get("nextPageToken", "")
        if not page_token:
            break

    return documentos if documentos else [{"error": "❌ No se encontraron documentos en la carpeta."}]

@app.route('/get_docs', methods=['GET'])
def get_docs():
    """API para obtener documentos de Google Drive con TODO su contenido."""
    data = obtener_texto_docs()
    return jsonify(data), 200, {"Content-Type": "application/json; charset=utf-8"}

@app.route('/openapi.yaml', methods=['GET'])
def serve_openapi():
    """Sirve el archivo openapi.yaml desde la raíz del proyecto."""
    openapi_path = os.path.join(os.path.dirname(__file__), "openapi.yaml")
    if os.path.exists(openapi_path):
        return send_file(openapi_path, mimetype='text/yaml')
    else:
        return jsonify({"error": "Archivo openapi.yaml no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
