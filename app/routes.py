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
import requests
from flask import send_file
import io
from app.models import BeeImage, NewBeeImage



@app.route("/image/<int:image_id>")
def get_image(image_id):
    bee = BeeImage.query.get_or_404(image_id)
    return send_file(io.BytesIO(bee.image_data), mimetype='image/png')

@app.route("/bee-gallery")
def bee_gallery():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    filter_val = request.args.get('filter', 'all')

    query = BeeImage.query
    if filter_val == 'yes':
        query = query.filter_by(has_varroa=True)
    elif filter_val == 'no':
        query = query.filter_by(has_varroa=False)

    pagination = query.paginate(page=page, per_page=per_page)
    return render_template("gallery.html", bees=pagination.items, pagination=pagination)

@app.route("/new-bee-gallery")
def new_bee_gallery():
    new_bees = NewBeeImage.query.all()
    return render_template("new_gallery.html", bees=new_bees)


@app.route("/add-to-new-images/<int:image_id>", methods=["POST"])
def add_to_new_images(image_id):
    bee = BeeImage.query.get_or_404(image_id)

    # Prevent duplicates
    existing = NewBeeImage.query.filter_by(image_name=bee.image_name).first()
    if existing:
        flash("Cette image est déjà dans les nouvelles images.", "warning")
        return redirect(url_for("bee_gallery"))

    new_bee = NewBeeImage(
        image_name=bee.image_name,
        image_data=bee.image_data,
        has_varroa=bee.has_varroa
    )
    db.session.add(new_bee)
    db.session.commit()

    flash("Image ajoutée au dataset pour entraînement.", "success")
    return redirect(url_for("bee_gallery"))

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
            flash('Aucun fichier sélectionné', 'error')
            return redirect(url_for('index'))

        file = request.files['file']
        print("📎 Filename received:", file.filename)

        if file.filename == '':
            print("❌ Empty filename")
            flash('Aucun fichier sélectionné', 'error')
            return redirect(url_for('index'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_bytes = file.read()
            print("💾 File loaded in memory")

            try:
                response = requests.post(
                    'http://localhost:8000/predict',
                    files={'file': (filename, file_bytes, file.content_type)}
                )
                print("🌐 Sent to FastAPI")

                if response.status_code == 200:
                    result = response.json()
                    print("🧠 Prediction:", result)

                    # Store in NewBeeImage
                    new_image = NewBeeImage(
                        image_name=filename,
                        image_data=file_bytes,
                        has_varroa=bool(result.get("class") == 1)
                    )
                    db.session.add(new_image)
                    db.session.commit()

                    return render_template('result.html', filename=filename, result=result)
                else:
                    print("❌ FastAPI error:", response.text)
                    flash('Erreur de prédiction : ' + response.json().get('detail', 'Erreur inconnue'), 'error')
            except Exception as e:
                print("🚨 Exception in FastAPI call:", str(e))
                flash(f"Erreur lors de l'appel à l'API : {str(e)}", 'error')

            return redirect(url_for('index'))

        print("❌ File not allowed:", file.filename)
        flash("Format non autorisé", 'error')
        return redirect(url_for('index'))

    return render_template('index.html')


    return render_template('index.html')