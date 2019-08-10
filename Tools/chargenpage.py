import functools, yaml
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from . import chargen, forms

bp = Blueprint('chargenpage', __name__, url_prefix='/chargen')

@bp.route('/', methods=('GET', 'POST'))
def page():

    with open("classes.yaml", 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            
    session['classes'] = sorted(data['classes'].keys())

    charGenForm = forms.CharacterGenerationForm()
    charGenForm.characterClass.choices = [(x,x) for x in session['classes']]
    
    return render_template('chargen/chargen.html', cfg = charGenForm)
    
    
@bp.route('/generate/', methods=('GET', 'POST'))
def generate():
    with open("classes.yaml", 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            
    characterClass = request.form.get('characterClass')
    characterLevel = int(request.form.get('characterLevel'))
    characterPersonality = request.form.get('characterPersonality')
    x = chargen.createCharacter(characterClass, characterLevel, data)
    
    charGenForm = forms.CharacterGenerationForm()
    charGenForm.characterClass.choices = [(x,x) for x in session['classes']]
    charGenForm.characterClass.process_data(characterClass)
    charGenForm.characterLevel.process_data(characterLevel)
    charGenForm.characterPersonality.process_data(characterPersonality)  
    
    return render_template('chargen/chargen.html', char = x, cfg = charGenForm)
    
