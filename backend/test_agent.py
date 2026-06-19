from modules.agent.agent import procesar_frame
import fiftyone.zoo as foz
import fiftyone as fo

# Descargar 3 imágenes de prueba del zoo de FiftyOne
print("⬇️ Descargando imágenes de prueba...")
dataset = foz.load_zoo_dataset("quickstart", max_samples=3)

# Tomar el filepath de la primera imagen
sample = dataset.first()
filepath = sample.filepath
print(f"📸 Imagen de prueba: {filepath}")

# Correr el agente sobre esa imagen
resultado = procesar_frame(filepath, vehiculo_id="CAM-TEST")

# Mostrar resultado
print("\n📊 Resultado completo:")
print(f"  YOLO detectó: {resultado['yolo']['clases']}")
print(f"  Conductor:    {resultado['conductor']['estado']}")
print(f"  Vía:          {resultado['via']['estado']}")
print(f"  Alerta:       {resultado['alerta']['nivel'].upper()}")
print(f"  Mensaje:      {resultado['alerta']['mensaje']}")
print(f"  Tokens usados:{resultado['tokens_total']}")