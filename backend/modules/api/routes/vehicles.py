"""
COPILOTO 360 — Rutas de Vehículos
modules/api/routes/vehicles.py

Endpoints:
  GET  /vehicles          → Lista de todos los vehículos activos con su estado actual
  GET  /vehicles/{id}     → Detalle completo + historial de un vehículo específico
"""

from fastapi import APIRouter, HTTPException

try:
    from modules.dataset.session_manager import obtener_o_crear_dataset
    import fiftyone as fo
    DATASET_DISPONIBLE = True
except ImportError:
    DATASET_DISPONIBLE = False

router = APIRouter()


def _listar_vehiculo_ids() -> list[str]:
    """Extrae los IDs de vehículos a partir de los datasets registrados en FiftyOne."""
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


def _estado_actual(vehiculo_id: str) -> dict:
    """
    Inspecciona el último frame del dataset para obtener el estado más reciente
    del conductor y la vía. Se usa para pintar el semáforo en el VehicleCard.
    """
    if not DATASET_DISPONIBLE:
        return {"nivel": "desconocido", "conductor": "desconocido", "via": "desconocido"}

    try:
        dataset = obtener_o_crear_dataset(vehiculo_id)

        if dataset.count() == 0:
            return {"nivel": "sin_datos", "conductor": "sin_datos", "via": "sin_datos"}

        # Último sample ingresado
        ultimo_sample = dataset.last()
        frames = list(ultimo_sample.frames.values())

        if not frames:
            return {"nivel": "sin_datos", "conductor": "sin_datos", "via": "sin_datos"}

        ultimo_frame = frames[-1]

        nivel = getattr(ultimo_frame.get_field("alerta_nivel"), "label", "bajo")
        conductor = getattr(ultimo_frame.get_field("conductor_estado"), "label", "normal")
        via = getattr(ultimo_frame.get_field("via_estado"), "label", "normal")

        return {"nivel": nivel, "conductor": conductor, "via": via}

    except Exception as e:
        return {"nivel": "error", "conductor": "error", "via": str(e)}


def _historial_completo(vehiculo_id: str) -> list[dict]:
    """
    Construye el historial completo frame a frame del vehículo.
    Usado por VehicleDetail.jsx para mostrar la línea de tiempo.
    """
    if not DATASET_DISPONIBLE:
        return []

    try:
        dataset = obtener_o_crear_dataset(vehiculo_id)
        historial = []

        for sample in dataset:
            for frame_num, frame in sample.frames.items():
                historial.append({
                    "frame": frame_num,
                    "filepath": sample.filepath,
                    "nivel": getattr(frame.get_field("alerta_nivel"), "label", "bajo"),
                    "mensaje": getattr(frame.get_field("alerta_mensaje"), "label", ""),
                    "conductor_estado": getattr(frame.get_field("conductor_estado"), "label", "normal"),
                    "conductor_detalle": getattr(frame.get_field("conductor_detalle"), "label", ""),
                    "via_estado": getattr(frame.get_field("via_estado"), "label", "normal"),
                    "via_detalle": getattr(frame.get_field("via_detalle"), "label", ""),
                })

        return historial

    except Exception as e:
        return [{"error": str(e)}]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", summary="Listar todos los vehículos activos con su estado")
def get_vehicles():
    """
    Retorna todos los vehículos registrados en la flota con su estado actual
    (nivel de alerta más reciente, estado del conductor, estado de la vía).
    Alimenta el VehiclesGrid del frontend.
    """
    ids = _listar_vehiculo_ids()

    vehiculos = []
    for vid in ids:
        estado = _estado_actual(vid)
        vehiculos.append({
            "vehiculo_id": vid,
            "estado_actual": estado,
        })

    return {
        "total": len(vehiculos),
        "vehiculos": vehiculos,
    }


@router.get("/{vehiculo_id}", summary="Detalle completo de un vehículo")
def get_vehicle_by_id(vehiculo_id: str):
    """
    Retorna el estado actual + historial completo de frames de un vehículo.
    Usado por VehicleDetail.jsx para mostrar la línea de tiempo del conductor.
    """
    vid = vehiculo_id.upper()

    ids_existentes = _listar_vehiculo_ids()
    if vid not in ids_existentes:
        raise HTTPException(
            status_code=404,
            detail=f"Vehículo '{vid}' no encontrado en la base de datos."
        )

    estado = _estado_actual(vid)
    historial = _historial_completo(vid)

    resumen = {
        "critico": sum(1 for h in historial if h.get("nivel") == "critico"),
        "alto":    sum(1 for h in historial if h.get("nivel") == "alto"),
        "medio":   sum(1 for h in historial if h.get("nivel") == "medio"),
        "bajo":    sum(1 for h in historial if h.get("nivel") == "bajo"),
    }

    return {
        "vehiculo_id": vid,
        "estado_actual": estado,
        "resumen_alertas": resumen,
        "total_frames": len(historial),
        "historial": historial,
    }