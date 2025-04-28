import numpy as np
from PIL import Image
import io
import os
from sklearn.model_selection import train_test_split
from tensorflow import keras
from app import app, db
from app.models import BeeImage
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report
from IA_model.images_modifications import image_modification



MODEL_PATH = "IA_model/models/retrained_model.h5"

def load_images():
    with app.app_context():
        data = BeeImage.query.all()
        X, y = [], []
        for entry in data:
            img = Image.open(io.BytesIO(entry.image_data)).convert("RGB")
            img = np.array(img)

            transformer = image_modification([img])
            processed_img = transformer.transform()

            X.append(processed_img[0])  # car transform() retourne une liste/array
            y.append(1 if entry.has_varroa else 0)
        return np.array(X), np.array(y)

def train_model():
    X, y = load_images()
    if len(X) == 0:
        print("⚠️ Aucune image disponible pour l'entraînement.")
        return

    X = X.astype("float32") / 255.0
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train)
    class_weights = dict(enumerate(class_weights))

    if os.path.exists(MODEL_PATH):
        print("📂 Chargement du modèle existant")
        model = keras.models.load_model(MODEL_PATH)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['binary_accuracy'])
    else:
        print("✨ Création d'un nouveau modèle")
        model = keras.models.Sequential([
            keras.layers.Input(shape=(54, 50, 3)),
            keras.layers.Conv2D(32, (3,3), activation='relu'),
            keras.layers.MaxPooling2D(),
            keras.layers.Flatten(),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['binary_accuracy'])

    model.fit(X_train, y_train, epochs=10, validation_data=(X_val, y_val), class_weight=class_weights)
    model.save(MODEL_PATH)
    print("✅ Modèle entraîné et sauvegardé sous retrained_model.h5")
    # Évaluation sur validation
    y_pred = (model.predict(X_val) > 0.5).astype("int32")
    print("\n📊 Rapport de classification sur le jeu de validation :")
    print(classification_report(y_val, y_pred, target_names=["Pas Varroa", "Varroa"]))


if __name__ == "__main__":
    train_model()
