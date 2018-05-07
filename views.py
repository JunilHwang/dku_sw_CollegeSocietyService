from flask import render_template
from app2 import app
from models import db

@app.route('/')
def MainPage():
    return render_template("index.html")

@app.teardown_appcontext                #close db session automatically when server off
def shutdown_session(exception=None):
    db.session.remove()