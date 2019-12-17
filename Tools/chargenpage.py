import yaml
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from forms import CharacterGenerationForm
import chargen

bp = Blueprint('chargenpage', __name__, url_prefix='/chargen')
data = {}


@bp.route('/', methods=('GET', 'POST'))
def page():
    global data

    with open("classes.yaml", 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    session['classes'] = sorted(data['classes'].keys())
    session['classes'].append('random')

    charGenForm = CharacterGenerationForm()
    charGenForm.characterClass.choices = [(x, x) for x in session['classes']]

    return render_template('chargen/chargen.html', cfg=charGenForm)


@bp.route('/generate/', methods=('GET', 'POST'))
def generate():
    global data

    characterClass = request.form.get('characterClass')
    characterLevel = int(request.form.get('characterLevel'))
    characterPersonality = request.form.get('characterPersonality')
    characterNumber = request.form.get('characterNumber')

    chargen.loadCharacterFile(data)
    x = chargen.rollCharacters(characterClass, characterLevel, int(characterNumber))

    charGenForm = CharacterGenerationForm()
    charGenForm.characterClass.choices = [(x, x) for x in session['classes']]
    charGenForm.characterClass.process_data(characterClass)
    charGenForm.characterLevel.process_data(characterLevel)
    charGenForm.characterPersonality.process_data(characterPersonality)
    charGenForm.characterNumber.process_data(characterNumber)

    return render_template('chargen/chargen.html', char=x, cfg=charGenForm)
