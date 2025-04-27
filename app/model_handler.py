import requests
import base64
import numpy as np
from PIL import Image
import io
from IA_model.images_modifications import image_modification

API_URL = "http://localhost:8000/predict"


def prepare_image_from_base64(base64_string):
    """
    Décode une image base64, applique image_modification et retourne un tableau prêt pour prédiction.
    """
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image_np = np.array(image)

    # Appliquer le pipeline de transformation
    processed = image_modification([image_np]) \
        .resize((54, 50)) \
        .grayscale() \
        .normalize()

    return processed.images[0]  # 1 image, preprocessée


def predict_image(base64_image):
    """
    Envoie l'image à l'API de prédiction FastAPI et retourne la classe et la confiance.
    """
    files = {'file': ('image.png', base64.b64decode(base64_image), 'image/png')}
    try:
        response = requests.post(API_URL, files=files, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur lors de l'appel à l'API de prédiction : {e}")
        return None

    result = response.json()
    return result.get("class"), result.get("confidence")