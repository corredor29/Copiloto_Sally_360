"""
COPILOTO 360 — Rutas de Reportes
modules/api/routes/reports.py

Endpoints:
  GET  /reports                → Lista todos los reportes JSON generados en disco
  POST /reports/generate       → Genera un nuevo reporte procesando un video
"""

import os
import json
import glob
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

try:
    from modules.vision.video_processor import procesar_video
    VIDEO_DISPONIBLE = True
except ImportError:
    VIDEO_DISPONIBLE = False

try:
    from modules.dataset import inicializar_fiftyone, cargar_reporte_en_fiftyone
    DATASET_DISPONIBLE = True
except ImportError:
    DATASET_DISPONIBLE = False

router = APIRouter()

# Directorio donde se guardan los reportes JSON generados
DATA_DIR = os.getenv("DATA_DIR", "./data")
os.makedirs(DATA_DIR, exist_ok=True)


# ── Modelos de Request/Response ───────────────────────────────────────────────

class GenerarReporteRequest(BaseModel):
    vehiculo_id: str
    ruta_video: str
    fps_deseados: float = 1.0


class GenerarReporteResponse(BaseModel):
    vehiculo_id: str
    ruta_salida: str
    total_frames: int
    resumen: dict
    mensaje: str


# ── Helpers ──────────────────────────────────────────────────────────────────

def _leer_reporte_json(ruta: str) -> dict:
    """Carga un reporte JSON del disco y adjunta metadata de archivo."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        stat = os.stat(ruta)
        return {
            "archivo": os.path.basename(ruta),
            "ruta": ruta,
            "tamaño_bytes": stat.st_size,
            "generado_en": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "vehiculo_id": data.get("vehiculo_id", "desconocido"),
            "total_frames": len(data.get("frames", [])),
            "resumen": data.get("resumen_alertas", {}),
        }
    except Exception as e:
        return {"archivo": os.path.basename(ruta), "error": str(e)}


def _calcular_resumen(reporte: dict) -> dict:
    """Calcula el conteo de alertas por nivel a partir del reporte completo."""
    frames = reporte.get("frames", [])
    resumen = {"critico": 0, "alto": 0, "medio": 0, "bajo": 0}
    for frame in frames:
        nivel = frame.get("alerta", {}).get("nivel", "bajo")
        if nivel in resumen:
            resumen[nivel] += 1
    return resumen


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", summary="Listar todos los reportes generados")
def get_reports():
    """
    Escanea el DATA_DIR y devuelve la lista de reportes JSON disponibles.
    El frontend usa esto para el ReportsPanel.jsx.
    """
    patrones = [
        os.path.join(DATA_DIR, "reporte_video_*.json"),
        os.path.join(DATA_DIR, "resultado_prueba_*.json"),
        # Busca también en la raíz del backend por compatibilidad
        "reporte_video_*.json",
        "resultado_prueba_*.json",
    ]

    archivos = set()
    for patron in patrones:
        archivos.update(glob.glob(patron))

    reportes = [_leer_reporte_json(ruta) for ruta in sorted(archivos, reverse=True)]

    return {
        "total": len(reportes),
        "reportes": reportes,
    }


@router.post("/generate", summary="Generar un nuevo reporte procesando un video")
def generate_report(body: GenerarReporteRequest, background_tasks: BackgroundTasks):
    """
    Lanza el pipeline de video (1 frame/segundo por defecto) y guarda el reporte JSON.
    Si el módulo de FiftyOne está disponible, también ingesta los datos en la BD.

    El proceso puede tardar varios minutos según la duración del video.
    """
    if not VIDEO_DISPONIBLE:
        raise HTTPException(
            status_code=503,
            detail="El módulo de visión (video_processor) no está disponible."
        )

    vehiculo_id = body.vehiculo_id.upper()
    ruta_video = body.ruta_video

    if not os.path.exists(ruta_video):
        raise HTTPException(
            status_code=404,
            detail=f"Archivo de video no encontrado en: {ruta_video}"
        )

    # Procesar el video de forma síncrona (el cliente puede esperar o usar background_tasks)
    try:
        reporte_final = procesar_video(
            video_path=ruta_video,
            fps_deseados=body.fps_deseados,
            vehiculo_id=vehiculo_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando video: {str(e)}")

    # Calcular resumen de alertas
    resumen = _calcular_resumen(reporte_final)
    reporte_final["resumen_alertas"] = resumen

    # Guardar JSON en disco
    nombre_archivo = f"reporte_video_{vehiculo_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    ruta_salida = os.path.join(DATA_DIR, nombre_archivo)

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(reporte_final, f, indent=4, ensure_ascii=False)

    # Ingestar en FiftyOne si está disponible (en background para no bloquear)
    if DATASET_DISPONIBLE:
        def _ingestar():
            try:
                cargar_reporte_en_fiftyone(reporte_final, ruta_permanente_video=ruta_video)
            except Exception:
                pass  # El reporte JSON ya fue guardado, la ingesta es adicional

        background_tasks.add_task(_ingestar)

    return GenerarReporteResponse(
        vehiculo_id=vehiculo_id,
        ruta_salida=ruta_salida,
        total_frames=len(reporte_final.get("frames", [])),
        resumen=resumen,
        mensaje=f"Reporte generado exitosamente para {vehiculo_id}.",
    )