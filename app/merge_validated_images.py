from app import app, db
from app.models import BeeImage, NewBeeImage

def merge_validated_images():
    with app.app_context():
        validated = NewBeeImage.query.filter_by(is_validated=True).all()
        added = 0

        for item in validated:
            if item.validated_has_varroa is None:
                continue  # sécurité : on ne copie pas les images sans label validé

            exists = BeeImage.query.filter_by(image_name=item.image_name).first()
            if not exists:
                bee = BeeImage(
                    image_name=item.image_name,
                    image_data=item.image_data,
                    has_varroa=item.validated_has_varroa
                )
                db.session.add(bee)
                added += 1

            db.session.delete(item)

        db.session.commit()
        print(f"✅ {added} images validées fusionnées dans BeeImage.")

if __name__ == "__main__":
    merge_validated_images()
