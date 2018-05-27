#-*- coding: utf-8 -*-
from flask_mail import Mail,Message
mail=Mail()

title="가입인증 메일입니다"
def send_email(to,subject,args):
    from app2 import app
    url='http://localhost:5000/mailauth/{user_index}'.format(user_index=args['idx'])
    msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,
                sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body=''
    msg.html="가입하신 계정정보는 아래와 같습니다<br><hr>"+\
        "아이디 : "+args['id']+"<br>"+\
        "닉네임 : "+args['nickname']+"<br>"+\
        "이메일 : "+args['email']+"<br><hr>"+\
        "아래 버튼을 클릭하시면 가입이 완료됩니다.<br>"+\
        "<a href='{URL}'><input type='button' value='메일인증'/></a>".format(URL=url)
    
    with app.app_context():
        mail.send(msg)