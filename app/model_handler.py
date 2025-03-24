import os
import numpy as np
import tensorflow as tf
from PIL import Image
from app import app
from IA_model.images_modifications import image_modification

# Load the model once
MODEL_PATH = os.path.join("IA_model","models", "best_bright.h5")
model = tf.keras.models.load_model(MODEL_PATH)

def prepare_image(filepath):
    # Open the image and convert to RGB
    img = Image.open(filepath).convert("RGB")
    img = np.asarray(img)

    # Use your image_modification class
    mod = image_modification([img])
    mod = mod.resize((50, 54)).normalize()  # Match model expected input: (54, 50, 3)
    processed_img = mod.images

    return processed_img

def predict_image(filepath):
    img = prepare_image(filepath)
    predictions = model.predict(img)
    predicted_class = int(np.argmax(predictions, axis=1)[0])
    confidence = float(np.max(predictions))
    return {"class": predicted_class, "confidence": confidence}
