"""
COPILOTO 360 — Punto de entrada del servidor
main.py

Corre el backend FastAPI con:
    python main.py

La API queda disponible en:
    http://localhost:8000
    http://localhost:8000/docs   ← Swagger UI para probar endpoints
"""

import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "modules.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,          # Recarga automática al guardar cambios
        log_level="info",
    )