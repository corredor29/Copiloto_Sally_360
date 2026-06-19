import pyttsx3
import threading

def _hablar_en_hilo(mensaje: str):
    """Ejecuta el motor de voz en un hilo separado para no congelar el pipeline de IA."""
    try:
        engine = pyttsx3.init()
        
        # Ajustar la velocidad (un poco más rápido para alertas inmediatas)
        engine.setProperty('rate', 180)
        
        # Configurar el idioma a español
        voices = engine.getProperty('voices')
        for voice in voices:
            if "spanish" in voice.name.lower() or "es-" in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
                
        engine.say(mensaje)
        engine.runAndWait()
    except Exception as e:
        print(f"AVISO: No se pudo reproducir el audio: {e}")

def emitir_asistente_voz(mensaje: str):
    """
    Lanza el asistente de voz sin detener la ejecucion del programa principal.
    Esto evita que el video se congele mientras la voz habla.
    """
    hilo = threading.Thread(target=_hablar_en_hilo, args=(mensaje,))
    hilo.daemon = True
    hilo.start()