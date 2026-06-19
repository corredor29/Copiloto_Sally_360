import json

def _convertir_a_float_seguro(valor) -> float:
    """Convierte un valor a float de manera segura sin romper la ejecución."""
    try:
        return round(float(valor), 2)
    except (ValueError, TypeError):
        return 0.0

def parsear_respuesta(texto: str, tipo: str) -> dict:
    """
    Parsea, limpia y valida de forma estricta la respuesta JSON de GPT-4o.
    Si el modelo no responde bien o el JSON es inválido, retorna un dict 
    seguro por defecto para mantener la estabilidad del sistema.
    
    tipo: "conductor" | "via"
    """
    # Guardamos una copia del texto original para los logs de error antes de transformar
    texto_original = texto
    
    try:
        if not texto:
            raise ValueError("El texto recibido de la API de OpenAI está vacío.")

        # 1. Limpieza exhaustiva del formato Markdown y espacios en blanco extremos
        texto = texto.strip()
        texto = texto.replace("```json", "").replace("```", "").strip()
        
        # Eliminar posibles anomalías o caracteres invisibles al inicio/fin del string
        if texto.startswith("`") or texto.endswith("`"):
            texto = texto.strip("`").strip()

        # 2. Parsear el JSON corregido
        resultado = json.loads(texto)

        # 3. Estructuración y tipado seguro para el análisis del CONDUCTOR
        if tipo == "conductor":
            # Asegurar que objetos_detectados sea una lista válida
            objetos = resultado.get("objetos_detectados", [])
            if not isinstance(objetos, list):
                objetos = [str(objetos)] if objetos else []

            return {
                "estado": str(resultado.get("estado", "normal")).lower().strip(),
                "detalle": str(resultado.get("detalle", "Sin detalle")),
                "confianza": _convertir_a_float_seguro(resultado.get("confianza", 0.0)),
                "objetos_detectados": objetos,
                "error": None,
            }

        # 4. Estructuración y tipado seguro para el análisis de la VÍA
        if tipo == "via":
            # Asegurar que riesgos sea una lista válida
            riesgos = resultado.get("riesgos", [])
            if not isinstance(riesgos, list):
                riesgos = [str(riesgos)] if riesgos else []

            return {
                "estado": str(resultado.get("estado", "normal")).lower().strip(),
                "detalle": str(resultado.get("detalle", "Sin detalle")),
                "confianza": _convertir_a_float_seguro(resultado.get("confianza", 0.0)),
                "riesgos": riesgos,
                "error": None,
            }
            
        raise ValueError(f"Tipo de análisis desconocido: '{tipo}'")

    except Exception as e:
        # Registro detallado del error en la consola del servidor (clave para debugging)
        print(f"⚠️ Error crítico parseando respuesta de GPT-4o ({tipo}): {e}")
        print(f"   Fragmento del payload original recibido: {repr(texto_original[:120])}")

        # Retornos de contingencia idénticos a los tuyos para no alterar la firma de datos
        if tipo == "conductor":
            return {
                "estado": "normal",
                "detalle": f"Error de parseo sintáctico: {str(e)[:40]}",
                "confianza": 0.0,
                "objetos_detectados": [],
                "error": str(e),
            }

        return {
            "estado": "normal",
            "detalle": f"Error de parseo sintáctico: {str(e)[:40]}",
            "confianza": 0.0,
            "riesgos": [],
            "error": str(e),
        }