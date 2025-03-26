import numpy as np
from PIL import Image
import io
from sklearn.model_selection import train_test_split
from tensorflow import keras
from app import app, db
from app.models import NewBeeImage

def load_new_images():
    with app.app_context():
        data = NewBeeImage.query.all()
        X, y = [], []
        for entry in data:
            img = Image.open(io.BytesIO(entry.image_data)).convert("RGB")
            img = img.resize((50, 54))
            X.append(np.array(img))
            y.append(1 if entry.has_varroa else 0)
        return np.array(X), np.array(y)

def train_model():
    X, y = load_new_images()
    X = X.astype("float32") / 255.0
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    model = keras.models.Sequential([
        keras.layers.Input(shape=(54, 50, 3)),
        keras.layers.Conv2D(32, (3,3), activation='relu'),
        keras.layers.MaxPooling2D(),
        keras.layers.Flatten(),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=5, validation_data=(X_val, y_val))

    model.save("IA_model/models/retrained_model.h5")
    print("\u2705 Modèle entraîné et sauvegardé sous retrained_model.h5")

if __name__ == "__main__":
    train_model()
