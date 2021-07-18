from flask import (Blueprint, render_template, request, session)


bp = Blueprint('mainpageSWN', __name__, url_prefix='/SWN')
data = {}

@bp.route('/', methods=('GET', 'POST'))
def page():

    return render_template('sidebarSWN.html')
