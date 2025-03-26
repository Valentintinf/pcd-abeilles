from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import uvicorn
import os
import io
from IA_model.images_modifications import image_modification

app = FastAPI()

MODEL_PATH = os.path.join("IA_model", "models", "best_original.h5")
model = load_model(MODEL_PATH)

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