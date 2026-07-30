import os
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# Inicialización segura del cliente con manejo de excepciones
client = None
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        client = genai.Client(api_key=api_key)
except Exception as e:
    print(f"Advertencia al inicializar el cliente de Gemini: {e}")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulador Geológico e Industrial - Procesamiento de Áridos</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 font-sans antialiased">
    <header class="bg-slate-800 border-b border-slate-700 py-6 shadow-md">
        <div class="max-w-7xl mx-auto px-4 flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold tracking-wider text-amber-400">GRAVAFILT S.A. | Módulo Técnico</h1>
                <p class="text-xs text-slate-400">Sistema Experto de Análisis Granulométrico y Simulación de Zarandas Tecmaq</p>
            </div>
            <span class="px-3 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs rounded-full font-mono">IA Motor: Activo</span>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        <section class="bg-slate-800/60 border border-slate-700 rounded-xl p-6 shadow-lg lg:col-span-1">
            <h2 class="text-lg font-semibold mb-4 text-amber-300 border-b border-slate-700 pb-2">Parámetros Físico-Mecánicos</h2>
            <form id="formSimulacion" class="space-y-4">
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Módulo de Fineza (MF):</label>
                    <input type="text" name="modulo_fineza" placeholder="Ej. 2.65" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:border-amber-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Coeficiente de Uniformidad (Cu):</label>
                    <input type="text" name="coef_uniformidad" placeholder="Ej. 3.2" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:border-amber-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Coeficiente de Curvatura (Cc):</label>
                    <input type="text" name="coef_curvatura" placeholder="Ej. 1.1" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:border-amber-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Destino / Tipo de Producto:</label>
                    <select name="tipo_proceso" class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-sm text-white focus:border-amber-500 focus:outline-none">
                        <option value="Arena Industrial / Fraccionada">Arena Industrial / Fraccionada</option>
                        <option value="Grava para Hidrocarburos (Vaca Muerta)">Grava para Petróleo (Vaca Muerta)</option>
                        <option value="Árido para Hormigón H-30">Árido para Hormigón H-30</option>
                        <option value="Arena Especial de Sílice / Revestimiento">Arena Especial para Fundición</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Fotografía del Material (Cinta / Acopio / Muestra):</label>
                    <input type="file" name="imagen_material" accept="image/*" class="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-amber-500/10 file:text-amber-400 hover:file:bg-amber-500/20 cursor-pointer">
                </div>
                <button type="submit" id="btnEjecutar" class="w-full mt-4 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold py-3 px-4 rounded-lg transition-all shadow-md text-sm">
                    Ejecutar Simulación Experta
                </button>
            </form>
        </section>

        <section class="bg-slate-800/60 border border-slate-700 rounded-xl p-6 shadow-lg lg:col-span-2 flex flex-col">
            <h2 class="text-lg font-semibold mb-4 text-amber-300 border-b border-slate-700 pb-2">Informe Técnico y Simulación Granulométrica</h2>
            <div id="loading" class="hidden flex-1 flex flex-col items-center justify-center py-16">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mb-4"></div>
                <p class="text-sm text-slate-400">Procesando matriz granulométrica y evaluando comportamiento en zaranda Tecmaq...</p>
            </div>
            <div id="resultadoContainer" class="flex-1 bg-slate-900/80 border border-slate-700 rounded-lg p-6 overflow-y-auto max-h-[600px] text-sm leading-relaxed text-slate-300 font-mono whitespace-pre-wrap">
                Esperando parámetros e ingresos visuales para generar la evaluación metalúrgica y el cuadro simulador de mallas...
            </div>
        </section>
    </main>

    <script>
        const form = document.getElementById('formSimulacion');
        const resultadoContainer = document.getElementById('resultadoContainer');
        const loading = document.getElementById('loading');
        const btnEjecutar = document.getElementById('btnEjecutar');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            loading.classList.remove('hidden');
            resultadoContainer.classList.add('hidden');
            btnEjecutar.disabled = true;

            try {
                const response = await fetch('/analizar_material', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (data.status === 'success') {
                    resultadoContainer.textContent = data.analisis;
                } else {
                    resultadoContainer.textContent = "Error en el motor: " + data.message;
                }
            } catch (error) {
                resultadoContainer.textContent = "Error de conexión con el servidor.";
            } finally {
                loading.classList.add('hidden');
                resultadoContainer.classList.remove('hidden');
                btnEjecutar.disabled = false;
            }
        });
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return HTML_CONTENT

@app.route('/analizar_material', methods=['POST'])
def analizar_material():
    try:
        if not client:
            return jsonify({
                "status": "error", 
                "message": "La API Key de Gemini no está configurada o el cliente no se pudo inicializar."
            }), 500

        modulo_fineza = request.form.get('modulo_fineza', 'No especificado')
        coef_uniformidad = request.form.get('coef_uniformidad', 'No especificado')
        coef_curvatura = request.form.get('coef_curvatura', 'No especificado')
        tipo_proceso = request.form.get('tipo_proceso', 'Arena Industrial')
        imagen = request.files.get('imagen_material')

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
