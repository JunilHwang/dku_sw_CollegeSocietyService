#models.py
#models mapping to database

from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class AddUpdateDelete():
    def add(self,resource):
        try:
            db.session.add(resource)
            return db.session.commit()
        except Exception as e:
            db.session.rollback()
            return str(e)
    def update(self):
        return db.session.commit()
    def delete(self,resource):
        try:
            db.session.delete(resource)
            return db.session.commit()
        except Exception as e:
            db.session.rollback()
            return str(e)

class member(db.Model, AddUpdateDelete):
    index=db.Column('idx',db.Integer, primary_key=True)
    id=db.Column(db.String(16), unique=True, nullable=False)
    pw=db.Column(db.String(255), nullable=False)
    name=db.Column(db.String(20), nullable=False)
    college=db.Column(db.String(20), nullable=False)
    major=db.Column(db.String(20), nullable=False)
    st_num=db.Column('undergrad_number',db.Integer, nullable=False)
    email=db.Column(db.String(30), nullable=False)
    nickname=db.Column(db.String(20))
    regdate=db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    level=db.Column(db.Integer)

    def __init__(self,index,id,pw,name,college,major,st_num,email,nickname,regdate,level):
        self.index=index
        self.id=id
        self.pw=pw
        self.name=name
        self.college=college
        self.major=major
        self.st_num=st_num
        self.email=email
        self.nickname=nickname
        self.regdate=regdate
        self.level=level
        
class board(db.Model,AddUpdateDelete):
    index=db.Column('idx', db.Integer, primary_key=True)
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

    def __init__(self,index,category,writer,parent,od,depth,subject,content,reg_date,hit,goods):
        self.index=index
        self.category=category
        self.writer=writer
        self.parent=parent
        self.od=od
        self.depth=depth
        self.subject=subject
        self.content=content
        self.reg_date=reg_date
        self.hit=hit
        self.goods=goods

class category(db.Model,AddUpdateDelete):
    index=db.Column('idx', db.Integer, primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    skin=db.Column(db.String(50))

    def __init__(self,index,name,skin):
        self.index=index
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

    def __init__(self,index,board_idx,writer,od,depth,content,date):
        self.index=index
        self.board_idx=board_idx
        self.writer=writer
        self.od=od
        self.depth=depth
        self.content=content
        self.date=date

class cms(db.Model,AddUpdateDelete):
    index=db.Column('idx', db.Integer, primary_key=True)
    content=db.Column(db.VARCHAR(255))
    deposit=db.Column(db.Integer)
    withdraw=db.Column(db.Integer)
    date=db.Column(db.DATE)

    def __init__(self,index,content,deposit,withdraw,date):
        self.index=index
        self.content=content
        self.deposit=deposit
        self.withdraw=withdraw
        self.date=date

#class meta_data(db.Model, AddUpdateDelete):
#    key=db.Column(db.String(20))
#    value=db.Column(db.TEXT)
#
#    def __init__(self, key, value):
#        self.key=key
#        self.value=value

class files(db.Model, AddUpdateDelete):
    index=db.Column('idx', db.Integer, primary_key=True)
    table=db.Column(db.String(20))
    id=db.Column(db.Integer)
    origin_name=db.Column(db.VARCHAR(255))
    file_name=db.Column(db.String(50))
    reg_date=db.Column(db.TIMESTAMP)

    def __init__(self,index,table,id,origin_name,file_name,reg_date):
        self.index=index
        self.table=table
        self.id=id
        self.origin_name=origin_name
        self.file_name=file_name
        self.reg_date=reg_date

