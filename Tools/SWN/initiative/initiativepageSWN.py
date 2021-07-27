from flask import (Blueprint, render_template, request, session)
from Tools.forms import InitiativeForm
from Tools.dice import roll, highest_x_of_y
from Tools.SWN.initiative import initiative

bp = Blueprint('initiativepageSWN', __name__, url_prefix='/SWN/initiativeSWN')
data = {}

@bp.route('/', methods=('GET', 'POST'))
def page():


    #initiativeTextbox = InitiativeForm("X: Y\nX2: Y2\n...\nwhere X = character name and Y = character initiative.\n"
    #                                   "if a character has the alert foci denote as X: Ya")

    initiativeTextbox = InitiativeForm()
    if 'ini' in session:
        initiativeTextbox.initiativeInput.process_data(session.get('ini', ""))
    #session['ini'] = request.form.get('initiativeInput')
    #initiativeTextbox.initiativeInput.process_data(session.get('ini', ""))

    return render_template('pagesSWN/initiative.html', cfg = initiativeTextbox)


@bp.route('/rollinitiative/', methods=('GET', 'POST'))
def roll_initiative():

    session['ini'] = request.form.get('initiativeInput')

    textInput = request.form.get('initiativeInput')
    lines = textInput.split("\n")
    initiativeValues = []
    for line in lines:
        print(line)
        ctup = ''
        try:
            c = line.split(":")
            if "a" in c[1]:
                ini_roll = highest_x_of_y(1, 2, "1d8")[0]
                c[1] = str.replace(c[1],"a","")
            else:
                ini_roll = roll("1d8")
            ctup = ("<b>"+c[0].strip()+"</b>", ini_roll+int(c[1].strip()))
        except: print(line + " is not a valid initiative.")
        initiativeValues.append(ctup)
    print(initiativeValues)

    i = initiative.getInitiativeAsString(initiativeValues)

    initiativeTextbox = InitiativeForm()
    initiativeTextbox.initiativeInput.process_data(session.get('ini', ""))

    return render_template('pagesSWN/initiative.html', cfg = initiativeTextbox, initiativeRolls = i)
