from ultralytics import YOLO
import os

# Carga el modelo una sola vez cuando se importa el módulo
# Se descarga automáticamente la primera vez
modelo = YOLO("yolov8n.pt")

# Clases que nos interesan para seguridad vial
CLASES_RELEVANTES = [
    "person",
    "car",
    "truck",
    "bus",
    "motorcycle",
    "bicycle",
    "traffic light",
    "stop sign",
    "cell phone",
    "cup",
    "bottle",
]


def detectar_objetos(filepath: str) -> dict:
    """
    Corre YOLO sobre una imagen y retorna los objetos detectados.
    Solo retorna las clases relevantes para seguridad vial.
    """
    try:
        resultados = modelo(filepath, verbose=False)
        detecciones = []

        for r in resultados:
            for box in r.boxes:
                clase = modelo.names[int(box.cls)]
                confianza = float(box.conf)

                # Solo guardamos clases relevantes con confianza > 40%
                if clase in CLASES_RELEVANTES and confianza > 0.4:
                    detecciones.append({
                        "clase": clase,
                        "confianza": round(confianza, 2),
                        "bbox": box.xyxy[0].tolist(),  # [x1, y1, x2, y2]
                    })

        return {
            "detecciones": detecciones,
            "total": len(detecciones),
            "clases": list(set(d["clase"] for d in detecciones)),
            "error": None,
        }

    except Exception as e:
        print(f"⚠️ Error en YOLO: {e}")
        return {
            "detecciones": [],
            "total": 0,
            "clases": [],
            "error": str(e),
        }