import yaml
from flask import (Blueprint, render_template, request, session)
from Tools.forms import CharacterGenerationForm
from Tools.chargen import characterGenerator
from pathlib import Path

bp = Blueprint('chargenpage', __name__, url_prefix='/chargen')
#data = {}
gen_dict = {}

@bp.route('/', methods=('GET', 'POST'))
def page():
    loadData()

    charGenForm = CharacterGenerationForm()
    charGenForm.ethnicity.choices = [(None,'random')]
    charGenForm.ethnicity.choices.extend([(x, x) for x in list(session['gen_dict']['ethnicity'].keys())])
    charGenForm.characterClass.choices = [(None, 'random')]
    charGenForm.characterClass.choices.extend([(x, x) for x in session['choices']])
    return render_template('pages/chargen.html', cfg=charGenForm)


@bp.route('/generate', methods=('GET', 'POST'))
def generate():
    loadData()
    characterClass = request.form.get('characterClass')
    try:
        characterLevel = int(request.form.get('characterLevel'))
        rollForParty = request.form.get('rollForParty')
        characterNumber = min(int(request.form.get('characterNumber')), 50)
        ethnicity = request.form.get('ethnicity')
    except:
        characterLevel = 1
        rollForParty = False
        characterNumber = 1
        ethnicity = "random"


    generateParty = False
    if rollForParty:
        generateParty = True

    characters = characterGenerator.roll_party(int(characterNumber), generateParty, session['gen_dict'], characterLevel, characterClass,
                                               ethnicity)

    charGenForm = CharacterGenerationForm()
    charGenForm.ethnicity.choices = [(None, 'random')]
    charGenForm.ethnicity.choices.extend([(x, x) for x in list(session['gen_dict']['ethnicity'].keys())])
    charGenForm.characterClass.choices = [(None, 'random')]
    charGenForm.characterClass.choices.extend([(x, x) for x in session['choices']])

    #todo das is bisschen unhübsch. könnte man evtl mal auftrennen in ethnicities und namen und dann richtig machen
    charGenForm.ethnicity.process_data(ethnicity)
    charGenForm.characterClass.process_data(characterClass)
    charGenForm.characterLevel.process_data(characterLevel)
    charGenForm.characterNumber.process_data(characterNumber)
    charGenForm.rollForParty.process_data(rollForParty)
    #charGenForm.createExcelSheet.process_data(createExcelSheet)

    return render_template('pages/chargen.html', char=characters, cfg=charGenForm)

def loadData():
    if 'gen_dict' not in session:
        print("fresh reload")

        path = Path(__file__).parent / "../../generator_basic_acks.yaml"
        a = path.open()
        with open(a.name, 'r') as stream:
            try:
                session['gen_dict'] = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    character_list = sorted(list(session['gen_dict']['classes'].keys()))
    #character_list.append('random')
    session['choices'] = character_list