import os
import cv2
import time
from typing import List, Dict, Any


def procesar_video(
    video_path: str, 
    fps_deseados: float = 1.0, 
    vehiculo_id: str = "CAM-001",
    temp_dir: str = "temp_frames"
) -> Dict[str, Any]:
    """
    Procesa un archivo de video aplicando el pipeline secuencial (YOLOv8 + GPT-4o) 
    a intervalos de tiempo inteligentes (Muestreo Temporal).
    
    Aísla las capturas en directorios por vehiculo_id para evitar colisiones en entornos multi-carro
    y retorna un reporte global estructurado.
    
    Args:
        video_path (str): Ruta local al archivo de video (.mp4, .avi, etc.).
        fps_deseados (float): Cuántos frames analizar por segundo de video. 
                              Ej: 1.0 significa 1 frame por segundo.
        vehiculo_id (str): Identificador único del vehículo comercial (determina la instancia destino).
        temp_dir (str): Carpeta raíz temporal para almacenar los frames extraídos.
        
    Returns:
        Dict[str, Any]: Reporte empaquetado del carro con métricas globales y la lista de frames detallada.
    """
    # IMPORTACION LOCAL PARA EVITAR IMPORTACION CIRCULAR INTERBLOQUEANTE
    from modules.agent.agent import procesar_frame

    start_time = time.time()
    print(f"\n[INICIO] COPILOTO 360 — Iniciando Procesamiento de Video Multi-Carro")
    print(f"    Archivo: {os.path.basename(video_path)}")
    print(f"    Vehículo ID: {vehiculo_id} (Asignando aislamiento de datos...)")
    print(f"    Frecuencia de muestreo: {fps_deseados} frame(s) por segundo")
    
    # 1. Validar existencia del video
    if not os.path.exists(video_path):
        print(f"ERROR: El archivo de video no existe en la ruta '{video_path}'")
        return {"vehiculo_id": vehiculo_id, "error": "Archivo no encontrado", "frames": []}

    # 2. Inicializar captura de video con OpenCV
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("ERROR: No se pudo abrir el archivo de video. Formato corrupto o códec incompatible.")
        return {"vehiculo_id": vehiculo_id, "error": "Error de códec o apertura", "frames": []}

    # 3. Extraer metadatos nativos del video
    fps_original = cap.get(cv2.CAP_PROP_FPS)
    total_frames_video = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duracion_segundos = total_frames_video / fps_original
    
    # Calcular el salto de frames requerido basado en los FPS deseados
    intervalo_frames = max(1, int(fps_original / fps_deseados))
    
    print(f"    Info Video: {fps_original:.2f} FPS Originales | Duración: {duracion_segundos:.2f}s | Total Frames: {total_frames_video}")
    print(f"    Estrategia: Analizando 1 frame cada {intervalo_frames} frames reales.")

    resultados_frames = []
    frame_actual_index = 0
    frames_procesados_count = 0
    
    # 4. AISLAMIENTO MULTI-CARRO: Crear subcarpeta exclusiva para este carro
    carpeta_vehiculo = os.path.join(temp_dir, vehiculo_id)
    os.makedirs(carpeta_vehiculo, exist_ok=True)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break  # Fin del video o error de lectura

            # Verificar si corresponde procesar este frame específico por la tasa de muestreo
            if frame_actual_index % intervalo_frames == 0:
                frames_procesados_count += 1
                timestamp_segundos = round(frame_actual_index / fps_original, 2)
                
                # Generar nombre único para el frame en el disco incorporando metadatos temporales
                nombre_frame = f"frame_{vehiculo_id}_t{timestamp_segundos:.2f}_f{frame_actual_index}.jpg"
                temp_filepath = os.path.join(carpeta_vehiculo, nombre_frame)
                
                # Guardar frame temporalmente en formato JPEG de alta calidad dentro de su subcarpeta aislada
                cv2.imwrite(temp_filepath, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                
                print(f"\n[Frame {frames_procesados_count}] Procesando segundo: {timestamp_segundos}s (Frame #{frame_actual_index})")
                
                # Ejecutar tu pipeline secuencial (YOLO + GPT-4o + Alert Engine)
                resultado_frame = procesar_frame(temp_filepath, vehiculo_id)
                
                # Inyectar metadatos temporales y de origen críticos para el Frontend y para Heiling (FiftyOne)
                resultado_frame["timestamp_segundos"] = timestamp_segundos
                resultado_frame["frame_index"] = frame_actual_index
                resultado_frame["video_origen"] = os.path.basename(video_path)
                
                resultados_frames.append(resultado_frame)
                
                # Optimización de almacenamiento: Eliminar frame de inmediato tras ser procesado
                if os.path.exists(temp_filepath):
                    try:
                        os.remove(temp_filepath)
                    except Exception as e:
                        print(f"AVISO: No se pudo remover el archivo temporal {temp_filepath}: {e}")

            frame_actual_index += 1

    except Exception as e:
        print(f"ERROR: Error crítico interrumpiendo el procesamiento del video: {e}")
    finally:
        # Liberar recursos de hardware del lector de video de OpenCV
        cap.release()
        
        # Limpieza defensiva: Eliminar la subcarpeta del carro si quedó vacía
        if os.path.exists(carpeta_vehiculo) and not os.listdir(carpeta_vehiculo):
            try:
                os.rmdir(carpeta_vehiculo)
            except:
                pass
        
        # Limpieza de la carpeta raíz temporal si no hay más carros ejecutando procesos
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            try:
                os.rmdir(temp_dir)
            except:
                pass

    # 5. Generar métricas y empaquetar reporte estructurado para la base de datos de FiftyOne destino
    tiempo_total_ejecucion = time.time() - start_time
    niveles_alerta = [r["alerta"]["nivel"] for r in resultados_frames if "alerta" in r]
    
    print(f"\n[FIN] Agente Finalizó Video — {frames_procesados_count} frames analizados en {tiempo_total_ejecucion:.2f}s")
    print(f"    Resumen de Alertas Detectadas para {vehiculo_id}:")
    print(f"       Crítico: {niveles_alerta.count('critico')}")
    print(f"       Alto:    {niveles_alerta.count('alto')}")
    print(f"       Medio:   {niveles_alerta.count('medio')}")
    print(f"       Bajo:    {niveles_alerta.count('bajo')}")
    
    reporte_final = {
        "vehiculo_id": vehiculo_id,
        "video_origen": os.path.basename(video_path),
        "total_frames_procesados": frames_procesados_count,
        "tiempo_procesamiento_segundos": round(tiempo_total_ejecucion, 2),
        "metricas_globales": {
            "critico": niveles_alerta.count('critico'),
            "alto": niveles_alerta.count('alto'),
            "medio": niveles_alerta.count('medio'),
            "bajo": niveles_alerta.count('bajo')
        },
        "frames": resultados_frames
    }
    
    return reporte_final