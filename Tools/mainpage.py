
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('mainpage', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    return render_template('base.html')
    
