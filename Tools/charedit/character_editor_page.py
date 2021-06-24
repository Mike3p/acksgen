from flask import (Blueprint, render_template, request, session, Response)
from flask import current_app as app
from flask_session import Session
from flask import Flask, flash, request, redirect, url_for
from Tools.chargen.characterGenerator import load_character, get_yaml_of_character
from Tools.chargen.character import Character
import yaml
from flask_jsonpify import jsonify
from werkzeug.utils import secure_filename

bp = Blueprint('character_editor_page', __name__, url_prefix='/charedit')


@bp.route('/')
def page():
    session['uploaded_character'] = None
    return render_template('pages/charedit.html')


@bp.route('/upload', methods=('GET', 'POST'))
def upload_character():
    character_file = request.files['file']
    print("test")
    if character_file:
        character_object = load_character(yaml.safe_load(character_file))
        session['uploaded_character'] = character_object

        #return render_template('pages/charedit.html', char = session.get('uploaded_character').__repr__())
        return jsonify(result=session.get('uploaded_character').__repr__())
    else:
        #return render_template('pages/charedit.html', char = ["no file chosen!"])
        return jsonify(result="No File chosen!")

# @bp.route('/levelup', methods=('GET', 'POST'))
# def levelup_character():
#     if session.get('uploaded_character'):
#         try:
#             c: Character = session.get('uploaded_character')
#             c.levelup(c.level+1,25)
#             session['uploaded_character'] = c
#         except:
#             return """
#             <h1 style='color: red;'>Invalid Character File!</h1>
#             """
#         #return render_template('pages/charedit.html', char = session.get('uploaded_character').__repr__())
#         return render_template('pages/charedit.html', embed=get_yaml_of_character(session.get('uploaded_character')))
#     return render_template('pages/charedit.html', char = ["no character uploaded!"])

@bp.route('/levelup', methods=('GET', 'POST'))
def levelup_character():
    if session.get('uploaded_character'):
        try:
            c: Character = session.get('uploaded_character')
            c.levelup(c.level+1,25)
            session['uploaded_character'] = c
        except:
            return """
            <h1 style='color: red;'>Invalid Character File!</h1>
            """
        return jsonify(char=c.__repr__())
        #return render_template('pages/charedit.html')
    return render_template('pages/charedit.html', char = ["no character uploaded!"])

@bp.route('/download', methods = ('GET', 'POST'))
def download_character():
    try:
        char_object = session.get('uploaded_character')
        result = get_yaml_of_character(char_object)
        return Response(result,
                        mimetype='file/yaml',
                        headers={'Content-Disposition': 'attachment; filename=' + str(char_object.name) + ".yaml"})
    except:
        # raise Exception("invalid character id")
        return render_template('pages/charedit.html', char = ["no character uploaded!"])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

