def calcular_alerta(conductor: dict, via: dict) -> dict:
    """
    Decide el nivel de alerta final combinando de forma matricial
    el análisis en tiempo real del conductor y el de la vía.

    Niveles:
    - critico → Peligro inminente de colisión o pérdida de control. Acción inmediata.
    - alto    → Riesgo severo latente. Requiere corrección del operador.
    - medio   → Anomalía moderada o entorno que requiere precaución. Monitorear.
    - bajo    → Operación totalmente normal.
    """
    estado_conductor = conductor.get("estado", "normal").lower().strip()
    estado_via = via.get("estado", "normal").lower().strip()


    
    # 1. La combinación más destructiva posible (Debe ir primero para que sea alcanzable)
    if estado_conductor == "dormido" and estado_via == "critico":
        return _alerta("critico", " CRISIS: ¡Conductor dormido ante colisión inminente en vía!", conductor, via)
        
    # 2. Conductor dormido (Pérdida total del control del vehículo)
    if estado_conductor == "dormido":
        return _alerta("critico", " CRÍTICO: Conductor dormido al volante. Activar alerta sonora.", conductor, via)
        
    # 3. Comportamientos de riesgo extremo según prompt industrial (ej: desmayo o soltar volante)
    if estado_conductor == "en_riesgo":
        return _alerta("critico", " CRÍTICO: Maniobra o estado del conductor de riesgo extremo detectado.", conductor, via)
        
    # 4. Situación catastrófica o colisión inminente en la carretera
    if estado_via == "critico":
        return _alerta("critico", " CRÍTICO: Peligro de colisión inminente u obstáculo insuperable en vía.", conductor, via)

    # 5. Combinación de riesgo acumulado: Conductor distraído/fatigado + Vía en Peligro
    if estado_conductor in ["distraido", "fatigado"] and estado_via == "peligro":
        return _alerta("critico", " CRÍTICO: Conductor incapacitado/distraído en escenario de peligro vial.", conductor, via)



    
    # 6. Peligro directo detectado en la carretera (Vehículo muy cerca o peatón cruzando)
    if estado_via == "peligro":
        return _alerta("alto", " ALTO: Condiciones de peligro detectadas en el entorno vial.", conductor, via)
        
    # 7. Fatiga acumulada combinada con factores de infraestructura complejos
    if estado_conductor == "fatigado" and estado_via == "precaucion":
        return _alerta("alto", " ALTO: Conductor fatigado transitando por zona de precaución vial.", conductor, via)

    # 8. Distracción en condiciones que exigen atención (ej: curvas u obras)
    if estado_conductor == "distraido" and estado_via == "precaucion":
        return _alerta("alto", " ALTO: Conductor distraído en zona que requiere atención.", conductor, via)



    
    # 9. Signos iniciales de cansancio o pesadez
    if estado_conductor == "fatigado":
        return _alerta("medio", " MEDIO: El conductor muestra signos tempranos de fatiga.", conductor, via)
        
    # 10. Pérdida momentánea de atención (mirar a los lados, etc.)
    if estado_conductor == "distraido":
        return _alerta("medio", " MEDIO: Evento de distracción moderada del conductor.", conductor, via)
        
    # 11. Entorno de la carretera complejo pero controlable (lluvia leve, tráfico denso)
    if estado_via == "precaucion":
        return _alerta("medio", " MEDIO: Condiciones de la vía requieren conducción defensiva.", conductor, via)



    return _alerta("bajo", " BAJO: Operación de conducción estable y segura.", conductor, via)


def _alerta(nivel: str, mensaje: str, conductor: dict, via: dict) -> dict:
    """
    Construye de forma estandarizada y segura el payload del JSON de alerta.
    Garantiza consistencia de tipos de datos para consumo de API y Base de Datos.
    """
    return {
        "nivel": nivel,
        "mensaje": mensaje,
        "conductor_estado": conductor.get("estado", "normal"),
        "conductor_detalle": conductor.get("detalle", ""),
        "via_estado": via.get("estado", "normal"),
        "via_detalle": via.get("detalle", ""),
        "confianza_promedio": round(
            (float(conductor.get("confianza", 0)) + float(via.get("confianza", 0))) / 2, 2
        ),
    }