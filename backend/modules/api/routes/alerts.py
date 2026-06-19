"""
COPILOTO 360 — Rutas de Alertas
modules/api/routes/alerts.py

Endpoints:
  GET  /alerts              → Todas las alertas de toda la flota (o filtradas por vehículo)
  GET  /alerts/criticas     → Solo alertas de nivel "critico"
  GET  /alerts/{vehiculo_id}→ Historial de alertas de un vehículo específico
"""

from fastapi import APIRouter, Query
from typing import Optional

try:
    from modules.dataset.query_service import (
        obtener_alertas_por_vehiculo,
        obtener_resumen_global,
    )
    from modules.dataset.session_manager import obtener_o_crear_dataset
    import fiftyone as fo
    DATASET_DISPONIBLE = True
except ImportError:
    DATASET_DISPONIBLE = False

router = APIRouter()


def _extraer_alertas_de_dataset(vehiculo_id: str) -> list[dict]:
    """
    Recorre el dataset FiftyOne del vehículo y extrae las alertas frame a frame.
    Devuelve una lista de dicts planos listos para serializar en JSON.
    """
    if not DATASET_DISPONIBLE:
        return []

    try:
        dataset = obtener_o_crear_dataset(vehiculo_id)
        alertas = []

        for sample in dataset:
            for frame_num, frame in sample.frames.items():
                nivel = getattr(frame.get_field("alerta_nivel"), "label", None)
                if nivel is None:
                    continue

                alertas.append({
                    "vehiculo_id": vehiculo_id,
                    "frame": frame_num,
                    "filepath": sample.filepath,
                    "nivel": nivel,
                    "mensaje": getattr(frame.get_field("alerta_mensaje"), "label", ""),
                    "conductor_estado": getattr(frame.get_field("conductor_estado"), "label", "normal"),
                    "conductor_detalle": getattr(frame.get_field("conductor_detalle"), "label", ""),
                    "via_estado": getattr(frame.get_field("via_estado"), "label", "normal"),
                    "via_detalle": getattr(frame.get_field("via_detalle"), "label", ""),
                })

        return alertas

    except Exception as e:
        return [{"error": str(e)}]


def _todos_los_vehiculos() -> list[str]:
    """Retorna todos los IDs de vehículos registrados en la base de datos."""
    if not DATASET_DISPONIBLE:
        return []
    try:
        prefijo = "Copiloto360_"
        return [
            nombre.replace(prefijo, "").replace("_", "-")
            for nombre in fo.list_datasets()
            if nombre.startswith(prefijo)
        ]
    except Exception:
        return []


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/", summary="Listar todas las alertas de la flota")
def get_all_alerts(
    vehiculo_id: Optional[str] = Query(None, description="Filtrar por ID de vehículo"),
    nivel: Optional[str] = Query(None, description="Filtrar por nivel: critico, alto, medio, bajo"),
):
    """
    Devuelve todas las alertas registradas en la flota.
    Opcionalmente filtra por vehículo y/o nivel de alerta.
    """
    if vehiculo_id:
        vehiculos = [vehiculo_id.upper()]
    else:
        vehiculos = _todos_los_vehiculos()

    todas = []
    for vid in vehiculos:
        todas.extend(_extraer_alertas_de_dataset(vid))

    if nivel:
        todas = [a for a in todas if a.get("nivel") == nivel.lower()]

    return {
        "total": len(todas),
        "alertas": todas,
    }


@router.get("/criticas", summary="Listar solo alertas críticas de la flota")
def get_critical_alerts():
    """
    Acceso rápido a todas las alertas de nivel 'critico' en toda la flota.
    Usado por el panel de alertas del frontend para el badge rojo urgente.
    """
    vehiculos = _todos_los_vehiculos()
    criticas = []

    for vid in vehiculos:
        alertas_vid = _extraer_alertas_de_dataset(vid)
        criticas.extend([a for a in alertas_vid if a.get("nivel") == "critico"])

    return {
        "total": len(criticas),
        "alertas": criticas,
    }


@router.get("/{vehiculo_id}", summary="Historial de alertas de un vehículo")
def get_alerts_by_vehicle(vehiculo_id: str):
    """
    Retorna el historial completo de alertas de un vehículo específico.
    Permite al frontend construir la línea de tiempo del conductor.
    """
    vid = vehiculo_id.upper()
    alertas = _extraer_alertas_de_dataset(vid)

    resumen = {
        "critico": sum(1 for a in alertas if a.get("nivel") == "critico"),
        "alto":    sum(1 for a in alertas if a.get("nivel") == "alto"),
        "medio":   sum(1 for a in alertas if a.get("nivel") == "medio"),
        "bajo":    sum(1 for a in alertas if a.get("nivel") == "bajo"),
    }

    return {
        "vehiculo_id": vid,
        "total": len(alertas),
        "resumen": resumen,
        "alertas": alertas,
    }