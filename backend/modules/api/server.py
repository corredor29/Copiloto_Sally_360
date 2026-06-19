"""
COPILOTO 360 — FastAPI Server
modules/api/server.py

Punto de entrada del servidor. Configura FastAPI, CORS, y registra todos los routers.
Ejecutar con: uvicorn modules.api.server:app --host 0.0.0.0 --port 8000 --reload
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from modules.api.routes.alerts import router as alerts_router
from modules.api.routes.vehicles import router as vehicles_router
from modules.api.routes.reports import router as reports_router
from modules.api.routes.agent import router as agent_router

load_dotenv()

# ── Inicialización de la app ────────────────────────────────────────────────
app = FastAPI(
    title="Copiloto 360 API",
    description="API de monitoreo inteligente de conductores — YOLO + GPT-4o",
    version="1.0.0",
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


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Copiloto 360 API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}