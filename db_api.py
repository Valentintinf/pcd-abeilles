from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import BeeImage, NewBeeImage, User
import os
import uvicorn
import base64
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI app
app = FastAPI()

# Pydantic Schemas
class BeeImageSchema(BaseModel):
    filename: str
    label: str
    data: str  # Base64 encoded image data

    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    username: str
    email: str
    password: str

class LoginSchema(BaseModel):
    username: str
    password: str

# --- Endpoints ---

@app.get("/images/", response_model=list[BeeImageSchema])
def list_validated_images():
    session = SessionLocal()
    images = session.query(BeeImage).all()
    session.close()
    return [
        BeeImageSchema(
            filename=img.image_name,
            label=str(img.has_varroa),
            data=base64.b64encode(img.image_data).decode('utf-8')
        ) for img in images
    ]

@app.get("/images/{image_id}", response_model=BeeImageSchema)
def get_validated_image(image_id: int):
    session = SessionLocal()
    image = session.query(BeeImage).filter(BeeImage.id == image_id).first()
    session.close()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return BeeImageSchema(
        filename=image.image_name,
        label=str(image.has_varroa),
        data=base64.b64encode(image.image_data).decode('utf-8')
    )

@app.get("/images/pending/", response_model=list[BeeImageSchema])
def list_pending_images():
    session = SessionLocal()
    images = session.query(NewBeeImage).all()
    session.close()
    return [
        BeeImageSchema(
            filename=img.image_name,
            label=str(img.has_varroa),
            data=base64.b64encode(img.image_data).decode('utf-8')
        ) for img in images
    ]

@app.get("/images/pending/{image_id}", response_model=BeeImageSchema)
def get_pending_image(image_id: int):
    session = SessionLocal()
    image = session.query(NewBeeImage).filter(NewBeeImage.id == image_id).first()
    session.close()
    if image is None:
        raise HTTPException(status_code=404, detail="Pending image not found")
    return BeeImageSchema(
        filename=image.image_name,
        label=str(image.has_varroa),
        data=base64.b64encode(image.image_data).decode('utf-8')
    )

@app.post("/images/")
def add_validated_image(image: BeeImageSchema):
    session = SessionLocal()
    new_img = BeeImage(
        image_name=image.filename,
        has_varroa=image.label.lower() == "true",
        image_data=base64.b64decode(image.data)
    )
    session.add(new_img)
    session.commit()
    session.close()
    return {"status": "Image added"}

@app.post("/images/pending/")
def add_pending_image(image: BeeImageSchema):
    session = SessionLocal()
    new_img = NewBeeImage(
        image_name=image.filename,
        has_varroa=image.label.lower() == "true",
        image_data=base64.b64decode(image.data)
    )
    session.add(new_img)
    session.commit()
    session.close()
    return {"status": "Pending image added"}

@app.patch("/images/pending/{image_id}")
def update_pending_image(image_id: int, update_fields: dict = Body(...)):
    session = SessionLocal()
    image = session.query(NewBeeImage).filter(NewBeeImage.id == image_id).first()
    if image is None:
        session.close()
        raise HTTPException(status_code=404, detail="Pending image not found")
    for key, value in update_fields.items():
        if hasattr(image, key):
            setattr(image, key, value)
    session.commit()
    session.close()
    return {"status": "Pending image updated"}

@app.delete("/images/{image_id}")
def delete_validated_image(image_id: int):
    session = SessionLocal()
    img = session.query(BeeImage).filter(BeeImage.id == image_id).first()
    if img is None:
        session.close()
        raise HTTPException(status_code=404, detail="Image not found")
    session.delete(img)
    session.commit()
    session.close()
    return {"status": "Image deleted"}

@app.delete("/images/pending/{image_id}")
def delete_pending_image(image_id: int):
    session = SessionLocal()
    img = session.query(NewBeeImage).filter(NewBeeImage.id == image_id).first()
    if img is None:
        session.close()
        raise HTTPException(status_code=404, detail="Pending image not found")
    session.delete(img)
    session.commit()
    session.close()
    return {"status": "Pending image deleted"}

@app.post("/users/register")
def register_user(user: UserSchema):
    session = SessionLocal()
    existing_user = session.query(User).filter(User.username == user.username).first()
    if existing_user:
        session.close()
        raise HTTPException(status_code=400, detail="Username already exists")

    password_hash = generate_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=password_hash
    )
    session.add(new_user)
    session.commit()
    session.close()
    return {"status": "User registered"}

@app.post("/users/login")
def login_user_api(user: LoginSchema):
    session = SessionLocal()
    existing_user = session.query(User).filter(User.username == user.username).first()
    session.close()
    if not existing_user or not check_password_hash(existing_user.password_hash, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {
        "status": "Login successful",
        "user": {
            "id": existing_user.id,
            "username": existing_user.username,
            "email": existing_user.email
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)