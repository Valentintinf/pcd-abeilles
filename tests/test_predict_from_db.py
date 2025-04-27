import requests
import base64
import random

# 1. Récupère toutes les images validées
response = requests.get("http://localhost:8001/images/")
response.raise_for_status()
images = response.json()

# 2. Prend une image random
img = random.choice(images)

# 3. Décode le base64
img_bytes = base64.b64decode(img["data"])

# 4. Sauvegarde temporaire
temp_filename = "tests/temp_test_img.png"
with open(temp_filename, "wb") as f:
    f.write(img_bytes)

# 5. Envoie à l'API Model /predict
files = {'file': open(temp_filename, 'rb')}
predict_response = requests.post("http://localhost:8000/predict", files=files)
predict_response.raise_for_status()

# 6. Analyse de la réponse
result = predict_response.json()
print("Prediction result:", result)

# 7. Vérification minimale
assert "prediction" in result, "No 'prediction' key in response!"
assert "confidence" in result, "No 'confidence' key in response!"

# 8. Affiche pour information
expected_label = img["label"]
predicted_label = result["prediction"]

print(f"✅ Expected label: {expected_label}")
print(f"✅ Predicted label: {predicted_label}")
print(f"✅ Confidence: {result['confidence']}")

# (Pas d'assertion stricte sur le match pour l'instant)