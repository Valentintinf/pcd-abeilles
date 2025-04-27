import requests
import base64
import random
import os

# 1. Récupère toutes les images validées depuis db_api
response = requests.get("http://localhost:8001/images/")
response.raise_for_status()
images = response.json()

# 2. Vérifie s'il y a au moins 1 image
if not images:
    raise Exception("❌ No images available in DB to test!")

# 3. Prend une image random
img = random.choice(images)

# 4. Décode l'image base64
img_bytes = base64.b64decode(img["data"])

# 5. Sauvegarde temporaire
temp_dir = os.path.dirname(__file__)
temp_filename = os.path.join(temp_dir, "temp_test_img.png")

with open(temp_filename, "wb") as f:
    f.write(img_bytes)

# 6. Envoie à l'API Model /predict
with open(temp_filename, 'rb') as f:
    files = {'file': f}
    predict_response = requests.post("http://localhost:8000/predict", files=files)
    predict_response.raise_for_status()

# 7. Analyse de la réponse
result = predict_response.json()
print("\nPrediction result:", result)

# 8. Vérifications minimales
assert "prediction" in result, "No 'prediction' key in response!"
assert "confidence" in result, "No 'confidence' key in response!"

# 9. Affiche pour information
expected_label = img["label"]
predicted_label = result["prediction"]

print(f"✅ Expected label: {expected_label}")
print(f"✅ Predicted label: {predicted_label}")
print(f"✅ Confidence: {result['confidence']}")

# 10. Clean up: Supprime l'image temporaire
os.remove(temp_filename)
print(f"✅ Temporary test image '{temp_filename}' deleted.")