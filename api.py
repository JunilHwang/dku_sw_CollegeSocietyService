#api.py
'''
HTTP Basic Auth에서
JWT(JSON Web Token)인증으로 변경.
'''

from flask import jsonify
from flask_restful import Api,Resource,reqparse
from models import *
from auth import *
from sqlalchemy.exc import SQLAlchemyError
import status
from flask_jwt_extended import (create_access_token,
                                create_refresh_token, jwt_required,
                                jwt_refresh_token_required, get_jwt_claims,
                                get_jwt_identity, get_raw_jwt)

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
        
        exist_id=member.query.filter_by(id=_id).first()
        if exist_id is not None:    #입력 id가 이미 존재할때
            return {"error": "User with the same ID already exists"}, status.HTTP_400_BAD_REQUEST
        try:
            new_member=member(_id,_name,_college,_major,_undergrad,_email,_nickname)
            error_message, pw_ok = \
                new_member.check_password_strength_and_hash_if_ok(_pw) #패스워드 유효성 체크, 만족시 해시 함수 적용.
            if pw_ok:
                new_member.add(new_member)      #member추가
                query=member.query.get(new_member.idx)  #추가된 새 member에 대한 정보를 받아옴
                result=query.as_dict()                  #<---필요한 attribute만 남기고 리턴할 것
                return result, status.HTTP_201_CREATED
            else:
                return {"error":error_message}, status.HTTP_400_BAD_REQUEST
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_400_BAD_REQUEST
    
    #@auth.login_required        #admin만 접근 가능해야함
    @jwt_required
    def get(self):      #show all users
        query=member.query.all()
        result=many_returns(query)
        for x in result:
            x['regdate']=str(x['regdate'])
        return jsonify(result)


class ProfileResource(AuthRequiredResource):    #해당 클래스 자원은 모두 인증이 필요
    def get(self,idx): #show user info
        identity=get_jwt_identity()
        current_user=member.query.get_or_404(idx)
        
        if identity==current_user.id:
            result=current_user.as_dict()
            result['regdate']=str(result['regdate'])
            del result['pw']        #응답에서 password 항목 삭제
            return jsonify(result)
        else:
            return {'error':'Not allowed to access this resource'}, status.HTTP_403_FORBIDDEN

    def patch(self, idx): #edit user info
        identity=get_jwt_identity()
        current_user=member.query.get_or_404(idx)
        if identity is not current_user.id:    
            return {'error':'Not allowed to access this resource'}, status.HTTP_403_FORBIDDEN

        parser=reqparse.RequestParser()
        #parsing list중 필요없는것 삭제할 것
        parser.add_argument('id', type=str)
        parser.add_argument('pw', type=str)
        parser.add_argument('name', type=str)
        parser.add_argument('college', type=str)
        parser.add_argument('major', type=str)
        parser.add_argument('undergrad_number', type=int)
        parser.add_argument('email', type=str)
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
            if _pw is not None:
                error_message, pw_ok = \
                current_user.check_password_strength_and_hash_if_ok(_pw)    #패스워드 유효성체크 및 암호화
                if pw_ok is False:
                    return {"error":error_message}, status.HTTP_400_BAD_REQUEST
            if _college is not None:
                current_user.college=_college
            if _major is not None:
                current_user.major=_major
            if _email is not None:
                current_user.email=_email
            if _nickname is not None:
                current_user.nickname=_nickname
            current_user.update()
            return {"idx":current_user.idx}

        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_400_BAD_REQUEST
    
    def delete(self,idx):
        identity=get_jwt_identity()
        current_user=member.query.get_or_404(idx)
        if identity is not current_user.id:        #인증과 삭제할 유저의 id가 일치하지 않을 때
            return {"error":"Not allowed to access this resource"}, status.HTTP_403_FORBIDDEN
        try:
            current_user.delete(current_user)
            return True, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_401_UNAUTHORIZED

class CategoryResource(Resource):
    def get(self):      #category정보를 리턴
        query=category.query.all()
        result=many_returns(query)
        return jsonify(result)

class BoardResource(Resource):
    def get(self, cate): #show list of post
        ctg=category.query.filter_by(idx=cate).first()
        if ctg is None:
            return {"error":"Category doesn't exist."}, status.HTTP_404_NOT_FOUND
        query=board.query.filter_by(category=ctg.idx).order_by(board.reg_date).all()
        result=many_returns(query)
        for x in result:
            x['reg_date']=str(x['reg_date'])
        return jsonify(result)

    #@auth.login_required
    @jwt_required
    def post(self, cate): #add new post board
        ctg=category.query.filter_by(idx=cate).first()
        if ctg is None:
            return {"error":"Category doesn't exist."}, status.HTTP_404_NOT_FOUND

        parser=reqparse.RequestParser()
        parser.add_argument('parent', type=int, required=True)
        parser.add_argument('od', type=int, required=True)
        parser.add_argument('depth', type=int, required=True)
        parser.add_argument('subject', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        args=parser.parse_args()

        claims=get_jwt_claims()
        _writer=claims['index']
        _parent=args['parent']
        _od=args['od']
        _depth=args['depth']
        _subject=args['subject']
        _content=args['content']
        
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

    #@auth.login_required
    @jwt_required
    def patch(self,cate,idx): #edit post
        current_post=board.query.filter_by(category=cate,idx=idx).first()
        if current_post is None:
            return {"error":"Resource Not Founded"}, status.HTTP_404_NOT_FOUND
        claims=get_jwt_claims()
        if claims['index'] is not current_post.writer:       #인증과 수정할 post의 작성자가 일치하지 않을 때
            return {"error":'Not allowed to access this resource'}, status.HTTP_403_FORBIDDEN

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

    #@auth.login_required
    @jwt_required
    def delete(self,cate,idx): #delete post
        current_post=board.query.filter_by(category=cate,idx=idx).first()
        if current_post is None:
            return {"error":"Resource Not Founded"}, status.HTTP_404_NOT_FOUND
        claims=get_jwt_claims()
        if claims['index'] is not current_post.writer:       #인증과 삭제할 post의 작성자가 일치하지 않을때
            return {"error":"Not allowed to access this resource"}, status.HTTP_403_FORBIDDEN
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
            return {"error":"Post doesn't exist"}, status.HTTP_404_NOT_FOUND
        comments=comment.query.filter_by(bidx=pst.idx).all()
        result=many_returns(comments)
        
        for x in result:
            x['date']=str(x['date'])
        return jsonify(result)

    #@auth.login_required
    @jwt_required
    def post(self,post_idx): #add new comment on post
        pst=board.query.filter_by(idx=post_idx).first()
        if pst is None:
            return {"error":"Post doesn't exist"}, status.HTTP_404_NOT_FOUND
        parser=reqparse.RequestParser()
        parser.add_argument('od', type=int, required=True)
        parser.add_argument('depth', type=int, required=True)
        parser.add_argument('content', type=str, required=True)
        args=parser.parse_args()

        claims=get_jwt_claims()
        _writer=claims['index']
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
    #@auth.login_required
    @jwt_required
    def patch(self, comment_idx): #edit comment
        current_comment=comment.query.get_or_404(comment_idx)
        claims=get_jwt_claims()
        if claims['index'] is not current_comment.writer:    #인증과 수정할 comment의 작성자가 일치하지 않을때
            return {"error":"Not allowed to access this resource"}, status.HTTP_403_FORBIDDEN
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
    
    #@auth.login_required
    @jwt_required
    def delete(self, comment_idx):   #delete comment
        current_comment=comment.query.get_or_404(comment_idx)
        claims=get_jwt_claims()
        if claims['index'] is not current_comment.writer:        #인증과 삭제할 comment의 작성자가 일치하지 않을때
            return {"error":"Not allowed to access this resource"}, status.HTTP_403_FORBIDDEN
        try:
            current_comment.delete(current_comment)
            return True, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_401_UNAUTHORIZED


class TestResource(Resource):
    @jwt_required
    def get(self):
        claims=get_jwt_claims()
        print(claims['id'])
        print(claims['index'])
        return jsonify({"hello":"world"})

class GetToken(Resource):
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=str)
        parser.add_argument('pw', type=str)
        args=parser.parse_args()
        id=args['id']
        pw=args['pw']
        user=member.query.filter_by(id=id).first()

        if not user or not user.verify_password(pw):
            return {"error":"User doesn't exist"}, status.HTTP_401_UNAUTHORIZED
        if not user.verify_password(pw):
            return {"error":"password invalid"}, status.HTTP_401_UNAUTHORIZED
        access_token=create_access_token(identity=id)
        refresh_token=create_refresh_token(identity=id)

        return jsonify({'access_token':access_token, 'refresh_token':refresh_token})

class RefreshToken(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}

api.add_resource(UserResource,'/member')
api.add_resource(ProfileResource,'/member/<int:idx>')
api.add_resource(CategoryResource,'/CategoryList')
api.add_resource(BoardResource,'/board/<int:cate>')
api.add_resource(PostResource,'/board/<int:cate>/<int:idx>')
api.add_resource(CommentListResource,'/board/<int:post_idx>/comments')
api.add_resource(CommentResource,'/comments/<int:comment_idx>')
api.add_resource(TestResource,'/test')
api.add_resource(GetToken,'/token')
api.add_resource(RefreshToken,'/refresh_token')