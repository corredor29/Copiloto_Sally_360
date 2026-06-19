"""
COPILOTO 360 — Rutas del Agente
modules/api/routes/agent.py

Endpoints:
  POST /agent/run         → Corre el pipeline YOLO + GPT-4o sobre una imagen o lote
  GET  /agent/status      → Estado actual del agente (ocupado / disponible)
"""

import os
import threading
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

try:
    from modules.agent.agent import procesar_frame, correr_agente
    AGENTE_DISPONIBLE = True
except ImportError:
    AGENTE_DISPONIBLE = False

router = APIRouter()

# ── Estado global del agente (simple, en memoria) ────────────────────────────
# En producción esto podría ser Redis o una tabla en BD.
_estado_agente = {
    "ocupado": False,
    "vehiculo_id": None,
    "inicio": None,
    "frames_total": 0,
    "frames_procesados": 0,
    "ultimo_nivel": None,
    "error": None,
}
_lock = threading.Lock()


# ── Modelos Pydantic ──────────────────────────────────────────────────────────

class AgentRunRequest(BaseModel):
    vehiculo_id: str
    filepath: Optional[str] = None          # Una sola imagen
    filepaths: Optional[list[str]] = None   # Lote de imágenes


class AgentRunResponse(BaseModel):
    vehiculo_id: str
    total_procesados: int
    resultados: list[dict]
    resumen: dict


# ── Helpers ───────────────────────────────────────────────────────────────────

def _marcar_ocupado(vehiculo_id: str, total: int):
    with _lock:
        _estado_agente.update({
            "ocupado": True,
            "vehiculo_id": vehiculo_id,
            "inicio": datetime.now().isoformat(),
            "frames_total": total,
            "frames_procesados": 0,
            "ultimo_nivel": None,
            "error": None,
        })


def _marcar_libre(frames_procesados: int, ultimo_nivel: Optional[str] = None):
    with _lock:
        _estado_agente.update({
            "ocupado": False,
            "frames_procesados": frames_procesados,
            "ultimo_nivel": ultimo_nivel,
        })


def _marcar_error(mensaje: str):
    with _lock:
        _estado_agente.update({
            "ocupado": False,
            "error": mensaje,
        })


def _resumen_desde_resultados(resultados: list[dict]) -> dict:
    """Calcula la distribución de niveles de alerta del lote procesado."""
    niveles = [r.get("alerta", {}).get("nivel", "bajo") for r in resultados if "alerta" in r]
    return {
        "critico": niveles.count("critico"),
        "alto":    niveles.count("alto"),
        "medio":   niveles.count("medio"),
        "bajo":    niveles.count("bajo"),
        "total":   len(niveles),
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/run", summary="Correr el agente YOLO + GPT-4o sobre imagen(es)")
def run_agent(body: AgentRunRequest):
    """
    Ejecuta el pipeline completo de IA (YOLOv8 → GPT-4o conductor → GPT-4o vía → Alert Engine)
    sobre una imagen individual o un lote de imágenes.

    - Para una sola imagen: envía `filepath`.
    - Para un lote: envía `filepaths` (lista de rutas).
    - `vehiculo_id` identifica el vehículo (ej: CAM-001, BUS-005).
    """
    if not AGENTE_DISPONIBLE:
        raise HTTPException(
            status_code=503,
            detail="El módulo del agente no está disponible. Verifica las dependencias."
        )

    with _lock:
        if _estado_agente["ocupado"]:
            raise HTTPException(
                status_code=409,
                detail=f"El agente ya está procesando el vehículo '{_estado_agente['vehiculo_id']}'. "
                       f"Espera a que termine o consulta GET /agent/status."
            )

    vehiculo_id = body.vehiculo_id.upper()

    # Armar la lista de archivos a procesar
    if body.filepaths:
        filepaths = body.filepaths
    elif body.filepath:
        filepaths = [body.filepath]
    else:
        raise HTTPException(
            status_code=422,
            detail="Debes proveer 'filepath' (una imagen) o 'filepaths' (lista de imágenes)."
        )

    # Validar existencia de archivos antes de marcar el agente como ocupado
    faltantes = [f for f in filepaths if not os.path.exists(f)]
    if faltantes:
        raise HTTPException(
            status_code=404,
            detail=f"Archivos no encontrados: {faltantes}"
        )

    _marcar_ocupado(vehiculo_id, total=len(filepaths))

    try:
        if len(filepaths) == 1:
            resultado_unico = procesar_frame(filepaths[0], vehiculo_id=vehiculo_id)
            resultados = [resultado_unico]
        else:
            resultados = correr_agente(filepaths, vehiculo_id=vehiculo_id)

        resumen = _resumen_desde_resultados(resultados)
        ultimo_nivel = resultados[-1].get("alerta", {}).get("nivel") if resultados else None
        _marcar_libre(frames_procesados=len(resultados), ultimo_nivel=ultimo_nivel)

        return AgentRunResponse(
            vehiculo_id=vehiculo_id,
            total_procesados=len(resultados),
            resultados=resultados,
            resumen=resumen,
        )

    except Exception as e:
        _marcar_error(str(e))
        raise HTTPException(status_code=500, detail=f"Error en el pipeline del agente: {str(e)}")


@router.get("/status", summary="Consultar el estado actual del agente")
def get_agent_status():
    """
    Devuelve si el agente está ocupado o disponible, cuántos frames lleva procesados
    y cuál fue el último nivel de alerta detectado.
    Usado por AgentStatus.jsx para mostrar la barra de progreso en tiempo real.
    """
    with _lock:
        estado = dict(_estado_agente)

    # Calcular progreso porcentual si el agente está ocupado
    if estado["frames_total"] > 0:
        estado["progreso_pct"] = round(
            (estado["frames_procesados"] / estado["frames_total"]) * 100, 1
        )
    else:
        estado["progreso_pct"] = 0.0

    estado["disponible"] = not estado["ocupado"]

    return estado