
import os
import threading
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

try:
    from modules.vision.video_processor import procesar_video
    VIDEO_DISPONIBLE = True
except ImportError:
    VIDEO_DISPONIBLE = False

router = APIRouter()

# ── Estado por vehículo (en memoria, suficiente para demo) ───────────────────
# Estructura: { vehiculo_id: { estado, progreso, nivel, mensaje, resultado } }
_estados: dict[str, dict] = {}
_lock = threading.Lock()

UPLOAD_DIR = os.getenv("DATA_DIR", "./data") + "/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _set_estado(vid: str, **kwargs):
    with _lock:
        if vid not in _estados:
            _estados[vid] = {}
        _estados[vid].update(kwargs)


def _procesar_en_background(video_path: str, vehiculo_id: str, fps: float):
    """Corre el pipeline de video en un hilo secundario y actualiza el estado en vivo."""
    try:
        _set_estado(vehiculo_id,
            estado="procesando",
            progreso=0,
            nivel=None,
            mensaje="Analizando video frame a frame...",
            iniciado_en=datetime.now().isoformat(),
            resultado=None,
        )

        if not VIDEO_DISPONIBLE:
            # Modo demo: simular resultado si el módulo de visión no está disponible
            import time, random
            niveles = ["bajo", "bajo", "medio", "bajo", "critico", "bajo", "alto"]
            for i, n in enumerate(niveles):
                time.sleep(0.4)
                _set_estado(vehiculo_id, progreso=int((i + 1) / len(niveles) * 100), nivel=n)

            resultado_demo = {
                "vehiculo_id": vehiculo_id,
                "total_frames_procesados": len(niveles),
                "metricas_globales": {
                    "critico": niveles.count("critico"),
                    "alto": niveles.count("alto"),
                    "medio": niveles.count("medio"),
                    "bajo": niveles.count("bajo"),
                },
                "frames": [
                    {"frame_index": i, "alerta": {"nivel": n, "mensaje": f"Frame {i+1} analizado"}}
                    for i, n in enumerate(niveles)
                ],
                "modo": "demo",
            }
            nivel_final = max(
                resultado_demo["metricas_globales"],
                key=lambda k: {"critico": 3, "alto": 2, "medio": 1, "bajo": 0}[k]
            ) if any(resultado_demo["metricas_globales"].values()) else "bajo"

            _set_estado(vehiculo_id,
                estado="completado",
                progreso=100,
                nivel=nivel_final,
                mensaje="Análisis completo (modo demo — backend IA no disponible).",
                resultado=resultado_demo,
                completado_en=datetime.now().isoformat(),
            )
            return

        # Pipeline real: procesar_video actualiza frames internamente
        # Hacemos monkey-patch del print para capturar progreso aproximado
        reporte = procesar_video(
            video_path=video_path,
            fps_deseados=fps,
            vehiculo_id=vehiculo_id,
        )

        # Calcular nivel dominante
        metricas = reporte.get("metricas_globales", {})
        prioridad = {"critico": 3, "alto": 2, "medio": 1, "bajo": 0}
        nivel_final = max(metricas, key=lambda k: prioridad.get(k, 0)) if metricas else "bajo"

        _set_estado(vehiculo_id,
            estado="completado",
            progreso=100,
            nivel=nivel_final,
            mensaje=f"Análisis completado — {reporte.get('total_frames_procesados', 0)} frames procesados.",
            resultado=reporte,
            completado_en=datetime.now().isoformat(),
        )

    except Exception as e:
        _set_estado(vehiculo_id,
            estado="error",
            mensaje=str(e),
            nivel=None,
            progreso=0,
        )
    finally:
        # Limpiar el archivo temporal subido
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
        except Exception:
            pass


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/upload-video", summary="Subir video y analizar en tiempo real")
async def upload_video(
    background_tasks: BackgroundTasks,
    vehiculo_id: str = Form(...),
    fps_deseados: float = Form(1.0),
    video: UploadFile = File(...),
):
    """
    Recibe un video desde el frontend (multipart/form-data), lo guarda en disco
    y lanza el pipeline YOLO + GPT-4o en background.

    El frontend debe hacer polling a GET /agent/status/{vehiculo_id} para
    obtener el progreso y el resultado en tiempo real.
    """
    # Validar tipo de archivo
    ext = os.path.splitext(video.filename or "")[-1].lower()
    if ext not in (".mp4", ".avi", ".mov", ".mkv", ".webm"):
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{ext}' no soportado. Usa MP4, AVI, MOV, MKV o WEBM."
        )

    vid = vehiculo_id.upper()

    # Verificar que no haya ya un proceso corriendo para este vehículo
    with _lock:
        estado_actual = _estados.get(vid, {})
    if estado_actual.get("estado") == "procesando":
        raise HTTPException(
            status_code=409,
            detail=f"Ya hay un análisis en curso para {vid}. Espera a que termine."
        )

    # Guardar el archivo con nombre único
    nombre_unico = f"{vid}_{uuid.uuid4().hex[:8]}{ext}"
    ruta_video = os.path.join(UPLOAD_DIR, nombre_unico)

    contents = await video.read()
    with open(ruta_video, "wb") as f:
        f.write(contents)

    # Marcar inicio inmediatamente
    _set_estado(vid,
        estado="iniciando",
        progreso=0,
        nivel=None,
        mensaje="Video recibido. Iniciando pipeline...",
        iniciado_en=datetime.now().isoformat(),
        resultado=None,
        video_nombre=video.filename,
        fps_solicitados=fps_deseados,
    )

    # Lanzar en background
    background_tasks.add_task(_procesar_en_background, ruta_video, vid, fps_deseados)

    return {
        "ok": True,
        "vehiculo_id": vid,
        "video_guardado": nombre_unico,
        "mensaje": "Video recibido. Procesamiento iniciado en background.",
    }


@router.get("/status/{vehiculo_id}", summary="Estado de análisis de un vehículo")
def get_vehicle_status(vehiculo_id: str):
    """
    Devuelve el estado actual del análisis del vehículo:
    - estado: 'idle' | 'iniciando' | 'procesando' | 'completado' | 'error'
    - progreso: 0-100
    - nivel: 'bajo' | 'medio' | 'alto' | 'critico' | null
    - resultado: el reporte completo cuando estado == 'completado'
    """
    vid = vehiculo_id.upper()
    with _lock:
        estado = dict(_estados.get(vid, {}))

    if not estado:
        return {
            "vehiculo_id": vid,
            "estado": "idle",
            "progreso": 0,
            "nivel": None,
            "mensaje": "Sin análisis previo. Sube un video para comenzar.",
            "resultado": None,
        }

    return {"vehiculo_id": vid, **estado}
