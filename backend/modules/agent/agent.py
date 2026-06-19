import os
import threading
import pyttsx3
from modules.vision.yolo_detector import detectar_objetos
from modules.vision.vlm_conductor import analizar_conductor
from modules.vision.vlm_via import analizar_via
from modules.agent.alert_engine import calcular_alerta


def reproducir_alerta_voz(mensaje: str):
    """
    Inicializa el motor de texto a voz de forma local buscando una variante
    femenina natural y fluida para las alertas de cabina.
    """
    try:
        engine = pyttsx3.init()
        
        # Ajustar la velocidad para que la locución sea clara y natural (175 es ideal)
        engine.setProperty('rate', 175)
        
        voices = engine.getProperty('voices')
        voice_seleccionada = None

        # Estrategia de búsqueda de prioridad 1: Voces femeninas avanzadas de Windows (Sabina, Laura, Mobile)
        for voice in voices:
            nombre = voice.name.lower()
            if "spanish" in nombre or "spain" in nombre or "mexico" in nombre or "es-" in voice.id.lower():
                if "sabina" in nombre or "laura" in nombre or "mobile" in nombre:
                    voice_seleccionada = voice.id
                    break

        # Estrategia de búsqueda de prioridad 2: Voz femenina estándar (Helena) si las premium no están instaladas
        if not voice_seleccionada:
            for voice in voices:
                nombre = voice.name.lower()
                if "helena" in nombre:
                    voice_seleccionada = voice.id
                    break

        # Estrategia de búsqueda de prioridad 3: Cualquier voz disponible que contenga español
        if not voice_seleccionada:
            for voice in voices:
                nombre = voice.name.lower()
                if "spanish" in nombre or "es-" in voice.id.lower():
                    voice_seleccionada = voice.id
                    break

        # Aplicar la voz seleccionada si se encontró una coincidencia válida
        if voice_seleccionada:
            engine.setProperty('voice', voice_seleccionada)
                
        engine.say(mensaje)
        engine.runAndWait()
    except Exception as e:
        print(f"AVISO: No se pudo reproducir el audio de asistencia: {e}")


def emitir_asistente_voz(mensaje: str):
    """
    Lanza la alerta por comandos de voz utilizando hilos de ejecución (threading)
    para no congelar ni retrasar el análisis de los siguientes segundos de video.
    """
    hilo = threading.Thread(target=reproducir_alerta_voz, args=(mensaje,))
    hilo.daemon = True
    hilo.start()


def emitir_saludo_bienvenida():
    """
    Emite un saludo inicial de presentación al arrancar el sistema
    para confirmar que el motor de audio y asistencia de Sally está activo.
    """
    frase = "Hola, soy Sally, tu asistente de cabina inteligente. Estoy lista para monitorear la ruta y asistir al conductor."
    emitir_asistente_voz(frase)


def procesar_frame(filepath: str, vehiculo_id: str = "CAM-001") -> dict:
    """
    Procesa un frame completo ejecutando el pipeline secuencial de Inteligencia Artificial:
    1. YOLOv8 detecta y traduce objetos relevantes en la escena.
    2. GPT-4o analiza el estado conductual del operador usando el contexto de YOLO.
    3. GPT-4o evalúa los riesgos del entorno vial usando el contexto de YOLO.
    4. El Alert Engine fusiona ambos análisis bajo una matriz de riesgo industrial.
    5. El asistente de voz emite instrucciones habladas inmediatas si el riesgo es elevado.
    
    Retorna un diccionario estructurado listo para persistencia en la instancia FiftyOne del carro.
    """
    print(f"\n[PROCESANDO] Archivo: {os.path.basename(filepath)}")

    if not os.path.exists(filepath):
        print(f"ERROR: Archivo frame no encontrado en {filepath}")
        return {
            "vehiculo_id": vehiculo_id,
            "filename": os.path.basename(filepath),
            "filepath": filepath,
            "error": "Archivo no encontrado"
        }

    # ── Paso 1: YOLOv8 (Detector de Objetos Local) ──────────────────────────
    print("    → YOLO detectando objetos...")
    yolo = detectar_objetos(filepath)
    print(f"    → Detectados en español: {yolo.get('clases', [])}")

    # ── Paso 2: GPT-4o (VLM Conductor) ──────────────────────────────────────
    print("    → GPT-4o analizando conductor...")
    conductor = analizar_conductor(filepath, contexto_yolo=yolo)
    print(f"    → Conductor: {conductor.get('estado', 'normal')} (Confianza: {conductor.get('confianza', 0.0)})")

    # ── Paso 3: GPT-4o (VLM Vía y Entorno) ──────────────────────────────────
    print("    → GPT-4o analizando vía...")
    via = analizar_via(filepath, contexto_yolo=yolo)
    print(f"    → Vía: {via.get('estado', 'normal')} (Confianza: {via.get('confianza', 0.0)})")

    # ── Paso 4: Calcular Alerta Final Matrizada ─────────────────────────────
    alerta = calcular_alerta(conductor, via)
    nivel_alerta = alerta.get('nivel', 'bajo').lower()
    mensaje_alerta = alerta.get('mensaje', '')
    print(f"    → Alerta Final: {nivel_alerta.upper()} — {mensaje_alerta}")

    # ── Paso 5: Asistente Narrativo de Cabina en Tiempo Real ────────────────
    # Filtra y emite de forma audible los avisos de riesgo prioritarios (Medio, Alto, Crítico)
    if nivel_alerta in ["medio", "alto", "critico"] and mensaje_alerta:
        emitir_asistente_voz(mensaje_alerta)

    # Extraer tokens de forma segura protegiendo contra nulos o respuestas corruptas
    tokens_conductor = conductor.get("tokens", 0) if isinstance(conductor, dict) else 0
    tokens_via = via.get("tokens", 0) if isinstance(via, dict) else 0

    return {
        "vehiculo_id": vehiculo_id,
        "filename": os.path.basename(filepath),
        "filepath": filepath,
        "yolo": yolo,
        "conductor": conductor,
        "via": via,
        "alerta": alerta,
        "tokens_total": (tokens_conductor or 0) + (tokens_via or 0),
    }


def correr_agente(filepaths: list, vehiculo_id: str = "CAM-001") -> list:
    """
    Corre el pipeline secuencial sobre un lote de imágenes o secuencias sueltas.
    Utilizado principalmente para análisis Batch o testing local.
    """
    print(f"\n[INICIO] COPILOTO 360 — Iniciando Procesamiento por Lote del Agente")
    print(f"    Vehículo ID: {vehiculo_id}")
    print(f"    Frames en cola: {len(filepaths)}")

    resultados = []

    for i, filepath in enumerate(filepaths):
        print(f"\n[LOTE {i+1}/{len(filepaths)}]", end="")
        resultado = procesar_frame(filepath, vehiculo_id)
        resultados.append(resultado)

    # Resumen métrico final en consola de servidor
    niveles = [r.get("alerta", {}).get("nivel", "bajo") for r in resultados if "alerta" in r]
    print(f"\n[FIN] Agente finalizó lote — {len(resultados)} frames procesados con éxito.")
    print(f"    Distribución de riesgo para {vehiculo_id}:")
    print(f"        Crítico: {niveles.count('critico')}")
    print(f"        Alto:    {niveles.count('alto')}")
    print(f"        Medio:   {niveles.count('medio')}")
    print(f"        Bajo:    {niveles.count('bajo')}")

    return resultados