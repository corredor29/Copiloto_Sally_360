from .session_manager import obtener_o_crear_dataset

def obtener_alertas_por_vehiculo(vehiculo_id: str) -> list:
    """Filtra y extrae el historial de alertas del vehiculo para la API."""
    dataset = obtener_o_crear_dataset(vehiculo_id)
    resultados = []
    return resultados

def obtener_resumen_global() -> dict:
    """Genera metricas globales cruzando todos los datasets de la flota."""
    # Retorna totales de alertas criticas, altas, etc.
    return {}