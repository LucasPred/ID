import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from google import genai
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración y validación robusta de la clave de API (Soporta GEMINI_API_KEY o GOOGLE_API_KEY)
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("No se encontró la clave de API de Gemini en las variables de entorno de Render.")

# Inicializar el cliente oficial de Gemini
client = genai.Client(api_key=api_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar_material', methods=['POST'])
def analizar_material():
    try:
        # Recopilar parámetros técnicos de entrada del formulario
        modulo_fineza = request.form.get('modulo_fineza', 'No especificado')
        coef_uniformidad = request.form.get('coef_uniformidad', 'No especificado')
        coef_curvatura = request.form.get('coef_curvatura', 'No especificado')
        tipo_proceso = request.form.get('tipo_proceso', 'Arena / Grava Estándar')

        prompt_sistema = f"""
        Actúa como un experto geólogo senior e ingeniero metalúrgico especialista en procesamiento de áridos, 
        extracción de arenas fluviales y plantas de clasificación industrial (zarandas Tecmaq, hornos rotativos de secado).
        
        Analiza los siguientes datos de entrada del material:
        - Módulo de Fineza (MF): {modulo_fineza}
        - Coeficiente de Uniformidad (Cu): {coef_uniformidad}
        - Coeficiente de Curvatura (Cc): {coef_curvatura}
        - Aplicación / Destino: {tipo_proceso}

        Genera un informe técnico exhaustivo, preciso y de nivel industrial que incluya:
        1. Criterios técnicos, químicos y organolepticos del material.
        2. Cuadro simulador de ensayo por mallas (ASTM C136) detallando tamaño de apertura, % retenido parcial, % retenido acumulado y % pasante acumulado con alta precisión matemática.
        3. Comportamiento en zarandas rectangulares tipo Tecmaq (eficiencia de separación, inclinación recomendada, amplitud y frecuencia de vibración).
        4. Fundamento técnico y variables críticas para el proceso de secado (temperatura de ingreso/egreso en secador rotativo, control de humedad residual para arenas especiales).
        """

        # Procesar imagen si el usuario la adjuntó
        contents = [prompt_sistema]
        if 'imagen_material' in request.files:
            archivo = request.files['imagen_material']
            if archivo and archivo.filename != '':
                filename = secure_filename(archivo.filename)
                file_bytes = archivo.read()
                # Adjuntar la imagen al contexto multimodal de Gemini
                contents.append(
                    types.Part.from_bytes(
                        data=file_bytes,
                        mime_type=archivo.content_type or 'image/jpeg'
                    )
                )

        # Llamada al modelo Gemini 2.5 Flash para procesamiento rápido y técnico
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents
        )

        return jsonify({"status": "success", "analisis": response.text})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
