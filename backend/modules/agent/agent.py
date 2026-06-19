import os
from modules.vision.yolo_detector import detectar_objetos
from modules.vision.vlm_conductor import analizar_conductor
from modules.vision.vlm_via import analizar_via
from modules.agent.alert_engine import calcular_alerta


def procesar_frame(filepath: str, vehiculo_id: str = "CAM-001") -> dict:
    """
    Procesa un frame completo:
    1. YOLO detecta objetos
    2. GPT-4o analiza conductor
    3. GPT-4o analiza vía
    4. Alert engine decide nivel de alerta
    Retorna dict completo listo para guardar en FiftyOne.
    """
    print(f"\n🔍 Procesando: {os.path.basename(filepath)}")

    # ── Paso 1: YOLO ─────────────────────────────────────
    print("   → YOLO detectando objetos...")
    yolo = detectar_objetos(filepath)
    print(f"   → Detectados: {yolo['clases']}")

    # ── Paso 2: GPT-4o analiza conductor ─────────────────
    print("   → GPT-4o analizando conductor...")
    conductor = analizar_conductor(filepath, contexto_yolo=yolo)
    print(f"   → Conductor: {conductor['estado']} ({conductor['confianza']})")

    # ── Paso 3: GPT-4o analiza vía ───────────────────────
    print("   → GPT-4o analizando vía...")
    via = analizar_via(filepath, contexto_yolo=yolo)
    print(f"   → Vía: {via['estado']} ({via['confianza']})")

    # ── Paso 4: Calcular alerta final ────────────────────
    alerta = calcular_alerta(conductor, via)
    print(f"   → Alerta: {alerta['nivel'].upper()} — {alerta['mensaje']}")

    return {
        "vehiculo_id": vehiculo_id,
        "filepath": filepath,
        "yolo": yolo,
        "conductor": conductor,
        "via": via,
        "alerta": alerta,
        "tokens_total": conductor.get("tokens", 0) + via.get("tokens", 0),
    }


def correr_agente(filepaths: list, vehiculo_id: str = "CAM-001") -> list:
    """
    Corre el agente sobre una lista de frames.
    Retorna lista de resultados listos para guardar en FiftyOne.
    """
    print(f"\n COPILOTO 360 — Iniciando agente")
    print(f"   Vehículo: {vehiculo_id}")
    print(f"   Frames a procesar: {len(filepaths)}")

    resultados = []

    for i, filepath in enumerate(filepaths):
        print(f"\n[{i+1}/{len(filepaths)}]", end="")
        resultado = procesar_frame(filepath, vehiculo_id)
        resultados.append(resultado)

    # Resumen final
    niveles = [r["alerta"]["nivel"] for r in resultados]
    print(f"\n Agente terminó — {len(resultados)} frames procesados")
    print(f"    Crítico: {niveles.count('critico')}")
    print(f"    Alto:    {niveles.count('alto')}")
    print(f"    Medio:   {niveles.count('medio')}")
    print(f"    Bajo:    {niveles.count('bajo')}")

    return resultados