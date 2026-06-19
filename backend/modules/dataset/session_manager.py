import fiftyone as fo

def inicializar_fiftyone():
    """Configura los parametros globales de la base de datos de FiftyOne."""

    pass

def obtener_o_crear_dataset(vehiculo_id: str) -> fo.Dataset:
    """Garantiza la existencia de un espacio aislado en BD por cada vehiculo."""
    nombre_dataset = f"Copiloto360_{vehiculo_id.replace('-', '_')}"
    
    if nombre_dataset in fo.list_datasets():
        return fo.load_dataset(nombre_dataset)
        
    dataset = fo.Dataset(nombre_dataset)
    dataset.persistent = True
    return dataset