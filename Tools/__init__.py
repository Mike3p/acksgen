import os

from flask import Flask
from flask_session import Session
from Tools import mainpage
from Tools.config import Config

from Tools.ACKS import mainpageACKS
from Tools.ACKS.upload import uploadpage
from Tools.ACKS.initiative import initiativepage
from Tools.ACKS.chargen import chargenpage
from Tools.ACKS.charedit import character_editor_page
from Tools.ACKS.ability_array_generator import array_generator_page

from Tools.SWN import mainpageSWN
from Tools.SWN.initiative import initiativepageSWN
from Tools.SWN.chargen import chargenpageSWN


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

    app.register_blueprint(mainpageACKS.bp)
    app.register_blueprint(mainpage.bp)
    app.register_blueprint(chargenpage.bp)
    app.register_blueprint(initiativepage.bp)
    app.register_blueprint(uploadpage.bp)
    app.register_blueprint(character_editor_page.bp)
    app.register_blueprint(array_generator_page.bp)

    app.register_blueprint(mainpageSWN.bp)
    app.register_blueprint(initiativepageSWN.bp)
    app.register_blueprint(chargenpageSWN.bp)

    app.add_url_rule('/', endpoint='index')
    
    return app