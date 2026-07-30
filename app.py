import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

# Forzar la ruta absoluta de la carpeta templates y de la aplicación
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# Inicializar el cliente de Gemini de forma segura
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar_material', methods=['POST'])
def analizar_material():
    try:
        if not client:
            return jsonify({
                "status": "error", 
                "message": "La API Key de Gemini no está configurada en las variables de entorno de Render."
            }), 500

        # Recoger parámetros del formulario HTML
        modulo_fineza = request.form.get('modulo_fineza', 'No especificado')
        coef_uniformidad = request.form.get('coef_uniformidad', 'No especificado')
        coef_curvatura = request.form.get('coef_curvatura', 'No especificado')
        tipo_proceso = request.form.get('tipo_proceso', 'Arena Industrial')
        
        imagen = request.files.get('imagen_material')

        # Construir el prompt técnico experto
        prompt_text = (
            f"Actúa como un ingeniero metalúrgico y geólogo experto en procesamiento de áridos, "
            f"operando para el sector industrial (como GRAVAFILT S.A. y aplicaciones en Vaca Muerta). "
            f"Analiza los siguientes parámetros geotécnicos proporcionados:\n"
            f"- Módulo de Fineza (MF): {modulo_fineza}\n"
            f"- Coeficiente de Uniformidad (Cu): {coef_uniformidad}\n"
            f"- Coeficiente de Curvatura (Cc): {coef_curvatura}\n"
            f"- Destino / Producto: {tipo_proceso}\n\n"
            f"Genera un informe técnico riguroso que incluya:\n"
            f"1. Evaluación del comportamiento granulométrico y su idoneidad para el destino indicado.\n"
            f"2. Simulación estimada de rendimiento en zarandas industriales y control de humedad/secado.\n"
            f"3. Recomendaciones de optimización operativa para la planta."
        )

        contents = [prompt_text]

        if imagen and imagen.filename != '':
            image_bytes = imagen.read()
            mime_type = imagen.mimetype or 'image/jpeg'
            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                )
            )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents
        )

        return jsonify({
            "status": "success",
            "analisis": response.text
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
