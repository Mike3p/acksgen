from flask import (Blueprint, render_template, request, session)
from Tools.dice import roll, get_ability_mod_str
from Tools.forms import AbilityScoreForm

bp = Blueprint('array_generator_page', __name__, url_prefix='/ACKS/ability_scores')
data = {}

@bp.route('/', methods=('GET', 'POST'))
def page():

    ability_scores = []
    ability_score_form = AbilityScoreForm()

    return render_template('pagesACKS/ability_arrays.html', scores = ability_scores, cfg = ability_score_form)


@bp.route('/generate', methods=('GET', 'POST'))
def generate_scores():

    ability_score_form = AbilityScoreForm()
    table = request.form.get('table')
    ability_score_form.table.process_data(table)
    ability_scores = []

    for i in range(5):
        abl = []
        mod = []
        for i in range(6):
            abl_roll = roll("3d6")
            abl.append(abl_roll)
            mod.append(get_ability_mod_str(abl_roll))

        abilities = {"STR":{"a":abl[0],"m":mod[0]},"INT":{"a":abl[1],"m":mod[1]},"WIS":{"a":abl[2],"m":mod[2]},
                     "DEX":{"a":abl[3],"m":mod[3]},"CON":{"a":abl[4],"m":mod[4]},"CHA":{"a":abl[5],"m":mod[5]}}
        ability_scores.append(abilities)

    return render_template('pagesACKS/ability_arrays.html', scores = ability_scores, cfg = ability_score_form, table = table)
