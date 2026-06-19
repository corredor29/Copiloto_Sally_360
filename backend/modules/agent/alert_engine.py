def calcular_alerta(conductor: dict, via: dict) -> dict:
    """
    Decide el nivel de alerta final combinando
    el análisis del conductor y el de la vía.

    Niveles:
    - critico → peligro inmediato, acción urgente
    - alto    → situación de riesgo, atención requerida
    - medio   → precaución, monitorear
    - bajo    → todo normal
    """

    estado_conductor = conductor.get("estado", "normal")
    estado_via = via.get("estado", "normal")

    # ── Reglas de nivel CRÍTICO ──────────────────────────
    if estado_conductor == "dormido":
        return _alerta("critico", "Conductor dormido al volante", conductor, via)

    if estado_via == "critico":
        return _alerta("critico", "Situación crítica en la vía", conductor, via)

    if estado_conductor == "dormido" and estado_via == "critico":
        return _alerta("critico", "Conductor dormido + situación crítica en vía", conductor, via)

    # ── Reglas de nivel ALTO ─────────────────────────────
    if estado_conductor == "en_riesgo":
        return _alerta("alto", "Conductor en situación de riesgo", conductor, via)

    if estado_via == "peligro":
        return _alerta("alto", "Peligro detectado en la vía", conductor, via)

    if estado_conductor == "fatigado" and estado_via == "precaucion":
        return _alerta("alto", "Conductor fatigado en vía con precaución", conductor, via)

    # ── Reglas de nivel MEDIO ────────────────────────────
    if estado_conductor == "fatigado":
        return _alerta("medio", "Conductor muestra signos de fatiga", conductor, via)

    if estado_conductor == "distraido":
        return _alerta("medio", "Conductor distraído detectado", conductor, via)

    if estado_via == "precaucion":
        return _alerta("medio", "Precaución requerida en la vía", conductor, via)

    # ── Sin alerta ───────────────────────────────────────
    return _alerta("bajo", "Operación normal", conductor, via)


def _alerta(nivel: str, mensaje: str, conductor: dict, via: dict) -> dict:
    """
    Construye el dict de alerta final.
    """
    return {
        "nivel": nivel,
        "mensaje": mensaje,
        "conductor_estado": conductor.get("estado"),
        "conductor_detalle": conductor.get("detalle"),
        "via_estado": via.get("estado"),
        "via_detalle": via.get("detalle"),
        "confianza_promedio": round(
            (conductor.get("confianza", 0) + via.get("confianza", 0)) / 2, 2
        ),
    }