import os
import uuid
import cloudinary.uploader
from django.db import models
from cloudinary.models import CloudinaryField

def generate_public_id(instance, filename):
    name, ext = os.path.splitext(filename)
    name = name.replace(' ', '_').replace('-', '_').lower()

    unique_id = str(uuid.uuid4())
    public_id = f"planetsuperheroes/images/productos/{name}_{unique_id}{ext}"

    return public_id