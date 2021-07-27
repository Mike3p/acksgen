from flask import (Blueprint, render_template, request, session)
from Tools.tableroller import *

bp = Blueprint('chargenpageSWN', __name__, url_prefix='/SWN/chargenSWN')
data = {}

@bp.route('/', methods=('GET', 'POST'))
def page():

    return render_template('pagesSWN/chargen.html')


@bp.route('/createcharacter/', methods=('GET', 'POST'))
def create_character():

    character = ""
    background = rollOnTable_string()

    return render_template('pagesSWN/chargen.html', char = character)
