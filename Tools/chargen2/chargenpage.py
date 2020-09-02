import yaml
from flask import (Blueprint, render_template, request)
from Tools.forms import CharacterGenerationForm
from Tools.chargen2 import characterGenerator
from pathlib import Path

bp = Blueprint('chargenpage', __name__, url_prefix='/chargen')
data = {}
session = {}

@bp.route('/', methods=('GET', 'POST'))
def page():
    global session
    loadData()

    charGenForm = CharacterGenerationForm()
    charGenForm.ethnicity.choices = [('random','random')]
    charGenForm.ethnicity.choices.extend([(x, x) for x in list(session['data']['ethnicity'].keys())])
    charGenForm.characterClass.choices = [(x, x) for x in session['choices']]
    return render_template('pages/chargen.html', cfg=charGenForm)


@bp.route('/generate/', methods=('GET', 'POST'))
def generate():
    global session
    loadData()

    characterClass = request.form.get('characterClass')
    characterLevel = int(request.form.get('characterLevel'))
    rollForParty = request.form.get('rollForParty')
    characterNumber = min(int(request.form.get('characterNumber')),200)
    #createExcelSheet = request.form.get('createExcelSheet')
    ethnicity = request.form.get('ethnicity')

    generateParty = False
    if rollForParty:
        generateParty = True

    characters = characterGenerator.roll_party(int(characterNumber),generateParty, session['data'], characterLevel, characterClass,
                                               ethnicity)

    charGenForm = CharacterGenerationForm()
    charGenForm.ethnicity.choices = [('random', 'random')]
    charGenForm.ethnicity.choices.extend([(x, x) for x in list(session['data']['ethnicity'].keys())])
    charGenForm.characterClass.choices = [(x, x) for x in session['choices']]

    #todo das is bisschen unhübsch. könnte man evtl mal auftrennen in ethnicities und namen und dann richtig machen
    charGenForm.ethnicity.process_data(ethnicity)
    charGenForm.characterClass.process_data(characterClass)
    charGenForm.characterLevel.process_data(characterLevel)
    charGenForm.characterNumber.process_data(characterNumber)
    charGenForm.rollForParty.process_data(rollForParty)
    #charGenForm.createExcelSheet.process_data(createExcelSheet)

    return render_template('pages/chargen.html', char=characters, cfg=charGenForm)

def loadData():
    global session

    if not 'data' in session:
        print("fresh reload")

        path = Path(__file__).parent / "../../newdata.yaml"
        a = path.open()
        with open(a.name, 'r') as stream:
            try:
                session['data'] = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    character_list = sorted(list(session['data']['classes'].keys()))
    character_list.append('random')
    session['choices'] = character_list