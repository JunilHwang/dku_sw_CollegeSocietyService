#models.py
#models mapping to database

from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as password_context     #for password hashing
import re       #for regular expression

db=SQLAlchemy()

def many_returns(query):    #쿼리 응답이 여러개의 튜플을 리턴할 때 serialization
    tuple_list=[]
    for tuple in query:
        tuple_list.append(tuple.as_dict())
    return tuple_list

class AddUpdateDelete():
    def add(self,resource):
        db.session.add(resource)
        return db.session.commit()
    def update(self):
        return db.session.commit()
    def delete(self,resource):
        db.session.delete(resource)
        return db.session.commit()
    def as_dict(self):      #쿼리결과를 dictionary로 변환
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

#class이름과 db table이름을 일치시킨다. 일치하지 않을땐 __tablename__="테이블명"으로 매칭
class member(db.Model, AddUpdateDelete):
    idx=db.Column(db.Integer, primary_key=True)
    id=db.Column(db.String(16), unique=True, nullable=False)
    pw=db.Column(db.String(255), nullable=False)    #hashed password
    name=db.Column(db.String(20), nullable=False)
    college=db.Column(db.String(20), nullable=False)
    major=db.Column(db.String(20), nullable=False)
    undergrad_number=db.Column(db.Integer, nullable=False)
    email=db.Column(db.String(30), nullable=False)
    nickname=db.Column(db.String(20))
    regdate=db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    level=db.Column(db.Integer, default=1)

    def verify_password(self, password):
        return password_context.verify(password, self.pw)

    #패스워드의 유효성을 검사하고 모두 만족시 해시 암호화 한다(64bit-SHA512,32bit-SHA256)
    #처리에 시간이 오래걸릴 경우 필요 라운드 수를 줄여야 함
    def check_password_strength_and_hash_if_ok(self, password):
        if len(password)<8:
            return 'The password is too short.', False
        if len(password)>16:
            return 'The password is too long.', False
        if re.search(r'[a-zA-Z]', password) is None:
            return 'The password must include at least one alphabet', False
        if re.search(r'\d', password) is None:
            return 'The password must include at least one number', False
        if re.search(r"[!@#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None:
            return 'The password must include at least one symbol', False
        self.pw=password_context.encrypt(password)
        return '', True

    def __init__(self,id,name,college,major,undergrad_number,email,nickname):
        self.id=id
        self.name=name
        self.college=college
        self.major=major
        self.undergrad_number=undergrad_number
        self.email=email
        if nickname:
            self.nickname=nickname
        else:   #닉네임이 None이면 이름을 닉네임으로 설정.
            self.nickname=name

class board(db.Model,AddUpdateDelete):
    idx=db.Column(db.Integer, primary_key=True)
    category=db.Column(db.Integer, db.ForeignKey('category.idx'), nullable=False)
    writer=db.Column(db.Integer, db.ForeignKey('member.idx'), nullable=False)
    parent=db.Column(db.Integer)
    od=db.Column(db.Integer)
    depth=db.Column(db.Integer)
    subject=db.Column(db.String(255), nullable=False)
    content=db.Column(db.TEXT)
    reg_date=db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    hit=db.Column(db.Integer, default=0)
    goods=db.Column(db.Integer, default=0)

    def __init__(self,category,writer,parent,od,depth,subject,content):
        self.category=category
        self.writer=writer
        self.parent=parent
        self.od=od
        self.depth=depth
        self.subject=subject
        self.content=content

class category(db.Model,AddUpdateDelete):
    idx=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    skin=db.Column(db.String(50))

    def __init__(self,name,skin):
        self.name=name
        self.skin=skin

class comment(db.Model,AddUpdateDelete):
    idx=db.Column(db.Integer, primary_key=True)
    bidx=db.Column(db.Integer, db.ForeignKey('board.idx',ondelete='CASCADE'), nullable=False)
    writer=db.Column(db.Integer, db.ForeignKey('member.idx'), nullable=False)
    od=db.Column(db.Integer)
    depth=db.Column(db.Integer)
    content=db.Column(db.TEXT)
    date=db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

    def __init__(self,bidx,writer,od,depth,content):
        self.bidx=bidx
        self.writer=writer
        self.od=od
        self.depth=depth
        self.content=content

class cms(db.Model,AddUpdateDelete):
    idx=db.Column(db.Integer, primary_key=True)
    content=db.Column(db.VARCHAR(255))
    deposit=db.Column(db.Integer)
    withdraw=db.Column(db.Integer)
    date=db.Column(db.DATE)

    def __init__(self,content,deposit,withdraw,date):
        self.content=content
        self.deposit=deposit
        self.withdraw=withdraw
        self.date=date

class meta_data(db.Model, AddUpdateDelete):
    key=db.Column(db.String(20), primary_key=True)
    value=db.Column(db.TEXT)

    def __init__(self, key, value):
        self.key=key
        self.value=value

class files(db.Model, AddUpdateDelete):
    idx=db.Column(db.Integer, primary_key=True)
    table=db.Column(db.String(20))
    id=db.Column(db.Integer)
    origin_name=db.Column(db.VARCHAR(255))
    file_name=db.Column(db.String(50))
    reg_date=db.Column(db.TIMESTAMP)

    def __init__(self,table,id,origin_name,file_name,reg_date):
        self.table=table
        self.id=id
        self.origin_name=origin_name
        self.file_name=file_name
        self.reg_date=reg_date
