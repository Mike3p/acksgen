import yaml
from flask import (Blueprint, render_template, request, session)
from forms import CharacterGenerationForm
from charactergeneration import chargen


bp = Blueprint('chargenpage', __name__, url_prefix='/chargen')
data = {}
session = {}

@bp.route('/', methods=('GET', 'POST'))
def page():
    global session
    loadData()

    charGenForm = CharacterGenerationForm()
    charGenForm.ethnicity.choices = [('random','random')]
    charGenForm.ethnicity.choices.extend([(x, x) for x in list(session['data']['names'].keys())])
    charGenForm.characterClass.choices = [(x, x) for x in session['choices']]
    return render_template('pages/chargen.html', cfg=charGenForm)


@bp.route('/generate/', methods=('GET', 'POST'))
def generate():
    global session
    loadData()

    characterClass = request.form.get('characterClass')
    characterLevel = int(request.form.get('characterLevel'))
    rollForParty = request.form.get('rollForParty')
    characterNumber = request.form.get('characterNumber')
    ethnicity = request.form.get('ethnicity')

    chargen.loadCharacterFile(session['data'])
    generateParty = False
    if rollForParty:
        generateParty = True

    characters = chargen.rollCharacters(characterClass, characterLevel, int(characterNumber), generateParty, ethnicity)

    charGenForm = CharacterGenerationForm()
    charGenForm.ethnicity.choices = [('random', 'random')]
    charGenForm.ethnicity.choices.extend([(x, x) for x in list(session['data']['names'].keys())])
    charGenForm.characterClass.choices = [(x, x) for x in session['choices']]

    #todo das is bisschen unhübsch. könnte man evtl mal auftrennen in ethnicities und namen und dann richtig machen
    charGenForm.ethnicity.process_data(ethnicity)
    charGenForm.characterClass.process_data(characterClass)
    charGenForm.characterLevel.process_data(characterLevel)
    charGenForm.characterNumber.process_data(characterNumber)
    charGenForm.rollForParty.process_data(rollForParty)

    return render_template('pages/chargen.html', char=characters, cfg=charGenForm)

def loadData():
    global session

    if not 'data' in session:
        print("fresh reload")
        with open("data.yaml", 'r') as stream:
            try:
                session['data'] = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    character_list = sorted(list(session['data']['classes'].keys()))
    character_list.append('random')
    character_list.append('generate from scores')
    session['choices'] = character_list