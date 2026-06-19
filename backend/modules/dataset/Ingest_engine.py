import fiftyone as fo
from .session_manager import obtener_o_crear_dataset

def cargar_reporte_en_fiftyone(reporte_json: dict, ruta_permanente_video: str):
    """
    Toma el reporte generado por el pipeline de IA e ingesta los metadatos
    en la linea de tiempo del video en FiftyOne.
    """
    vehiculo_id = reporte_json["vehiculo_id"]
    dataset = obtener_o_crear_dataset(vehiculo_id)
    
    # Crear una muestra base asociada al video real persistido en disco
    sample = fo.Sample(filepath=ruta_permanente_video)
    
    # Metadatos del viaje de telemetria
    sample["vehiculo_id"] = vehiculo_id
    sample["video_origen"] = reporte_json["video_origen"]
    sample["tiempo_procesamiento_segundos"] = reporte_json["tiempo_procesamiento_segundos"]
    
    frames_fiftyone = {}
    
    # Recorrer la lista de frames que procesaste
    for f_data in reporte_json["frames"]:
        frame_index = f_data["frame_index"]
        
        # Crear objeto de almacenamiento temporal de FiftyOne
        frame_fo = fo.Frame()
        
        # Mapear tus clasificaciones estructuradas
        frame_fo["alerta_nivel"] = fo.Classification(label=f_data["alerta"]["nivel"])
        frame_fo["alerta_mensaje"] = fo.Classification(label=f_data["alerta"]["mensaje"])
        frame_fo["conductor_estado"] = fo.Classification(label=f_data["conductor"]["estado"])
        frame_fo["conductor_detalle"] = fo.Classification(label=f_data["conductor"]["detalle"])
        frame_fo["via_estado"] = fo.Classification(label=f_data["via"]["estado"])
        frame_fo["via_detalle"] = fo.Classification(label=f_data["via"]["detalle"])
        
        # Mapear las bboxes de YOLO que tu script ya proceso y limpio
        detecciones_yolo = []
        for det in f_data["yolo"]["detecciones"]:
            detecciones_yolo.append(
                fo.Detection(
                    label=det["clase"],
                    confidence=det["confianza"]
                )
            )
            
        if detecciones_yolo:
            frame_fo["objetos_yolo"] = fo.Detections(detections=detecciones_yolo)
            
        # Sincronizar con el indice base 1 que maneja FiftyOne para videos
        fo_idx = frame_index if frame_index > 0 else 1
        frames_fiftyone[fo_idx] = frame_fo
        
    # Fusionar la linea de tiempo e insertar en base de datos
    sample.frames.merge(frames_fiftyone)
    dataset.add_sample(sample)