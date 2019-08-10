import functools, yaml

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('personalitygenpage', __name__, url_prefix='/persgen')

@bp.route('/', methods=('GET', 'POST'))
def page():
    return render_template('personality.html')
    
