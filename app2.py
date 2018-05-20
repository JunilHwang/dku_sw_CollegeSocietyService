#app2.py
#initialize flask app

from flask import Flask, render_template, jsonify
from auth import *
def create_app(config_filename):    #init flask app then return
    app=Flask(__name__)
    app.config.from_object(config_filename)

    from models import db
    db.init_app(app)

    from api import api
    api.init_app(app)

    from auth import jwt
    jwt.init_app(app)

    @app.route('/')
    def MainPage():
        return render_template("index.html")

    @app.teardown_appcontext                #close db session automatically when server off
    def shutdown_session(exception=None):
        db.session.remove()
    
    return app

app=create_app('config')    #read settings from config.py