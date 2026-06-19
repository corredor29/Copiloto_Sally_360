"""
COPILOTO 360 — Ruta de Voz (Text-to-Speech)
modules/api/routes/voice.py

Convierte texto o alertas a audio usando OpenAI TTS (tts-1).
El frontend recibe el audio directamente como stream MP3 y lo reproduce.

Endpoints:
  POST /voice/speak         → Convierte cualquier texto a voz y devuelve el audio
  POST /voice/alert         → Lee en voz alta una alerta estructurada del sistema
  GET  /voice/voices        → Lista las voces disponibles
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI

router = APIRouter()

# Cliente OpenAI (usa la OPENAI_API_KEY del .env automáticamente)
client = OpenAI()

# Voces disponibles en OpenAI TTS
VOCES_DISPONIBLES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# Voz por defecto para alertas del copiloto (nova suena clara y natural)
VOZ_DEFAULT = "nova"

# Mapa de nivel → prefijo de urgencia que se leerá en voz
PREFIJOS_ALERTA = {
    "critico": "¡Alerta crítica! ",
    "alto":    "Alerta alta. ",
    "medio":   "Atención. ",
    "bajo":    "",
}


# ── Modelos ───────────────────────────────────────────────────────────────────

class SpeakRequest(BaseModel):
    texto: str
    voz: Optional[str] = VOZ_DEFAULT        # alloy | echo | fable | onyx | nova | shimmer
    velocidad: Optional[float] = 1.0        # 0.25 a 4.0


class AlertSpeakRequest(BaseModel):
    nivel: str                              # critico | alto | medio | bajo
    mensaje: str
    detalle: Optional[str] = None           # Detalle adicional del conductor o vía
    voz: Optional[str] = VOZ_DEFAULT


# ── Helper ────────────────────────────────────────────────────────────────────

def _generar_audio(texto: str, voz: str, velocidad: float) -> bytes:
    """Llama a OpenAI TTS y devuelve los bytes del audio MP3."""

    if voz not in VOCES_DISPONIBLES:
        raise HTTPException(
            status_code=422,
            detail=f"Voz '{voz}' no válida. Opciones: {VOCES_DISPONIBLES}"
        )

    if not (0.25 <= velocidad <= 4.0):
        raise HTTPException(
            status_code=422,
            detail="La velocidad debe estar entre 0.25 y 4.0"
        )

    if not texto.strip():
        raise HTTPException(status_code=422, detail="El texto no puede estar vacío.")

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voz,
            input=texto,
            speed=velocidad,
            response_format="mp3",
        )
        return response.content

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error al generar audio con OpenAI TTS: {str(e)}"
        )


def _stream_audio(audio_bytes: bytes) -> StreamingResponse:
    """Envuelve los bytes en un StreamingResponse MP3 listo para el navegador."""
    return StreamingResponse(
        content=iter([audio_bytes]),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=copiloto_voz.mp3",
            "Content-Length": str(len(audio_bytes)),
            "Cache-Control": "no-cache",
        },
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/speak", summary="Convertir cualquier texto a voz")
def speak(body: SpeakRequest):
    """
    Recibe un texto libre y devuelve el audio MP3 generado por OpenAI TTS.

    El frontend puede usarlo para leer cualquier contenido en pantalla:
    nombres de vehículos, estadísticas, mensajes del sistema, etc.

    Ejemplo de uso desde el frontend:
        const res = await fetch('/voice/speak', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto: 'Sistema iniciado correctamente.' })
        });
        const blob = await res.blob();
        const audio = new Audio(URL.createObjectURL(blob));
        audio.play();
    """
    audio = _generar_audio(
        texto=body.texto,
        voz=body.voz or VOZ_DEFAULT,
        velocidad=body.velocidad or 1.0,
    )
    return _stream_audio(audio)


@router.post("/alert", summary="Leer una alerta del sistema en voz alta")
def speak_alert(body: AlertSpeakRequest):
    """
    Recibe una alerta estructurada (nivel + mensaje + detalle opcional)
    y genera el audio MP3 con el tono y urgencia apropiados.

    El prefijo de urgencia se agrega automáticamente según el nivel:
      - critico → '¡Alerta crítica! ...'
      - alto    → 'Alerta alta. ...'
      - medio   → 'Atención. ...'
      - bajo    → (sin prefijo)

    Usado por AlertCard.jsx cuando el usuario pulsa el botón de audio
    o cuando el panel detecta una alerta crítica nueva.
    """
    nivel = body.nivel.lower().strip()
    prefijo = PREFIJOS_ALERTA.get(nivel, "")

    # Construir el texto completo que se leerá
    texto_completo = prefijo + body.mensaje
    if body.detalle:
        texto_completo += f". {body.detalle}"

    audio = _generar_audio(
        texto=texto_completo,
        voz=body.voz or VOZ_DEFAULT,
        velocidad=1.0 if nivel not in ["critico", "alto"] else 1.1,
    )
    return _stream_audio(audio)


@router.get("/voices", summary="Listar voces disponibles")
def get_voices():
    """
    Devuelve las voces disponibles de OpenAI TTS.
    El frontend puede usarlas para un selector de voz en configuración.
    """
    return {
        "voz_default": VOZ_DEFAULT,
        "voces": [
            {"id": "alloy",   "descripcion": "Neutral y equilibrada"},
            {"id": "echo",    "descripcion": "Masculina y directa"},
            {"id": "fable",   "descripcion": "Expresiva y cálida"},
            {"id": "onyx",    "descripcion": "Grave y autoritaria"},
            {"id": "nova",    "descripcion": "Clara y natural (recomendada para alertas)"},
            {"id": "shimmer", "descripcion": "Suave y femenina"},
        ],
    }