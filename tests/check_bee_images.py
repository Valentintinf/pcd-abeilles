from sqlalchemy import create_engine, inspect
import os

# Connexion à la base
db_path = os.getenv("DATABASE_URL", "sqlite:///app.db")
engine = create_engine(db_path)

# Inspecteur
inspector = inspect(engine)

# Liste des tables
tables = inspector.get_table_names()
print("Tables in DB:", tables)

# Vérifie la présence de bee_image
if "bee_image" not in tables:
    raise Exception("❌ Table 'bee_image' not found in app.db!")
else:
    print("✅ Table 'bee_image' found.")