#api.py

from flask import jsonify
from flask_restful import Api,Resource,reqparse
from models import *
from sqlalchemy.exc import SQLAlchemyError
import status

api=Api()
class UserResource(Resource):
    def post(self): #add new user
        try:
            parser=reqparse.RequestParser()
            parser.add_argument('id',type=str)
            parser.add_argument('pw',type=str)
            parser.add_argument('name',type=str)
            parser.add_argument('college',type=str)
            parser.add_argument('major',type=str)
            parser.add_argument('undergrad_number',type=int)
            parser.add_argument('email',type=str)
            parser.add_argument('nickname',type=str)
            args=parser.parse_args()
        except Exception as e:
            resp = jsonify({"error" : "No input data provided"})
            return resp, status.HTTP_400_BAD_REQUEST

        _id=args['id']
        _pw=args['pw']
        _name=args['name']
        _college=args['college']
        _major=args['major']
        _undergrad=args['undergrad_number']
        _email=args['email']
        _nickname=args['nickname']

        #try:
        #    new_member=member(_id,_pw,_name,_college,_major,_undergrad,_email,_nickname)
        #    new_member.add(new_member)
        #    추가 됐는지 조회 후, 결과, code201 리턴할 것

        #except SQLAlchemyError as e:
        #    db.session.rollback()
        #    resp=jsonify({"error":str(e)})
        #    return resp, status.HTTP_400_BAD_REQUEST
        
        return {'id':_id,
                'pw':_pw,
                'name':_name,
                'college':_college,
                'major':_major,
                'undergrad_number':_undergrad,
                'email':_email,
                'nickname':_nickname}, status.HTTP_201_CREATED

class ProfileResource(Resource):
    def get(self): #show user info
        pass
    def patch(self): #edit user info
        pass

class BoardResource(Resource):
    def get(self): #show list of post
        pass
    def post(self): #add new post on board
        pass

class PostResource(Resource):
    def get(self): #show content of post
        pass
    def patch(self): #edit post
        pass
    def delete(): #delete post
        pass

class CommentListResource(Resource):
    def get(self):  #show comment list of the post
        pass
    def post(self): #add new comment on post
        pass

class CommentResource(Resource):
    def patch(self): #edit comment
        pass


api.add_resource(UserResource,'/member')
api.add_resource(ProfileResource,'/member/<idx>')
api.add_resource(BoardResource,'/board/<category>')
api.add_resource(PostResource,'/board/<idx>')
api.add_resource(CommentListResource,'/comments')
api.add_resource(CommentResource,'/comments/<idx>')