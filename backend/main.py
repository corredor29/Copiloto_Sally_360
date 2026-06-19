import os
import json
from dotenv import load_dotenv
from modules.agent.agent import procesar_frame
from modules.vision.video_processor import procesar_video

try:
    from modules.dataset import inicializar_fiftyone, cargar_reporte_en_fiftyone
    DATASET_DISPONIBLE = True
except ImportError:
    DATASET_DISPONIBLE = False

load_dotenv()


def verificar_entorno() -> bool:
    """Verifica de forma defensiva que la API Key de OpenAI esté configurada en el entorno."""
    if not os.getenv("OPENAI_API_KEY"):
        print("\nERROR: La variable 'OPENAI_API_KEY' no está configurada en el archivo .env")
        print("Por favor, crea un archivo .env en la raíz con: OPENAI_API_KEY=tu_clave_aqui")
        return False
    return True


def ejecutar_prueba_imagen(ruta_imagen: str, vehiculo_id: str):
    """
    Prueba el pipeline secuencial completo (YOLOv8 + GPT-4o) con una sola imagen estática.
    """
    print(f"\n--- Probando Pipeline con Imagen Estática ---")
    print(f"Ruta objetivo: {ruta_imagen}")
    print(f"Asociando al Vehículo: {vehiculo_id}")
    
    if not os.path.exists(ruta_imagen):
        print(f"Archivo de imagen no encontrado en: {ruta_imagen}")
        print(f"Asegúrate de colocar una foto de prueba válida dentro de la carpeta 'test_files/'.")
        return

    # Corre el pipeline individual pasándole el carro correspondiente
    resultado = procesar_frame(ruta_imagen, vehiculo_id=vehiculo_id)
    
    # Guardar el JSON resultante de forma estructurada para inspección del equipo
    ruta_salida = f"resultado_prueba_{vehiculo_id}.json"
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)
        
    print(f"\n[EXITO] Análisis del frame guardado con éxito en: '{ruta_salida}'")


def ejecutar_prueba_video(ruta_video: str, vehiculo_id: str):
    """
    Prueba el pipeline de video aplicando muestreo temporal inteligente (1 frame por segundo)
    y empaquetando el reporte global para la base de datos distribuida de FiftyOne.
    """
    print(f"\n--- Probando Pipeline con Archivo de Video ---")
    print(f"Ruta objetivo: {ruta_video}")
    print(f"Asociando al Vehículo: {vehiculo_id}")
    
    if not os.path.exists(ruta_video):
        print(f"Archivo de video no encontrado en: {ruta_video}")
        print(f"Por favor, coloca un video corto de prueba (.mp4) en 'test_files/viaje_prueba.mp4'.")
        return

    # Procesamos el video muestreando 1 frame por segundo (fps_deseados=1.0)
    # La versión de 'procesar_video' devuelve el dict 'reporte_final'
    reporte_final = procesar_video(
        video_path=ruta_video, 
        fps_deseados=1.0, 
        vehiculo_id=vehiculo_id
    )
    
    # Guardar el JSON empaquetado del carro
    ruta_salida = f"reporte_video_{vehiculo_id}.json"
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(reporte_final, f, indent=4, ensure_ascii=False)
        
    print(f"\n[EXITO] Historial global del vehículo guardado con éxito en: '{ruta_salida}'")

    # ACOPLAMIENTO DE PRUEBA: Si el modulo de Heiling esta listo, guarda en FiftyOne
    if DATASET_DISPONIBLE:
        print(f"\n[INTEGRACION] Enviando reporte final al motor de ingesta de FiftyOne...")
        try:
            cargar_reporte_en_fiftyone(reporte_final, ruta_permanente_video=ruta_video)
            print("[EXITO INTEGRACION] Datos cargados correctamente en la base de datos.")
        except Exception as e:
            print(f"AVISO: Fallo la insercion automatica en FiftyOne: {e}")
    else:
        print(f"\n[AVISO] El modulo 'modules.dataset' no fue detectado o esta incompleto.")
        print("Los datos solo se guardaron en el archivo JSON local.")


if __name__ == "__main__":
    print("==========================================================")
    print("COPILOTO 360 — MODULO AGENTE-VISION (ENTORNO DE PRUEBAS)")
    print("==========================================================")
    
    if verificar_entorno():
        # INICIALIZACION DE BASE DE DATOS: Prepara FiftyOne antes de interactuar con el menu
        if DATASET_DISPONIBLE:
            print("[SISTEMA] Inicializando base de datos local de FiftyOne...")
            try:
                inicializar_fiftyone()
            except Exception as e:
                print(f"AVISO: No se pudo levantar el servicio de FiftyOne: {e}")
        
        os.makedirs("test_files", exist_ok=True)
        
        IMAGEN_TEST = "test_files/conductor_prueba.jpg"
        VIDEO_TEST = "test_files/viaje_prueba.mp4"
        
        print("\nMenú de Selección de Modos:")
        print("  1. Intentar procesar una Imagen estática")
        print("  2. Intentar procesar un Video (.mp4) con aislamiento temporal")
        print("  3. Salir del evaluador")
        
        opcion = input("\nElige una opción (1-3): ").strip()
        
        if opcion in ["1", "2"]:
            # Pedimos el ID dinámicamente para simular el comportamiento del sistema multi-carro
            id_ingresado = input("Ingrese el ID del vehículo a simular (Ej: CAM-001, BUS-005): ").strip().upper()
            vehiculo_id = id_ingresado if id_ingresado else "CARRO-GENERICO"
            
            if opcion == "1":
                ejecutar_prueba_imagen(IMAGEN_TEST, vehiculo_id)
            elif opcion == "2":
                ejecutar_prueba_video(VIDEO_TEST, vehiculo_id)
                
        elif opcion == "3":
            print("\nCerrando el entorno de pruebas del agente. Módulo listo para producción.")
        else:
            print("\nOpción inválida. Ejecute el script de nuevo para reintentar.")