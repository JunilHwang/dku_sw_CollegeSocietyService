#app2.py
#initialize flask app

from flask import Flask

def create_app(config_filename):    #init flask app then return
    app=Flask(__name__)
    app.config.from_object(config_filename)

    from models import db
    db.init_app(app)

    from api import api
    api.init_app(app)

    return app

app=create_app('config')    #read settings from config.py
