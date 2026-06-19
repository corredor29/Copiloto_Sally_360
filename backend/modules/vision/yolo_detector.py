import os
from ultralytics import YOLO


modelo = YOLO("yolov8n.pt")

# Clases nativas de COCO que nos interesan para seguridad vial y fatiga
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

# Diccionario de traducción para entregar contexto limpio en español a tus prompts
TRADUCCION_CLASES = {
    "person": "peaton",
    "car": "vehiculo",
    "truck": "camion",
    "bus": "autobus",
    "motorcycle": "motocicleta",
    "bicycle": "bicicleta",
    "traffic light": "semaforo",
    "stop sign": "señal_pare",
    "cell phone": "celular",
    "cup": "taza_o_vaso",
    "bottle": "botella",
}


def detectar_objetos(filepath: str) -> dict:
    """
    Corre YOLOv8 sobre una imagen y retorna los objetos detectados.
    Filtra solo las clases relevantes para el ecosistema Copiloto 360
    y asegura que las coordenadas (BBox) sean serializables a JSON.
    """
    try:
        # Validación defensiva de la ruta antes de instanciar la predicción
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No se encontró el archivo en: {filepath}")

        resultados = modelo(filepath, verbose=False)
        detecciones = []

        for r in resultados:
            for box in r.boxes:
                clase_nativa = modelo.names[int(box.cls)]
                confianza = float(box.conf)

                # Guardamos únicamente clases útiles para la vía/conductor con confianza > 40%
                if clase_nativa in CLASES_RELEVANTES and confianza > 0.4:
                    # Mapeamos al nombre en español usando nuestro diccionario
                    clase_es = TRADUCCION_CLASES.get(clase_nativa, clase_nativa)
                    
                    # 👈 CORRECCIÓN CRÍTICA: Mover tensor a CPU antes de convertir a lista
                    bbox_lista = box.xyxy[0].cpu().tolist()
                    
                    detecciones.append({
                        "clase": clase_es,
                        "clase_original": clase_nativa,
                        "confianza": round(confianza, 2),
                        "bbox": [round(coord, 2) for coord in bbox_lista],  # Redondeamos coordenadas [x1, y1, x2, y2]
                    })

        return {
            "detecciones": detecciones,
            "total": len(detecciones),
            # Lista única de nombres de objetos detectados (lista para inyectar en el prompt)
            "clases": list(set(d["clase"] for d in detecciones)),
            "error": None,
        }

    except Exception as e:
        print(f"⚠️ Error en módulo YOLO: {e}")
        return {
            "detecciones": [],
            "total": 0,
            "clases": [],
            "error": str(e),
        }