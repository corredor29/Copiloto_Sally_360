import os
from modules.vision.yolo_detector import detectar_objetos
from modules.vision.vlm_conductor import analizar_conductor
from modules.vision.vlm_via import analizar_via
from modules.agent.alert_engine import calcular_alerta


def procesar_frame(filepath: str, vehiculo_id: str = "CAM-001") -> dict:
    """
    Procesa un frame completo ejecutando el pipeline secuencial de Inteligencia Artificial:
    1. YOLOv8 detecta y traduce objetos relevantes en la escena.
    2. GPT-4o analiza el estado conductual del operador usando el contexto de YOLO.
    3. GPT-4o evalúa los riesgos del entorno vial usando el contexto de YOLO.
    4. El Alert Engine fusiona ambos análisis bajo una matriz de riesgo industrial.
    
    Retorna un diccionario estructurado listo para persistencia en la instancia FiftyOne del carro.
    """
    print(f"\n🔍 Procesando: {os.path.basename(filepath)}")

    if not os.path.exists(filepath):
        print(f"⚠️ Error: Archivo frame no encontrado en {filepath}")
        return {
            "vehiculo_id": vehiculo_id,
            "filename": os.path.basename(filepath),
            "filepath": filepath,
            "error": "Archivo no encontrado"
        }

    # ── Paso 1: YOLOv8 (Detector de Objetos Local) ──────────────────────────
    print("   → YOLO detectando objetos...")
    yolo = detectar_objetos(filepath)
    print(f"   → Detectados en español: {yolo.get('clases', [])}")

    # ── Paso 2: GPT-4o (VLM Conductor) ──────────────────────────────────────
    print("   → GPT-4o analizando conductor...")
    conductor = analizar_conductor(filepath, contexto_yolo=yolo)
    print(f"   → Conductor: {conductor.get('estado', 'normal')} (Confianza: {conductor.get('confianza', 0.0)})")

    # ── Paso 3: GPT-4o (VLM Vía y Entorno) ──────────────────────────────────
    print("   → GPT-4o analizando vía...")
    via = analizar_via(filepath, contexto_yolo=yolo)
    print(f"   → Vía: {via.get('estado', 'normal')} (Confianza: {via.get('confianza', 0.0)})")

    # ── Paso 4: Calcular Alerta Final Matrizada ─────────────────────────────
    alerta = calcular_alerta(conductor, via)
    print(f"   → Alerta Final: {alerta.get('nivel', 'bajo').upper()} — {alerta.get('mensaje', '')}")

    # Extraer tokens de forma segura protegiendo contra nulos o respuestas corruptas
    tokens_conductor = conductor.get("tokens", 0) if isinstance(conductor, dict) else 0
    tokens_via = via.get("tokens", 0) if isinstance(via, dict) else 0

    return {
        "vehiculo_id": vehiculo_id,
        "filename": os.path.basename(filepath),  # Facilitará las búsquedas y filtrado a Heiling en FiftyOne
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
    print(f"\n🤖 COPILOTO 360 — Iniciando Procesamiento por Lote del Agente")
    print(f"   Vehículo ID: {vehiculo_id}")
    print(f"   Frames en cola: {len(filepaths)}")

    resultados = []

    for i, filepath in enumerate(filepaths):
        print(f"\n🚀 Lote [{i+1}/{len(filepaths)}]", end="")
        resultado = procesar_frame(filepath, vehiculo_id)
        resultados.append(resultado)

    # Resumen métrico final en consola de servidor
    niveles = [r.get("alerta", {}).get("nivel", "bajo") for r in resultados if "alerta" in r]
    print(f"\n🏁 Agente finalizó lote — {len(resultados)} frames procesados con éxito.")
    print(f"    📊 Distribución de riesgo para {vehiculo_id}:")
    print(f"       🔴 Crítico: {niveles.count('critico')}")
    print(f"       orange Alto:    {niveles.count('alto')}")
    print(f"       🟡 Medio:   {niveles.count('medio')}")
    print(f"       🟢 Bajo:    {niveles.count('bajo')}")

    return resultados