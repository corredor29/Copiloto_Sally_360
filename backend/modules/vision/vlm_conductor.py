import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from modules.agent.prompts import PROMPT_CONDUCTOR
from modules.vision.response_parser import parsear_respuesta

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analizar_conductor(filepath: str, contexto_yolo: dict = None) -> dict:
    """
    Analiza al conductor usando GPT-4o.
    Si YOLO ya detectó objetos, se los pasamos como contexto extra.
    """
    try:
        # Leer imagen y convertir a base64
        with open(filepath, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        # Detectar tipo de imagen
        ext = filepath.lower().split(".")[-1]
        mime = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
        }.get(ext, "image/jpeg")

        prompt_final = PROMPT_CONDUCTOR
        if contexto_yolo and contexto_yolo["clases"]:
            clases = ", ".join(contexto_yolo["clases"])
            prompt_final += f"\n\nNota: YOLO ya detectó estos objetos en la imagen: {clases}"

        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=200,
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

        texto = resp.choices[0].message.content
        resultado = parsear_respuesta(texto, "conductor")
        resultado["tokens"] = resp.usage.total_tokens
        return resultado

    except Exception as e:
        print(f"⚠️ Error en vlm_conductor: {e}")
        return {
            "estado": "normal",
            "detalle": f"Error: {str(e)[:50]}",
            "confianza": 0.0,
            "objetos_detectados": [],
            "tokens": 0,
            "error": str(e),
        }