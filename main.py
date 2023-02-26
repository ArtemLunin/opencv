import os
import hashlib
from flask import Flask, flash, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = "./uploads"
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
    return hashlib.md5(name.encode()).hexdigest() + ext

class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    fileId = db.Column(db.String(length=32), nullable=False, unique=True)
    storedName = db.Column(db.String(length=32))
    originalName = db.Column(db.String(length=255))


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        fileId = request.form['file_id']
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            print(request.url)
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print(secure_filename(file.filename))
            filename = digest_filename(secure_filename(file.filename))
            # hashlib.md5('test string'.encode()).hexdigest()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    forms = [
    {'title': 'form1', 'image': 'img_1.jpg', 'file_id': 'file1'}, 
    {'title': 'form2', 'image': 'img_2.jpg', 'file_id': 'file2'}
    ]
    return render_template('index.html', forms = forms)

@app.route("/clear")
def clear():
    db.session.query(Item).delete()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
