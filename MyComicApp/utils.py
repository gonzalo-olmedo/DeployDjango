# MyComicApp/utils.py
import os
import uuid

def generate_public_id(instance, filename):
    # Obtener el nombre base y la extensión
    name, ext = os.path.splitext(filename)
    
    # Reemplazar espacios y caracteres especiales
    name = name.replace(' ', '_').replace('-', '_').lower()
    
    # Generar un UUID para asegurar unicidad
    unique_id = uuid.uuid4().hex
    
    # Combinar el nombre y el UUID, agregando la extensión original
    public_id = f"planetsuperheroes/images/productos/{name}_{unique_id}{ext}"  # Añadir la ruta de la carpeta deseada
    
    return public_id