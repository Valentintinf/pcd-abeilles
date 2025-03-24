import os
from dotenv import load_dotenv

load_dotenv()

# Convert string set to actual Python set
allowed_extensions = eval(os.getenv('ALLOWED_EXTENSIONS', '{}'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
