from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.utils import allowed_file
from app.model_handler import predict_image


@app.route('/', methods=['GET', 'POST'])
def root():
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
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
        get_user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
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
        print("🔄 Form submitted")

        if 'file' not in request.files:
            print("❌ No file in request.files")
            flash('error: Aucun fichier sélectionné')
            return redirect(url_for('index'))

        file = request.files['file']
        print("📎 Filename received:", file.filename)

        if file.filename == '':
            print("❌ Empty filename")
            flash('error: Aucun fichier sélectionné')
            return redirect(url_for('index'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print("✅ Allowed file:", filename)

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            print("📁 Will save to:", filepath)

            file.save(filepath)
            print("💾 File saved!")

            result = predict_image(filepath)
            print("🧠 Prediction:", result)

            return render_template('result.html', filename=filename, result=result)

        print("❌ File not allowed:", file.filename)
        flash("error: Format non autorisé")
        return redirect(url_for('index'))


    return render_template('index.html')