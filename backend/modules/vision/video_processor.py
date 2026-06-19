import os
import cv2
import time
from typing import List, Dict, Any
from modules.agent.agent import procesar_frame

def procesar_video(
    video_path: str, 
    fps_deseados: float = 1.0, 
    vehiculo_id: str = "CAM-001",
    temp_dir: str = "temp_frames"
) -> List[Dict[str, Any]]:
    """
    Procesa un archivo de video aplicando el pipeline secuencial (YOLOv8 + GPT-4o) 
    a intervalos de tiempo inteligentes (Muestreo Temporal).
    
    Args:
        video_path (str): Ruta local al archivo de video (.mp4, .avi, etc.).
        fps_deseados (float): Cuántos frames analizar por segundo de video. 
                              Ej: 1.0 significa 1 frame por segundo. 
                              Ej: 0.5 significa 1 frame cada 2 segundos.
        vehiculo_id (str): Identificador único del vehículo comercial.
        temp_dir (str): Carpeta temporal para almacenar los frames extraídos.
        
    Returns:
        List[Dict[str, Any]]: Lista de diccionarios con el análisis completo de cada frame muestreado.
    """
    start_time = time.time()
    print(f"\n COPILOTO 360 — Iniciando Procesamiento de Video")
    print(f"    Archivo: {os.path.basename(video_path)}")
    print(f"    Vehículo ID: {vehiculo_id}")
    print(f"    Frecuencia de muestreo: {fps_deseados} frame(s) por segundo")
    
    # Validar existencia del video
    if not os.path.exists(video_path):
        print(f"❌ Error: El archivo de video no existe en la ruta '{video_path}'")
        return []

    # Inicializar captura de video con OpenCV
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Error: No se pudo abrir el archivo de video. Formato corrupto o códec incompatible.")
        return []

    # Extraer metadatos nativos del video
    fps_original = cap.get(cv2.CAP_PROP_FPS)
    total_frames_video = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duracion_segundos = total_frames_video / fps_original
    
    # Calcular el salto de frames requerido basado en los FPS deseados
    # Ej: Si el video va a 30 FPS y queremos 1 FPS, procesamos un frame cada 30 frames.
    intervalo_frames = max(1, int(fps_original / fps_deseados))
    
    print(f"   📊 Info Video: {fps_original:.2f} FPS Originales | Duración: {duracion_segundos:.2f}s | Total Frames: {total_frames_video}")
    print(f"   ⚙️ Estrategia: Analizando 1 frame cada {intervalo_frames} frames reales.")

    resultados = []
    frame_actual_index = 0
    frames_procesados_count = 0
    
    # Asegurar la creación del directorio temporal para los frames extraídos
    os.makedirs(temp_dir, exist_ok=True)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break  # Fin del video o error de lectura

            # Verificar si corresponde procesar este frame específico por la tasa de muestreo
            if frame_actual_index % intervalo_frames == 0:
                frames_procesados_count += 1
                timestamp_segundos = round(frame_actual_index / fps_original, 2)
                
                # Generar nombre único para el frame en el disco
                nombre_frame = f"frame_{vehiculo_id}_t{timestamp_segundos:.2f}_f{frame_actual_index}.jpg"
                temp_filepath = os.path.join(temp_dir, nombre_frame)
                
                # Guardar frame temporalmente en formato JPEG de alta calidad
                cv2.imwrite(temp_filepath, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                
                print(f"\n🎞️ [Frame {frames_procesados_count}] Procesando segundo: {timestamp_segundos}s (Frame #{frame_actual_index})")
                
                # Ejecutar tu pipeline secuencial (YOLO + GPT-4o + Alert Engine) que ya tienes implementado
                resultado_frame = procesar_frame(temp_filepath, vehiculo_id)
                
                # Inyectar metadatos temporales críticos para el Frontend y el modulo Dataset (FiftyOne)
                resultado_frame["timestamp_segundos"] = timestamp_segundos
                resultado_frame["frame_index"] = frame_actual_index
                resultado_frame["video_origen"] = os.path.basename(video_path)
                
                resultados.append(resultado_frame)
                
                # Optimización de almacenamiento: Eliminar frame de inmediato tras ser procesado
                if os.path.exists(temp_filepath):
                    try:
                        os.remove(temp_filepath)
                    except Exception as e:
                        print(f"⚠️ No se pudo remover el archivo temporal {temp_filepath}: {e}")

            frame_actual_index += 1

    except Exception as e:
        print(f"❌ Error crítico interrumpiendo el procesamiento del video: {e}")
    finally:
        # Liberar recursos de hardware del lector de video de OpenCV
        cap.release()
        
        # Limpieza defensiva de la carpeta temporal si quedó vacía
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            try:
                os.rmdir(temp_dir)
            except:
                pass

    # Resumen analítico final en consola (Ideal para el log del sistema)
    tiempo_total_ejecucion = time.time() - start_time
    niveles_alerta = [r["alerta"]["nivel"] for r in resultados]
    
    print(f"\n🎉 Agente Finalizó Video — {frames_procesados_count} frames analizados en {tiempo_total_ejecucion:.2f}s")
    print(f"   🚨 Resumen de Alertas Detectadas:")
    print(f"      🔴 Crítico: {niveles_alerta.count('critico')}")
    print(f"      🟠 Alto:    {niveles_alerta.count('alto')}")
    print(f"      🟡 Medio:   {niveles_alerta.count('medio')}")
    print(f"      🟢 Bajo:    {niveles_alerta.count('bajo')}")
    
    return resultados