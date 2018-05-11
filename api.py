#api.py
'''
<To Do List> - 18.05.11
user입력,변경시 validation추가
cms,meta_data,file 테이블에 대한 api추가
http인증
파일처리(?)
'''
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
            return jsonify(resp), status.HTTP_400_BAD_REQUEST
        query=member.query.get(new_member.idx)
        result=query.as_dict()

        return jsonify(result), status.HTTP_201_CREATED
   
    def get(self):      #show all users
        query=member.query.all()
        result=many_returns(query)
        for x in result:
            x['regdate']=str(x['regdate'])
        return jsonify(result)


class ProfileResource(Resource):
    def get(self,idx): #show user info
        current_user=member.query.get_or_404(idx)
        result=current_user.as_dict()
        result['regdate']=str(result['regdate'])
        return jsonify(result)

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
            if _pw is not None:
                current_user.pw=_pw
            if _college is not None:
                current_user.college=_college
            if _major is not None:
                current_user.major=_major
            if _email is not None:
                current_user.email=_email
            if _nickname is not None:
                current_user.nickname=_nickname
            current_user.update()
            return jsonify({'idx':self.get(idx)})
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp,status.HTTP_400_BAD_REQUEST

    def delete(self,idx):
        current_user=member.query.get_or_404(idx)
        try:
            current_user.delete(current_user)
            return True, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_401_UNAUTHORIZED

class CategoryResource(Resource):
    def get(self):
        query=category.query.all()
        result=many_returns(query)
        
        return result

class BoardResource(Resource):
    def get(self, cate): #show list of post
        ctg=category.query.filter_by(idx=cate).first()
        if ctg is None:
            return {"error":"Category doesn't exist."}
        query=board.query.filter_by(category=ctg.idx).order_by(board.reg_date).all()
        result=many_returns(query)
        for x in result:
            x['reg_date']=str(x['reg_date'])
        return jsonify(result)

    def post(self, cate): #add new post board
        ctg=category.query.filter_by(idx=cate).first()
        if ctg is None:
            return {"error":"Category doesn't exist."}, status.HTTP_406_NOT_ACCEPTABLE

        parser=reqparse.RequestParser()
        parser.add_argument('writer', type=int, required=True)
        parser.add_argument('parent', type=int, required=True)
        parser.add_argument('od', type=int, required=True)
        parser.add_argument('depth', type=int, required=True)
        parser.add_argument('subject', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        args=parser.parse_args()

        _writer=args['writer']
        _parent=args['parent']
        _od=args['od']
        _depth=args['depth']
        _subject=args['subject']
        _content=args['content']
        
        mem=member.query.filter_by(idx=_writer).first()
        
        try:
            new_post=board(cate,_writer,_parent,_od,_depth,_subject,_content)
            new_post.add(new_post)

        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_400_BAD_REQUEST

        query=board.query.get(new_post.idx)
        result=query.as_dict()
        result['reg_date']=str(result['reg_date'])
        return result, status.HTTP_201_CREATED

class PostResource(Resource):
    def get(self,cate,idx): #show content of post
        current_post=board.query.filter_by(category=cate,idx=idx).first()
        if current_post is None:
            return {"error":"Resource Not Founded"}, status.HTTP_404_NOT_FOUND
        result=current_post.as_dict()
        result['reg_date']=str(result['reg_date'])
        return result

    def patch(self,cate,idx): #edit post
        current_post=board.query.filter_by(category=cate,idx=idx).first()
        if current_post is None:
            return {"error":"Resource Not Founded"}, status.HTTP_404_NOT_FOUND

        parser=reqparse.RequestParser()
        parser.add_argument('subject', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        args=parser.parse_args()

        try:
            current_post.subject=args['subject']
            current_post.content=args['content']
            current_post.update()
            return jsonify({'idx':current_post.idx})

        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_400_BAD_REQUEST

    def delete(self,cate,idx): #delete post
        current_post=board.query.filter_by(category=cate,idx=idx).first()
        if current_post is None:
            return {"error":"Resource Not Founded"}, status.HTTP_404_NOT_FOUND
        try:
            current_post.delete(current_post)
            return True, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_401_UNAUTHORIZED

class CommentListResource(Resource):
    def get(self,post_idx):  #show comment list of the post
        pst=board.query.filter_by(idx=post_idx).first()
        if pst is None:
            return {"error":"Post doesn't exist"}, status.HTTP_406_NOT_ACCEPTABLE
        comments=comment.query.filter_by(bidx=pst.idx).all()
        result=many_returns(comments)
        
        for x in result:
            x['date']=str(x['date'])
        return jsonify(result)

    def post(self,post_idx): #add new comment on post
        pst=board.query.filter_by(idx=post_idx).first()
        if pst is None:
            return {"error":"Post doesn't exist"}, status.HTTP_406_NOT_ACCEPTABLE
        parser=reqparse.RequestParser()
        parser.add_argument('writer', type=int, required=True)
        parser.add_argument('od', type=int, required=True)
        parser.add_argument('depth', type=int, required=True)
        parser.add_argument('content', type=str, required=True)
        args=parser.parse_args()

        _writer=args['writer']
        _od=args['od']
        _depth=args['depth']
        _content=args['content']
        
        try:
            new_comment=comment(post_idx,_writer,_od,_depth,_content)
            new_comment.add(new_comment)

        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_400_BAD_REQUEST
        
        query=comment.query.get(new_comment.idx)
        result=query.as_dict()
        result['date']=str(result['date'])
        return jsonify(result), status.HTTP_201_CREATED

class CommentResource(Resource):
    def patch(self, comment_idx): #edit comment
        current_comment=comment.query.get_or_404(comment_idx)
        
        parser=reqparse.RequestParser()
        parser.add_argument('content', type=str, required=True)
        args=parser.parse_args()

        try:
            current_comment.content=args['content']
            current_comment.update()
            return jsonify({'idx':current_comment.idx})
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp,status.HTTP_400_BAD_REQUEST

    def delete(self, comment_idx):   #delete comment
        current_comment=comment.query.get_or_404(comment_idx)
        try:
            current_comment.delete(current_comment)
            return True, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_401_UNAUTHORIZED



api.add_resource(UserResource,'/member')
api.add_resource(ProfileResource,'/member/<int:idx>')
api.add_resource(CategoryResource,'/CategoryList')
api.add_resource(BoardResource,'/board/<int:cate>')
api.add_resource(PostResource,'/post/<int:cate>/<int:idx>')
api.add_resource(CommentListResource,'/post/<int:post_idx>/comments')
api.add_resource(CommentResource,'/comments/<int:comment_idx>')