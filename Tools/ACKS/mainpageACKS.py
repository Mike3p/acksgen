from flask import (Blueprint, render_template, request, session)


bp = Blueprint('mainpageACKS', __name__, url_prefix='/ACKS')
data = {}

@bp.route('/', methods=('GET', 'POST'))
def page():

    return render_template('sidebarACKS.html')
