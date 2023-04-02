import os
import hashlib
from flask import Flask, flash, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from werkzeug.utils import secure_filename
import random
import string
from compare import CompareIimages, CalcImageHash, CompareHash


UPLOAD_FOLDER = "./static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///opencv.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


db = SQLAlchemy(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def digest_filename(filename):
    base = os.path.basename(filename)
    [name, ext] = os.path.splitext(base)
    file_prefix = ''.join(random.choice(string.digits) for i in range(4))
    return hashlib.md5((file_prefix + name).encode()).hexdigest() + ext

def remove_files(dir_name):
    for file in os.scandir(dir_name):
        if os.path.isfile(file.path) or os.path.islink(file.path):
            os.remove(file.path)

def compare_images(images):
    hash1 = CalcImageHash(images[0])
    hash2 = CalcImageHash(images[1])
    return CompareHash(hash1, hash2)


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    fileId = db.Column(db.String(length=32), nullable=False, unique=True)
    storedName = db.Column(db.String(length=32))
    originalName = db.Column(db.String(length=255))


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part', category='warning')
            return redirect(request.url)
        
        fileId = request.form['fileId']
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', category='warning')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            secureFilename = secure_filename(file.filename)
            filename = digest_filename(secureFilename)
            item = Item(fileId=fileId, storedName=filename, originalName=secureFilename)
            try:
                db.session.add(item)
                db.session.commit()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except IntegrityError:
                # filter_by
                db.session.rollback()
                upd_item = db.session.execute(db.select(Item).filter_by(fileId=fileId)).scalar_one_or_none()
                if upd_item:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], upd_item.storedName))
                    upd_item.originalName = secureFilename
                    upd_item.storedName = filename
                    db.session.commit()
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    if request.method == "GET":
        items = Item.query.all()
        forms = [
            {'title': 'form1', 'dir': 'images', 'storedName': 'upload.png', 'fileId': 'file1'}, 
            {'title': 'form2', 'dir': 'images', 'storedName': 'upload.png', 'fileId': 'file2'}
            ]
        i = 0
        for item in items:
            forms[i]['storedName'] = item.storedName
            forms[i]['originalName'] = item.originalName
            forms[i]['fileId'] = item.fileId
            forms[i]['dir'] = 'uploads'
            i += 1
    return render_template('index.html', forms=forms)

@app.route("/clear")
def clear():
    try:
        db.session.query(Item).delete()
        db.session.commit()
    except OperationalError as e:
        db.create_all()
        db.session.commit()
    except Exception as err:
        flash(f"Unexpected {err=}, {type(err)=}", category='danger')
    finally:
        remove_files(app.config['UPLOAD_FOLDER'])
    return redirect(url_for('index'))

@app.route("/compare")
def compare():
    items = Item.query.all()
    images = []
    # print(items)
    if len(items) < 2:
        flash(f"Nothing to compare", category='warning')
        return redirect(url_for('index'))
    
    for item in items:
        images.append(os.path.join(app.config['UPLOAD_FOLDER'], item.storedName))

    compare_result = compare_images(images)

    flash(f"Images: {'are identical' if compare_result <5 else 'are not identical' }", category='info')
    # compare_result = CompareIimages(images)
    # flash(f"PIL Compare result is: {compare_result}")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
