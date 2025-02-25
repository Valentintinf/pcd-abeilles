# import cv2

import os
from app import app, db
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from app.models import User, UploadedImage
from app.utils import allowed_file

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("Ce nom d'utilisateur est déjà pris.", "danger")
            return redirect(url_for('register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Compte créé avec succès. Connectez-vous maintenant.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Connexion réussie !", "success")
            return redirect(url_for('upload_file'))
        else:
            flash("Identifiants invalides.", "danger")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
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

            # new_image = UploadedImage(filename=filename, filepath=filepath)
            # db.session.add(new_image)
            # db.session.commit()
            
            # Appel du modèle pour la détection
            # output_path = os.path.join("static", filename)
            # annotated_image = your_model_script.detect_varroa(filepath)  # Fonction à implémenter dans ton fichier modèle
            # cv2.imwrite(output_path, annotated_image)

            return render_template('result.html', filename=filename)
    
    # images = UploadedImage.query.order_by(UploadedImage.uploaded_at.desc()).all()
    return render_template('index.html', images=images)