import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'tu-ne-sauras-jamais'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     f"mysql://root:@localhost:3306/first_flask_app"
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")