import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from modules.agent.prompts import PROMPT_CONDUCTOR
from modules.vision.response_parser import parsear_respuesta

load_dotenv()
# Inicializamos el cliente validando que la API key exista
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analizar_conductor(filepath: str, contexto_yolo: dict = None) -> dict:
    """
    Analiza al conductor usando GPT-4o con salida JSON garantizada.
    Si YOLO ya detectó objetos, se los pasamos como contexto extra al final del prompt.
    """
    try:
        # Leer imagen y convertir a base64
        with open(filepath, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        # Detectar tipo de imagen de forma dinámica
        ext = filepath.lower().split(".")[-1]
        mime = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
        }.get(ext, "image/jpeg")

        # Acoplamos el contexto de YOLO si contiene detecciones
        prompt_final = PROMPT_CONDUCTOR
        if contexto_yolo and contexto_yolo.get("clases"):
            clases = ", ".join(contexto_yolo["clases"])
            prompt_final += f"\n\n[CONTEXTO DETECTOR SENSOR]: YOLO ya detectó estos objetos en la imagen actual: {clases}"

        # Realizar la llamada a GPT-4o
        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=400,  # Aumentado a 400 para evitar que el JSON se corte por la mitad
            response_format={"type": "json_object"},  # 👈 OBLIGA a GPT-4o a retornar JSON válido
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_final},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"}
                    }
                ]
            }]
        )

        # Extraer el contenido de la respuesta
        texto = resp.choices[0].message.content
        
        # Parsear y validar la estructura JSON
        resultado = parsear_respuesta(texto, "conductor")
        resultado["tokens"] = resp.usage.total_tokens
        return resultado

    except Exception as e:
        print(f"⚠️ Error en vlm_conductor: {e}")
        return {
            "estado": "normal",
            "detalle": f"Error en procesamiento VLM: {str(e)[:50]}",
            "confianza": 0.0,
            "objetos_detectados": [],
            "tokens": 0,
            "error": str(e),
        }