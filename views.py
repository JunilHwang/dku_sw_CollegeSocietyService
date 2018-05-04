from flask import render_template
from app2 import app

@app.route('/')
def MainPage():
    return render_template("index.html")