from flask import (Blueprint, render_template, request, session)
from Tools.forms import InitiativeForm
from Tools.dice import roll
from Tools.ACKS.initiative import initiative

bp = Blueprint('initiativepage', __name__, url_prefix='/ACKS/initiative')
data = {}

@bp.route('/', methods=('GET', 'POST'))
def page():


    initiativeTextbox = InitiativeForm()
    if 'ini' in session:
        initiativeTextbox.initiativeInput.process_data(session.get('ini', ""))
    #session['ini'] = request.form.get('initiativeInput')
    #initiativeTextbox.initiativeInput.process_data(session.get('ini', ""))

    return render_template('pagesACKS/initiative.html', cfg = initiativeTextbox)


@bp.route('/rollInitiative', methods=('GET', 'POST'))
def rollInitiative():

    session['ini'] = request.form.get('initiativeInput')

    textInput = request.form.get('initiativeInput')
    lines = textInput.split("\n")
    initiativeValues = []
    for line in lines:
        print(line)
        ctup = ''
        try:
            c = line.split(":")
            ctup = ("<b>"+c[0].strip()+"</b>", roll('1d6')+int(c[1].strip()))
        except: print(line + " is not a valid initiative.")
        initiativeValues.append(ctup)
    print(initiativeValues)

    i = initiative.getInitiativeAsString(initiativeValues)

    initiativeTextbox = InitiativeForm()
    initiativeTextbox.initiativeInput.process_data(session.get('ini', ""))

    return render_template('pagesACKS/initiative.html', cfg = initiativeTextbox, initiativeRolls = i)
