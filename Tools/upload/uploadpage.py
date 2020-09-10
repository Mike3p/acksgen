from flask import (Blueprint, render_template, request, session)
from flask import current_app as app
from flask_session import Session
from flask import Flask, flash, request, redirect, url_for
import yaml
from werkzeug.utils import secure_filename

bp = Blueprint('uploadpage', __name__, url_prefix='/upload')


@bp.route('/')
def page():

    return render_template('pages/upload.html')


@bp.route('/upload', methods=('GET', 'POST'))
def upload_file():
    #print("asd")
    gen_config = request.files['file']
    yaml_config = yaml.safe_load(gen_config)
    session['gen_dict'] = yaml_config
    #print(yaml_config)

    return render_template('pages/upload.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@bp.route('/reset', methods=['GET', 'POST'])
def reset_generator():
    if 'gen_dict' in session: session.pop('gen_dict')
    print("generator file resetted")

    return render_template('pages/upload.html')