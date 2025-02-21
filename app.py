import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# 🔑 API Key y Folder ID desde las variables de entorno de Render
API_KEY = os.getenv("API_KEY")  
FOLDER_ID = os.getenv("FOLDER_ID")  

def obtener_texto_docs():
    """Obtiene texto de todos los archivos .txt en Google Drive."""
    query_drive = f"'{FOLDER_ID}' in parents and mimeType='text/plain'"
    url = f"https://www.googleapis.com/drive/v3/files?q={query_drive}&key={API_KEY}&fields=files(id, name)&pageSize=100"

    response = requests.get(url)
    
    print("🔍 API RESPONSE:", response.json())  # 👀 Ver respuesta en logs de Render

    if response.status_code != 200:
        return f"Error en la API: {response.json()}"

    archivos = response.json().get("files", [])

    if not archivos:
        return "❌ No se encontraron archivos en la carpeta."

    documentos = [{"nombre": archivo["name"]} for archivo in archivos]

    return documentos

@app.route('/get_docs', methods=['GET'])
def get_docs():
    """API para obtener documentos de Google Drive."""
    data = obtener_texto_docs()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
