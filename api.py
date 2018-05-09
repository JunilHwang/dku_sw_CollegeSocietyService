#api.py

from flask import jsonify, make_response
from flask_restful import Api,Resource,reqparse
from models import *
from sqlalchemy.exc import SQLAlchemyError
import status

api=Api()
class UserResource(Resource):
    def post(self): #add new user
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True)
        parser.add_argument('pw', type=str, required=True)
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('college', type=str, required=True)
        parser.add_argument('major', type=str, required=True)
        parser.add_argument('undergrad_number', type=int, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('nickname', type=str)
        args=parser.parse_args()

        _id=args['id']
        _pw=args['pw']
        _name=args['name']
        _college=args['college']
        _major=args['major']
        _undergrad=args['undergrad_number']
        _email=args['email']
        _nickname=args['nickname']
        
        try:
            new_member=member(_id,_pw,_name,_college,_major,_undergrad,_email,_nickname)
            new_member.add(new_member)

        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_400_BAD_REQUEST
        query=member.query.get(new_member.idx)
        result=query.as_dict()
        del result['regdate']
        return result, status.HTTP_201_CREATED

class ProfileResource(Resource):
    def get(self,idx): #show user info
        current_user=member.query.get_or_404(idx)
        result=current_user.as_dict()
        del result['regdate']
        return result

    def patch(self, idx): #edit user info
        current_user=member.query.get_or_404(idx)

        parser=reqparse.RequestParser()
        #parsing list중 필요없는것 삭제할 것
        parser.add_argument('id', type=str, location='form')
        parser.add_argument('pw', type=str, location='form')
        parser.add_argument('name', type=str, location='form')
        parser.add_argument('college', type=str, location='form')
        parser.add_argument('major', type=str, location='form')
        parser.add_argument('undergrad_number', type=int, location='form')
        parser.add_argument('email', type=str, location='form')
        parser.add_argument('nickname', type=str, location='form')
        args=parser.parse_args()

        _id=args['id']
        _pw=args['pw']
        _name=args['name']
        _college=args['college']
        _major=args['major']
        _undergrad=args['undergrad_number']
        _email=args['email']
        _nickname=args['nickname']

        try:
            if _pw!=None:
                current_user.pw=_pw
            if _college!=None:
                current_user.college=_college
            if _major!=None:
                current_user.major=_major
            if _email!=None:
                current_user.email=_email
            if _nickname!=None:
                current_user.nickname=_nickname
            current_user.update()
            return self.get(idx)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp,status.HTTP_400_BAD_REQUEST

    def delete(self,idx):
        current_user=member.query.get_or_404(idx)
        try:
            current_user.delete(current_user)
            resp={"status":"success"}
            return resp, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp=jsonify({"error":str(e)})
            return resp, status.HTTP_401_UNAUTHORIZED

class BoardResource(Resource):
    def get(self): #show list of post
        pass
        #posts=board.query.all()
        #query to json
        #return
    def post(self): #add new post board
        parser=reqparse.RequestParser()
        parser.add_argument('category', type=int, required=True)
        parser.add_argument('writer', type=int, required=True)
        parser.add_argument('parent', type=int, required=True)
        parser.add_argument('od', type=int, required=True)
        parser.add_argument('depth', type=int, required=True)
        parser.add_argument('subject', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        args=parser.parse_args()

        _category=args['category']
        _writer=args['writer']
        _parent=args['parent']
        _od=args['od']
        _depth=args['depth']
        _subject=args['subject']
        _content=args['content']
        '''
        try:
            new_post=member(_category,_writer,_parent,_od,_major,_depth,_subject,_content)
            new_post.add(new_post)
            추가 됐는지 조회 후, 결과, code201 리턴할 것

        except SQLAlchemyError as e:
            db.session.rollback()
            resp=jsonify({"error":str(e)})
            return resp, status.HTTP_400_BAD_REQUEST
        '''
        #db연동 확인후 아래 리턴문은 삭제
        return {'category':_category,
                'writer':_writer,
                'parent':_parent,
                'od':_od,
                'depth':_depth,
                'subject':_subject,
                'content':_content}, status.HTTP_201_CREATED

class PostResource(Resource):
    def get(self,idx): #show content of post
        pass
        #post=board.query.get_or_404(idx)
        #query to json
        #return

    def patch(self,idx): #edit post
        current_post=board.query.get_or_404(idx)

        parser=reqparse.RequestParser()
        parser.add_argument('category', type=int)
        parser.add_argument('writer', type=int)
        parser.add_argument('parent', type=int)
        parser.add_argument('od', type=int)
        parser.add_argument('depth', type=int)
        parser.add_argument('subject', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        args=parser.parse_args()

        _category=args['category']
        _writer=args['writer']
        _parent=args['parent']
        _od=args['od']
        _depth=args['depth']
        _subject=args['subject']
        _content=args['content']

        try:
            current_post.subject=args['subject']
            current_post.content=args['content']
            current_post.session.update()
        except SQLAlchemyError as e:
            db.session.rollback()
            resp=nsonify({"error":str(e)})
            return resp,status.HTTP_400_BAD_REQUEST

    def delete(self,idx): #delete post
        current_post=board.query.get_or_404(idx)
        try:
            current_post.delete(current_post)
            response=make_response()
            return response, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp=jsonify({"error":str(e)})
            return resp, status.HTTP_401_UNAUTHORIZED

class CommentListResource(Resource):
    def get(self,idx):  #show comment list of the post
        pass
        #comments=comment.query.flter_by().all()
        #query to json
        #return

    def post(self,idx): #add new comment on post
        parser=reqparse.RequestParser()
        parser.add_argument('bidx', type=int, required=True)
        parser.add_argument('writer', type=int, required=True)
        parser.add_argument('od', type=int, required=True)
        parser.add_argument('depth', type=int, required=True)
        parser.add_argument('content', type=str, required=True)
        args=parser.parse_args()

        _bidx=args['bidx']
        _writer=args['writer']
        _od=args['od']
        _depth=['depth']
        _content=['content']
        '''
        try:
            new_comment=member(_bidx,_writer,_od,_depth,_content)
            new_comment.add(new_comment)
            추가 됐는지 조회 후, 결과, code201 리턴할 것

        except SQLAlchemyError as e:
            db.session.rollback()
            resp=jsonify({"error":str(e)})
            return resp, status.HTTP_400_BAD_REQUEST
        '''
        #db연동 확인후 아래 리턴문은 삭제
        return {'bidx':_bidx,
                'writer':_writer,
                'od':_od,
                'depth':_depth,
                'content':_content}, status.HTTP_201_CREATED

class CommentResource(Resource):
    def put(self,comment_idx): #edit comment
        current_comment=comment.query.get_or_404(comment_idx)
        
        parser=reqparse.RequestParser()
        parser.add_argument('bidx', type=int)
        parser.add_argument('writer', type=int)
        parser.add_argument('od', type=int)
        parser.add_argument('depth', type=int)
        parser.add_argument('content', type=str, required=True)
        args=parser.parse_args()

        try:
            current_comment.content=args['content']
            current_comment.session.update()
        except SQLAlchemyError as e:
            db.session.rollback()
            resp=nsonify({"error":str(e)})
            return resp,status.HTTP_400_BAD_REQUEST

    def delete(self,comment_idx):   #delete comment
        current_comment=comment.query.get_or_404(comment_idx)
        try:
            current_comment.delete(current_comment)
            response=make_response()
            return response, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp=jsonify({"error":str(e)})
            return resp, status.HTTP_401_UNAUTHORIZED



api.add_resource(UserResource,'/member')
api.add_resource(ProfileResource,'/member/<idx>')
api.add_resource(BoardResource,'/board/<category>')
api.add_resource(PostResource,'/board/<idx>')
api.add_resource(CommentListResource,'/board/<post_idx>/comments')
api.add_resource(CommentResource,'/board/<post_idx>/comments/<comment_idx>')