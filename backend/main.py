import os
import json
from dotenv import load_dotenv
from modules.agent.agent import procesar_frame, correr_agente
from modules.vision.video_processor import procesar_video

load_dotenv()

def verificar_entorno():
    """Verifica que la API Key esté configurada correctamente."""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: La variable 'OPENAI_API_KEY' no está configurada en el archivo .env")
        return False
    return True

def ejecutar_prueba_imagen(ruta_imagen: str):
    """Prueba el pipeline con una sola imagen."""
    print(f"\n--- Probando Pipeline con Imagen ---")
    if not os.path.exists(ruta_imagen):
        print(f"⚠️ Archivo de imagen no encontrado en: {ruta_imagen}")
        print("Por favor, coloca una imagen de prueba válida.")
        return

    resultado = procesar_frame(ruta_imagen, vehiculo_id="TEST-IMG-001")
    
    # Guardar el JSON resultante para inspección visual de la estructura
    ruta_salida = "resultado_prueba_imagen.json"
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)
    print(f"\n💾 Análisis guardado con éxito en '{ruta_salida}'")

def ejecutar_prueba_video(ruta_video: str):
    """Prueba el pipeline con un archivo de video."""
    print(f"\n--- Probando Pipeline con Video ---")
    if not os.path.exists(ruta_video):
        print(f"⚠️ Archivo de video no encontrado en: {ruta_video}")
        print("Por favor, coloca un video corto de prueba (.mp4).")
        return

    # Procesamos el video muestreando 1 frame por segundo (fps_deseados=1.0)
    resultados_video = procesar_video(
        video_path=ruta_video, 
        fps_deseados=1.0, 
        vehiculo_id="TEST-VID-001"
    )
    
    # Guardar los resultados del video entero
    ruta_salida = "resultado_prueba_video.json"
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(resultados_video, f, indent=4, ensure_ascii=False)
    print(f"\n💾 Historial de video guardado con éxito en '{ruta_salida}'")


if __name__ == "__main__":
    print("🤖 COPILOTO 360 — MÓDULO AGENTE-VISION (TEST MENU)")
    
    if verificar_entorno():
        # Crea una carpeta de test si no existe para organizar tus archivos de prueba
        os.makedirs("test_files", exist_ok=True)
        
        # 💡 Configura aquí las rutas de tus archivos de prueba locales
        IMAGEN_TEST = "test_files/conductor_prueba.jpg"
        VIDEO_TEST = "test_files/viaje_prueba.mp4"
        
        print("\nSelecciona el modo de prueba:")
        print("1. Procesar una Imagen estática")
        print("2. Procesar un Video (.mp4)")
        print("3. Salir")
        
        opcion = input("\nElige una opción (1-3): ").strip()
        
        if opcion == "1":
            ejecutar_prueba_imagen(IMAGEN_TEST)
        elif opcion == "2":
            ejecutar_prueba_video(VIDEO_TEST)
        elif opcion == "3":
            print("Saliendo del evaluador de pruebas.")
        else:
            print("Opción inválida.")