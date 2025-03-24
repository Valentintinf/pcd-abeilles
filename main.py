from app import app
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

if __name__ == '__main__':
    app.run(debug=True)
