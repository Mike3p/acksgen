import functools, yaml

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from . import chargen
from wtforms import Form, SelectField, StringField, validators, IntegerField, SubmitField

class CharacterGenerationForm(Form):
    characterClass = SelectField(u'Class')
    level = SelectField(u'Level', choices=[(1,'1'), (2,'2'), (3,'3'), (4,'4'), (5,'5'), (6,'6'), (7,'7'), 
        (8,'8'), (9,'9'), (10,'10'), (11,'11'), (12,'12'), (13,'13'), (14,'14'), ])
    number = IntegerField(u'Number')
    submit = SubmitField(u'Generate')


bp = Blueprint('chargenpage', __name__, url_prefix='/chargen')

@bp.route('/', methods=('GET', 'POST'))
def page():

    with open("classes.yaml", 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            
    session['classes'] = sorted(data['classes'].keys())

    charGenForm = CharacterGenerationForm()
    charGenForm.characterClass.choices = [(x,x) for x in session['classes']]
    print(charGenForm.characterClass)
    return render_template('chargen/chargen.html', cfg = charGenForm)
    
    
@bp.route('/generate/', methods=('GET', 'POST'))
def generate():
    with open("classes.yaml", 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            
    characterClass = request.form.get('characterClass')
    characterLevel = int(request.form.get('level'))
    print(characterClass)
    x = chargen.createCharacter(characterClass, characterLevel, data)
    
    charGenForm = CharacterGenerationForm()
    charGenForm.characterClass.choices = [(x,x) for x in session['classes']]
    charGenForm.characterClass.process_data(characterClass)
    charGenForm.level.process_data(characterLevel)
  
    
    return render_template('chargen/chargen.html', char = x, cfg = charGenForm)
    
