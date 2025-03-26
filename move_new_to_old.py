from app import app, db
from app.models import BeeImage, NewBeeImage

def merge_images():
    with app.app_context():
        new_images = NewBeeImage.query.all()
        added = 0
        for new in new_images:
            exists = BeeImage.query.filter_by(image_name=new.image_name).first()
            if not exists:
                bee = BeeImage(
                    image_name=new.image_name,
                    image_data=new.image_data,
                    has_varroa=new.has_varroa
                )
                db.session.add(bee)
                added += 1
            db.session.delete(new)

        db.session.commit()
        print(f"✅ {added} images ajoutées à BeeImage et supprimées de NewBeeImage.")

if __name__ == "__main__":
    merge_images()
