import json


def parsear_respuesta(texto: str, tipo: str) -> dict:
    """
    Parsea y valida la respuesta de GPT-4o.
    Si el modelo no responde bien, retorna un dict seguro por defecto.
    tipo: "conductor" | "via"
    """
    try:
        texto = texto.strip()
        texto = texto.replace("```json", "").replace("```", "").strip()

        resultado = json.loads(texto)

        if tipo == "conductor":
            return {
                "estado": resultado.get("estado", "normal"),
                "detalle": resultado.get("detalle", "Sin detalle"),
                "confianza": float(resultado.get("confianza", 0.0)),
                "objetos_detectados": resultado.get("objetos_detectados", []),
                "error": None,
            }

        if tipo == "via":
            return {
                "estado": resultado.get("estado", "normal"),
                "detalle": resultado.get("detalle", "Sin detalle"),
                "confianza": float(resultado.get("confianza", 0.0)),
                "riesgos": resultado.get("riesgos", []),
                "error": None,
            }

    except Exception as e:

        print(f"⚠️ Error parseando respuesta de GPT-4o: {e}")
        print(f"   Respuesta recibida: {texto[:100]}")

        if tipo == "conductor":
            return {
                "estado": "normal",
                "detalle": "Error al procesar respuesta",
                "confianza": 0.0,
                "objetos_detectados": [],
                "error": str(e),
            }

        if tipo == "via":
            return {
                "estado": "normal",
                "detalle": "Error al procesar respuesta",
                "confianza": 0.0,
                "riesgos": [],
                "error": str(e),
            }