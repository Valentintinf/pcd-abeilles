import io
import os

import pandas as pd
import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user
from flask_login import logout_user, login_required
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.utils import allowed_file
# import cv2


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    print(form.password)
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('error: Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        flash('success: You are now logged in!')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        get_user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if get_user is None:

            user = User(
                username=form.username.data,
                email=form.email.data,
                )

            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash('success: Congratulations, you are now a registered!')
            return redirect(url_for('index'))
        else:
            flash('error: Username already exists!')
            return redirect(url_for('register'))
    return render_template('register.html', title='register', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('success: You are now logged out!')
    return redirect(url_for("login"))


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
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
            # output_path = os.path.join("static", filename)
            # annotated_image = your_model_script.detect_varroa(filepath)  # Fonction à implémenter dans ton fichier modèle
            # cv2.imwrite(output_path, annotated_image)
                
            return render_template('result.html', filename=filename)
    return render_template('index.html')