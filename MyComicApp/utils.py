import os
import uuid

def generate_public_id(instance, filename):

    name, ext = os.path.splitext(filename)

    name = name.replace(' ', '_').replace('-', '_').lower()

    public_id = f"planetsuperheroes/images/productos/{name}{ext}"

    return public_id  
