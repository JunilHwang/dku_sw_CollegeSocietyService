#-*- coding: utf-8 -*-
from flask_mail import Mail,Message
from flask import render_template
mail=Mail()

def send_email(to,subject):
    from app2 import app
    msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,
                sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body=''
    msg.html=render_template('test.html')
    
    with app.app_context():
        mail.send(msg)