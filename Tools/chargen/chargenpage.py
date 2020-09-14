import yaml
from flask import (Blueprint, render_template, request, session, Response, url_for)
from Tools.forms import CharacterGenerationForm
from Tools.chargen.characterGenerator import (roll_party, get_yaml_of_character)
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


@bp.route('/download/<character_id>')
def download_character(character_id = 0):
    try:
        char_object = session.get('character_objects')[int(character_id)]
        result = get_yaml_of_character(char_object)
        return Response(result,
                        mimetype='file/yaml',
                        headers={'Content-Disposition': 'attachment; filename='+str(char_object.name)+".yaml"})
    except:
        #raise Exception("invalid character id")
        return """
    <h1 style='color: red;'>No such character ID!</h1>
    """



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

    characters = roll_party(int(characterNumber), generateParty, session['gen_dict'],
                                               characterLevel, characterClass, ethnicity)
    out_strings = []
    out_characters =[]
    i = 0
    for c in characters:
        out = c.__repr__()
        out.append("<a href=\""+url_for('chargenpage.download_character',character_id = i) \
        + "\">export character</a>")
        #c.name = "<a href=\""+url_for('chargenpage.download_character',character_id = i) \
        #+ "\">"+c.name+"</a>"
        out_strings.append(out)
        out_characters.append(c)
        i+=1
    session['character_objects'] = out_characters


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

    return render_template('pages/chargen.html', char=out_strings, cfg=charGenForm)
    #return jsonify({'chars': out_strings, 'chars_yaml': out_characters})

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