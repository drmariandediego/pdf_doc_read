import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# 🔑 API Key y Folder ID desde las variables de entorno de Render
API_KEY = os.getenv("API_KEY")  
FOLDER_ID = os.getenv("FOLDER_ID")  

def obtener_texto_docs():
    """Obtiene texto de todos los archivos .txt en Google Drive."""
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
            return f"Error en la API: {response.json()}"

        data = response.json()
        archivos = data.get("files", [])

        if archivos:
            for archivo in archivos:
                file_id = archivo["id"]
                file_name = archivo["name"]

                # Descargar el contenido del archivo como texto
                url_download = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={API_KEY}"
                response = requests.get(url_download)

                if response.status_code == 200:
                    contenido = response.text
                    documentos.append({"nombre": file_name, "contenido": contenido[:1000]})  # Limita a 1000 caracteres
                else:
                    documentos.append({"nombre": file_name, "contenido": "Error al extraer contenido"})

        # Si hay más páginas, seguimos iterando
        page_token = data.get("nextPageToken", "")
        if not page_token:
            break

    return documentos if documentos else "❌ No se encontraron archivos en la carpeta."

@app.route('/get_docs', methods=['GET'])
def get_docs():
    """API para obtener documentos de Google Drive con su contenido."""
    data = obtener_texto_docs()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
