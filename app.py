from flask import Flask, request, jsonify

app = Flask(__name__)

# Ruta para obtener la lista de PDFs de la AIP
@app.route("/get_pdfs", methods=["GET"])
def get_pdfs():
    pdfs = obtener_pdfs()
    return jsonify({"pdfs": pdfs})

# Ruta para buscar y leer un PDF relevante según la pregunta del usuario
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
    app.run(debug=True)
