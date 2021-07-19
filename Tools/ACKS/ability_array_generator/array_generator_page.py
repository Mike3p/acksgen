from flask import (Blueprint, render_template, request, session)
from Tools.forms import InitiativeForm
from Tools.dice import roll
from Tools.ACKS.initiative import initiative

bp = Blueprint('initiativepage', __name__, url_prefix='/ACKS/ability_scores')
data = {}

@bp.route('/', methods=('GET', 'POST'))
def page():

    ability_scores = []

    return render_template('pagesACKS/ability_scores.html', scores = ability_scores)


@bp.route('/generate', methods=('GET', 'POST'))
def generate_scores():

    ability_scores = []

    for i in range(5):
        abilities = {"STR":roll("3d6"),"INT":roll("3d6"),"WIS":roll("3d6"),
                     "DEX":roll("3d6"),"CON":roll("3d6"),"CHA":roll("3d6"),}
        ability_scores.append(abilities)

    return render_template('pagesACKS/ability_scores.html', scores = ability_scores)
