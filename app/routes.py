from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.utils import allowed_file
from app.model_handler import predict_image
import requests
import io
import uuid
import base64
from flask import send_file
from app.api_db_handler import (
    get_validated_image, get_pending_image,
    list_validated_images, list_pending_images,
    delete_validated_image, delete_pending_image,
    update_pending_image
)
from app.api_db_handler import login_user_api, register_user_api


@app.route("/image/<int:image_id>")
@login_required
def get_image(image_id):
    bee = get_validated_image(image_id)
    if bee is None:
        abort(404)
    image_data = base64.b64decode(bee["data"])
    return send_file(io.BytesIO(image_data), mimetype="image/png")

@app.route("/new-image/<int:image_id>")
@login_required
def get_new_image(image_id):
    bee = get_pending_image(image_id)
    if bee is None:
        abort(404)
    image_data = base64.b64decode(bee["data"])
    return send_file(io.BytesIO(image_data), mimetype="image/png")

@app.route("/bee-gallery")
@login_required
def bee_gallery():
    bees = list_validated_images()
    return render_template("gallery.html", bees=bees)

@app.route("/new-bee-gallery")
@login_required
def new_bee_gallery():
    new_bees = list_pending_images()
    return render_template("new_gallery.html", bees=new_bees)

@app.route("/validate-images")
@login_required
def validate_images():
    images = list_pending_images()
    return render_template("validate.html", images=[img for img in images if not img.get("is_validated", False)])

@app.route("/validate-image/<int:image_id>", methods=["POST"])
@login_required
def validate_image(image_id):
    has_varroa = request.args.get("has_varroa") == "1"
    success = update_pending_image(image_id, {
        "is_validated": True,
        "validated_has_varroa": has_varroa
    })
    if success:
        flash("Image validée avec succès !", "success")
    else:
        flash("Erreur lors de la validation de l'image", "error")
    return redirect(url_for("validate_images"))

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(url_for('index'))

        file = request.files['file']
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(url_for('index'))

        if file and allowed_file(file.filename):
            unique_id = uuid.uuid4().hex
            filename = f"{unique_id}_{secure_filename(file.filename)}"
            file_bytes = file.read()

            try:
                response = requests.post(
                    'http://localhost:8000/predict',
                    files={'file': (filename, file_bytes, file.content_type)}
                )
                if response.status_code == 200:
                    result = response.json()
                    image_base64 = base64.b64encode(file_bytes).decode("utf-8")
                    requests.post('http://localhost:8001/images/pending/', json={
                        "filename": filename,
                        "label": str(result.get("class")),
                        "data": image_base64
                    })
                    return render_template('result.html', filename=filename, result=result)
                else:
                    flash('Erreur de prédiction : ' + response.json().get('detail', 'Erreur inconnue'), 'error')
            except Exception as e:
                flash(f"Erreur lors de l'appel à l'API : {str(e)}", 'error')
            return redirect(url_for('index'))

        flash("Format non autorisé", 'error')
        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/')
def root():
    return redirect(url_for('index'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user_data = login_user_api(form.username.data, form.password.data)
        if user_data:
            user = User(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"]
            )
            login_user(user)
            flash('success: You are now logged in!')
            return redirect(url_for('index'))
        else:
            flash('error: Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html', title='Sign In', form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        success = register_user_api(form.username.data, form.email.data, form.password.data)
        if success:
            # Auto-login après register
            user = User(username=form.username.data)
            login_user(user)
            flash('success: Congratulations, you are now registered!')
            return redirect(url_for('index'))
        else:
            flash('error: Username already exists!')
            return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('success: You are now logged out!')
    return redirect(url_for("login"))
