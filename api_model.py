from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import uvicorn
import os
import io
from IA_model.images_modifications import image_modification
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI()
instrumentator = Instrumentator().instrument(app).expose(app)


MODEL_PATH = os.path.join("IA_model", "models", "retrained_model.h5")
model = load_model(MODEL_PATH)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        img_array = np.asarray(image)

        mod = image_modification([img_array])
        mod = mod.resize((50, 54)).normalize()
        processed_img = mod.images

        predictions = model.predict(processed_img)
        predicted_class = int(np.argmax(predictions, axis=1)[0])
        confidence = float(np.max(predictions))

        return JSONResponse(content={"class": predicted_class, "confidence": confidence})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)