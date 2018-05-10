#models.py
#models mapping to database

from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

def many_returns(query):
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
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class member(db.Model, AddUpdateDelete):
    idx=db.Column(db.Integer, primary_key=True)
    id=db.Column(db.String(16), unique=True, nullable=False)
    pw=db.Column(db.String(255), nullable=False)
    name=db.Column(db.String(20), nullable=False)
    college=db.Column(db.String(20), nullable=False)
    major=db.Column(db.String(20), nullable=False)
    undergrad_number=db.Column(db.Integer, nullable=False)
    email=db.Column(db.String(30), nullable=False)
    nickname=db.Column(db.String(20))
    regdate=db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    level=db.Column(db.Integer, default=1)

    def __init__(self,id,pw,name,college,major,undergrad_number,email,nickname):
        self.id=id
        self.pw=pw
        self.name=name
        self.college=college
        self.major=major
        self.undergrad_number=undergrad_number
        self.email=email
        if nickname:
            self.nickname=nickname
        else:
            self.nickname=id

class board(db.Model,AddUpdateDelete):
    idx=db.Column(db.Integer, primary_key=True)
    category=db.Column(db.Integer, nullable=False)
    writer=db.Column(db.Integer, db.ForeignKey('member.idx'), nullable=False)
    parent=db.Column(db.Integer)
    od=db.Column(db.Integer)
    depth=db.Column(db.Integer)
    subject=db.Column(db.String(255), nullable=False)
    content=db.Column(db.TEXT)
    reg_date=db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    hit=db.Column(db.Integer)
    goods=db.Column(db.Integer)

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
    index=db.Column('idx', db.Integer, primary_key=True)
    board_idx=db.Column('bidx', db.Integer, db.ForeignKey('board.idx'), nullable=False)
    writer=db.Column(db.Integer, db.ForeignKey('member.idx'), nullable=False)
    od=db.Column(db.Integer)
    depth=db.Column(db.Integer)
    content=db.Column(db.TEXT, nullable=False)
    date=db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

    def __init__(self,board_idx,writer,od,depth,content):
        self.board_idx=board_idx
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
