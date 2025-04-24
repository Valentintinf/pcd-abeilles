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
import uuid



@app.route("/image/<int:image_id>")
@login_required
def get_image(image_id):
    bee = BeeImage.query.get_or_404(image_id)
    return send_file(io.BytesIO(bee.image_data), mimetype='image/png')


@app.route("/bee-gallery")
@login_required
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
@login_required
def new_bee_gallery():
    new_bees = NewBeeImage.query.all()
    return render_template("new_gallery.html", bees=new_bees)


@app.route("/new-image-by-name/<string:image_name>")
def get_new_image_by_name(image_name):
    bee = NewBeeImage.query.filter_by(image_name=image_name).first_or_404()
    return send_file(io.BytesIO(bee.image_data), mimetype='image/png')


@app.route("/new-image/<int:image_id>")
def get_new_image(image_id):
    bee = NewBeeImage.query.get_or_404(image_id)
    return send_file(io.BytesIO(bee.image_data), mimetype='image/png')


@app.route("/add-to-new-images/<int:image_id>", methods=["POST"])
@login_required
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


@app.route("/validate-images")
@login_required
def validate_images():
    images = NewBeeImage.query.filter_by(is_validated=False).all()
    return render_template("validate.html", images=images)


@app.route("/validate-image/<int:image_id>", methods=["POST"])
@login_required
def validate_image(image_id):
    has_varroa = request.args.get("has_varroa") == "1"
    bee = NewBeeImage.query.get_or_404(image_id)
    bee.is_validated = True
    bee.validated_has_varroa = has_varroa
    db.session.commit()
    flash("Image validée avec succès !", "success")
    return redirect(url_for("validate_images"))

@app.route("/merge-validated-images")
@login_required
def merge_validated_images_view():
    from app.models import BeeImage, NewBeeImage

    validated = NewBeeImage.query.filter_by(is_validated=True).filter(NewBeeImage.validated_has_varroa != None).all()
    added = 0

    for img in validated:
        if not BeeImage.query.filter_by(image_name=img.image_name).first():
            bee = BeeImage(
                image_name=img.image_name,
                image_data=img.image_data,
                has_varroa=img.validated_has_varroa
            )
            db.session.add(bee)
            added += 1
        db.session.delete(img)

    db.session.commit()
    flash(f"{added} image(s) transférée(s) avec succès dans BeeImage.", "success")
    return redirect(url_for('validate_images'))


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
            unique_id = uuid.uuid4().hex
            filename = f"{unique_id}_{secure_filename(file.filename)}"

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