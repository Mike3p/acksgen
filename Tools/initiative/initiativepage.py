from flask import (Blueprint, render_template, request, session)
from forms import InitiativeForm
from dice import roll
from initiative import initiative

bp = Blueprint('initiativepage', __name__, url_prefix='/initiative')
data = {}


@bp.route('/', methods=('GET', 'POST'))
def page():

    initiativeTextbox = InitiativeForm()
    initiativeTextbox.initiativeInput.process_data(session['initiativeField'])

    return render_template('pages/initiative.html', cfg = initiativeTextbox)


@bp.route('/rollinitiative/', methods=('GET', 'POST'))
def rollInitiative():

    session['initiativeField'] = request.form.get('initiativeInput')

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
    initiativeTextbox.initiativeInput.process_data(session['initiativeField'])

    return render_template('pages/initiative.html', cfg = initiativeTextbox, initiativeRolls = i)
