#api.py

from flask import jsonify
from flask_restful import Api,Resource,reqparse
from models import *
import status

api=Api()
class UserResource(Resource):
    def post(self): #add new user
        pass

class ProfileResource(Resource):
    def post(self): #edit user info
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
    def post(self): #edit comment
        pass


api.add_resource(UserResource,'/member')
api.add_resource(ProfileResource,'/member/<idx>')
api.add_resource(BoardResource,'/board/<category>')
api.add_resource(PostResource,'/board/<idx>')
api.add_resource(CommentListResource,'/comments')
api.add_resource(CommentResource,'/comments/<idx>')