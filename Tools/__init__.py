import os

from flask import Flask, session
from flask_session import Session
from Tools import mainpage
from Tools.upload import uploadpage
from Tools.init import initiativepage
from Tools.chargen import chargenpage
from Tools.charedit import character_editor_page
from Tools.config import Config


def create_app(test_config=None):
    # create and configure the app

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    Session(app)
    
    # if test_config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile('config.py', silent=True)
    # else:
        # load the test config if passed in
        # app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
      
    #db.init_app(app) wir brauchen erstma keine db denk ich

    app.register_blueprint(mainpage.bp)
    app.register_blueprint(chargenpage.bp)
    app.register_blueprint(initiativepage.bp)
    app.register_blueprint(uploadpage.bp)
    app.register_blueprint(character_editor_page.bp)
    
    app.add_url_rule('/', endpoint='index')
    
    return app