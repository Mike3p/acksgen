import functools, yaml

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('mainpage', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    return render_template('base.html')
    
# @bp.route('/createchar', methods=('GET', 'POST'))
# def createchar():
    # with open("classes.yaml", 'r') as stream:
        # try:
            # data = yaml.safe_load(stream)
        # except yaml.YAMLError as exc:
            # print(exc)
    # c = chargen.createCharacter('fighter', 1, data)
    # return render_template('gen/chargen.html', char = c)