"""
COPILOTO 360 — FastAPI Server
modules/api/server.py

Punto de entrada del servidor. Configura FastAPI, CORS, y registra todos los routers.
Ejecutar con: uvicorn modules.api.server:app --host 0.0.0.0 --port 8000 --reload
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from modules.api.routes.alerts import router as alerts_router
from modules.api.routes.vehicles import router as vehicles_router
from modules.api.routes.reports import router as reports_router
from modules.api.routes.agent import router as agent_router
from modules.api.routes.agent_upload import router as agent_upload_router

# ACOPLAMIENTO CON EL PAQUETE DE DATASET (HEILING)
try:
    from modules.dataset import inicializar_fiftyone
    DATASET_DISPONIBLE = True
except ImportError:
    DATASET_DISPONIBLE = False

load_dotenv()


# ── MANEJO DE CICLO DE VIDA (LIFESPAN) ──────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Controla los eventos de encendido y apagado del servidor.
    Inicializa de forma segura la base de datos distribuida antes de aceptar peticiones.
    """
    if DATASET_DISPONIBLE:
        print("[SISTEMA-API] Inicializando base de datos local de FiftyOne...")
        try:
            inicializar_fiftyone()
            print("[SISTEMA-API] Base de datos sincronizada y lista.")
        except Exception as e:
            print(f"AVISO CRITICO: No se pudo levantar el servicio de FiftyOne en el servidor: {e}")
    else:
        print("[AVISO-API] Modulo 'modules.dataset' no detectado. El servidor correra sin persistencia.")
        
    yield
    print("[SISTEMA-API] Cerrando recursos del servidor.")


# ── Inicialización de la app con ciclo de vida ──────────────────────────────
app = FastAPI(
    title="Copiloto 360 API",
    description="API de monitoreo inteligente de conductores — YOLO + GPT-4o",
    version="1.0.0",
    lifespan=lifespan
)


# ── CONTROLADOR DE EXCEPCIONES GLOBAL (Manejo defensivo) ───────────────────
@app.exception_handler(Exception)
async def manejador_excepciones_global(request: Request, exc: Exception):
    """
    Captura fallos inesperados en el pipeline de ejecucion para evitar
    caidas del servidor y entregar respuestas estandarizadas al Frontend.
    """
    print(f"ERROR SERVIDOR: Fallo en peticion {request.url.path} — Detalle: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "mensaje": "Ocurrio un fallo interno en el servidor de procesamiento.",
            "detalle": str(exc)
        }
    )


# ── CORS ────────────────────────────────────────────────────────────────────
# Lee los orígenes permitidos desde .env  (ej: http://localhost:5173)
origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
allowed_origins = [o.strip() for o in origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(alerts_router,   prefix="/alerts",   tags=["Alertas"])
app.include_router(vehicles_router, prefix="/vehicles", tags=["Vehículos"])
app.include_router(reports_router,  prefix="/reports",  tags=["Reportes"])
app.include_router(agent_router,    prefix="/agent",    tags=["Agente"])
app.include_router(agent_upload_router, prefix="/agent", tags=["Agente Upload"])


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Copiloto 360 API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}

# Agrega este import junto a los otros
from modules.api.routes.voice import router as voice_router

# Agrega esta línea junto a los otros app.include_router(...)
app.include_router(voice_router, prefix="/voice", tags=["Voz"])