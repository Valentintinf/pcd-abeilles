import os
import pandas as pd
from app import app, db
from app.models import BeeImage

def load_images_to_db():
    csv_path = os.path.join("IA_model", "data", "bee_data.csv")
    img_folder = os.path.join("IA_model", "data", "bee_imgs")
    df = pd.read_csv(csv_path)

    with app.app_context():
        for _, row in df.iterrows():
            image_path = os.path.join(img_folder, row['file'])
            if not os.path.exists(image_path):
                print(f"⚠️ Image not found: {row['file']}")
                continue

            with open(image_path, "rb") as f:
                image_data = f.read()

            has_varroa = 'varroa' in row['health'].lower()

            bee = BeeImage.query.filter_by(image_name=row['file']).first()
            if bee is None:
                bee = BeeImage(
                    id=int,
                    image_name=row['file'],
                    image_data=image_data,
                    has_varroa=has_varroa
                )
                db.session.add(bee)

        db.session.commit()
        print("✅ All images loaded into the database.")

if __name__ == "__main__":
    load_images_to_db()
