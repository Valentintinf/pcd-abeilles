import io
import os

from app import app
import pandas as pd
# import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for, request
# from flask_login import current_user, login_user
# from flask_login import logout_user, login_required
# from sqlalchemy import desc
from werkzeug.utils import secure_filename
# import cv2
from app.utils import allowed_file


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Aucun fichier sélectionné'
        file = request.files['file']
        if file.filename == '':
            return 'Aucun fichier sélectionné'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Appel du modèle pour la détection
            output_path = os.path.join("static", filename)
            # annotated_image = your_model_script.detect_varroa(filepath)  # Fonction à implémenter dans ton fichier modèle
            # cv2.imwrite(output_path, annotated_image)
                
            return render_template('result.html', filename=filename)
    return render_template('index.html')