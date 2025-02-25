import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'tu-ne-sauras-jamais'
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    DEBUG = True  # Change to False in production

    @staticmethod
    def init_app(app):
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)