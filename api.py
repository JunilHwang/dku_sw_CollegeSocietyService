#-*- coding: utf-8 -*-
#api.py
'''
HTTP Basic Auth에서
JWT(JSON Web Token)인증으로 변경. 기존 코드는 유지
How to make logout process with JWT?

2018.05.27
db접속 정보,jwt키,메일계정 등의 보안사항을 스크립트에서 제거하고
환경변수를 load하는것으로 수정.
허접한 메일 인증 추가
(MailAuthenticaion class의 redirect 주소, mail.py의 url확인)
access token과 refresh token 기본 만료 시간을 1시간, 무제한으로 변경
'''
'''
사용자등록, 전체 목록 : /member
사용자 정보 변경, 삭제 : /member/<사용자 idx>
카테고리 : /CategoryList
게시글 목록, 추가: /board/<category_id>
게시글 수정, 삭제: /board/<category_id>/<게시글 idx>
댓글 목록, 추가: /board/<게시글 idx>/comments
댓글 수정, 삭제: /comments/<댓글 idx>
교수 목록: /professor
교수 개별: /professor/<교수 idx>

'''

from flask import jsonify, redirect
from flask_restful import Api,Resource,reqparse
from models import *
from auth import *
from mail import send_email,title
from sqlalchemy import or_
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
        
        query=member.query
        if query.filter_by(id=_id).first() is not None:    #입력 id가 이미 존재할때
            return {"error": "User with the same ID already exists"}, status.HTTP_400_BAD_REQUEST
        if query.filter_by(nickname=_nickname).first() is not None: #중복 닉네임
            return {"error": "User with the same nickname already exists"}, status.HTTP_400_BAD_REQUEST
        if query.filter_by(undergrad_number=_undergrad).first() is not None:    #1인 1아이디
            return {"error": "User with the student id already exists"}
        if not _email[:8] == str(_undergrad):
            return {"error": "The email doesn't match with undergrad_number"}
        if not _email[9:] == "dankook.ac.kr":
            return {"error": "The email should use dankook university email for student authentication"}

        try:
            new_member=member(_id,_name,_college,_major,_email,_nickname)
            error_message, pw_ok = \
                new_member.check_password_strength_and_hash_if_ok(_pw) #패스워드 유효성 체크, 만족시 해시 함수 적용.
            if pw_ok:
                new_member.add(new_member)      #member추가
                query=member.query.get(new_member.idx)  #추가된 새 member에 대한 정보를 받아옴
                result=query.as_dict()                  #<---필요한 attribute만 남기고 리턴할 것
                del result['pw']
                result['regdate']=str(result['regdate'])
                send_email(_email,title,result)
                return result, status.HTTP_201_CREATED
            else:
                return {"error":error_message}, status.HTTP_400_BAD_REQUEST
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_400_BAD_REQUEST
          
    #@jwt_required               #admin만 접근 가능해야함
    #def get(self):      #show all users
    #    query=member.query.all()
    #    result=many_returns(query)
    #    for x in result:
    #        x['regdate']=str(x['regdate'])
    #    return jsonify(result)

class MailAuthentication(Resource):
    def get(self,user_idx):
        try:
            ma_mem=member.query.filter_by(idx=user_idx).first()
            ma_mem.mail_auth_complete(ma_mem.email[:8])
            ma_mem.update()
            return redirect("http://www.google.com",302)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_400_BAD_REQUEST

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
        print(identity)
        print(current_user.id)
        if identity != current_user.id:    
            return {'error':'Not allowed to access this resource'}, status.HTTP_403_FORBIDDEN

        parser=reqparse.RequestParser()
        #parsing list중 필요없는것 삭제할 것
        parser.add_argument('pw', type=str)
        parser.add_argument('college', type=str)
        parser.add_argument('major', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('nickname', type=str)
        args=parser.parse_args()

        _pw=args['pw']
        _college=args['college']
        _major=args['major']
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
        if identity != current_user.id:        #인증과 삭제할 유저의 id가 일치하지 않을 때
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
        ctg=category.query.filter_by(id=cate).first()
        if ctg is None:
            return {"error":"Category doesn't exist."}, status.HTTP_404_NOT_FOUND
        query=board.query.filter_by(category=ctg.id).order_by(board.reg_date).all()
        result=many_returns(query)
        nick=[sq.author.nickname for sq in query]
        for i in range(len(result)):
            result[i]['nickname']=nick[i]
            result[i]['reg_date']=str(result[i]['reg_date'])
        return jsonify(result)

    @jwt_required
    def post(self, cate): #add new post board
        ctg=category.query.filter_by(id=cate).first()
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
        current_post.hit+=1         #조회수 +1
        current_post.update()
        
        result=current_post.as_dict()
        result['reg_date']=str(result['reg_date'])
        if current_post.writer is not None:
            result['nickname']=current_post.author.nickname
        else:
            result['nickname']="탈퇴회원"
        return result

    @jwt_required
    def patch(self,cate,idx): #edit post
        current_post=board.query.filter_by(category=cate,idx=idx).first()
        if current_post is None:
            return {"error":"Resource Not Founded"}, status.HTTP_404_NOT_FOUND
        claims=get_jwt_claims()
        if claims['index'] is not current_post.writer:       #인증과 수정할 post의 작성자가 일치하지 않을 때
            return {"error":'Not allowed to access this resource'}, status.HTTP_403_FORBIDDEN

        parser=reqparse.RequestParser()
        parser.add_argument('subject', type=str)
        parser.add_argument('content', type=str)
        parser.add_argument('goods', type=str)
        args=parser.parse_args()

        try:
            if args['subject'] is not None:
                current_post.subject=args['subject']
            if args['content'] is not None:
                current_post.content=args['content']
            if args['goods'] is not None:
                current_post.goods+=1
            current_post.update()
            return jsonify({'idx':current_post.idx})

        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_400_BAD_REQUEST

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
        nick=[sq.author.nickname for sq in comments]
        for i in range(len(result)):
            if result[i]['writer'] is not None:
                result[i]['nickname']=nick[i]
            else:
                result[i]['nickname']="탈퇴회원"
            result[i]['date']=str(result[i]['date'])
        return jsonify(result)

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
        result={'idx':query.idx}
        return result, status.HTTP_201_CREATED

class CommentResource(Resource):
    @jwt_required
    def patch(self, comment_idx): #edit comment
        current_comment=comment.query.get_or_404(comment_idx)
        claims=get_jwt_claims()
        if claims['index'] != current_comment.writer:    #인증과 수정할 comment의 작성자가 일치하지 않을때
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
    
    @jwt_required
    def delete(self, comment_idx):   #delete comment
        current_comment=comment.query.get_or_404(comment_idx)
        claims=get_jwt_claims()
        if claims['index'] != current_comment.writer:        #인증과 삭제할 comment의 작성자가 일치하지 않을때
            return {"error":"Not allowed to access this resource"}, status.HTTP_403_FORBIDDEN
        try:
            current_comment.delete(current_comment)
            return True, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp={"error":str(e)}
            return resp, status.HTTP_401_UNAUTHORIZED

class ProfessorListResource(Resource):
    def get(self):
        prof=professor.query.all()
        result=many_returns(prof)
        for x in result:
            f=files.query.filter_by(idx=x['idx'],table="professor").first()
            x['origin_name']=f.origin_name
            x['file_name']=f.file_name
        return jsonify(result)

class ProfessorResource(Resource):
    def get(self,idx):
        prof=professor.query.filter_by(idx=idx).first()
        result=prof.as_dict()
        f=files.query.filter_by(idx=prof.idx).first()
        result['origin_name']=f.origin_name
        result['file_name']=f.file_name
        return jsonify(result)

class GetToken(Resource):   #로그인 시 access token, refresh token생성
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id', type=str)
        parser.add_argument('pw', type=str)
        args=parser.parse_args()
        id=args['id']
        pw=args['pw']
        user=member.query.filter_by(id=id).first()

        if user.undergrad_number == 0:
            return {"error":"Student Mail Authentication Not Completed"}, status.HTTP_401_UNAUTHORIZED
        if not user or not user.verify_password(pw):
            return {"error":"User doesn't exist"}, status.HTTP_401_UNAUTHORIZED
        if not user.verify_password(pw):
            return {"error":"password invalid"}, status.HTTP_401_UNAUTHORIZED
        access_token=create_access_token(identity=id)   #1시간  
        refresh_token=create_refresh_token(identity=id) #30일    
        #config.py에서 변경하거나
        #매개변수에 expires_delta=[datetime.timedelta object]로 설정할 수 있음
        return jsonify({'access_token':access_token, 'refresh_token':refresh_token})

class RefreshToken(Resource):   #access token이 만료 되었을 때 refresh token을 이용하여 새 access token 발급
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}

class TestResource(Resource):   #인증 테스트용. 나중에 삭제 바람
    @jwt_required
    def get(self):
        claims=get_jwt_claims()
        return jsonify({claims[id]:claims[index]})

class MailTest(Resource):       #메일 테스트용. 나중에 삭제 바람
    def get(self):
        aaa={}
        aaa['id']="asdf"
        aaa['nickname']="nicknick"
        aaa['email']="test@test.kr"
        send_email("32131752@dankook.ac.kr",title,aaa)

api.add_resource(UserResource,'/member')
api.add_resource(ProfileResource,'/member/<int:idx>')
api.add_resource(CategoryResource,'/CategoryList')
api.add_resource(BoardResource,'/board/<cate>')
api.add_resource(PostResource,'/board/<cate>/<int:idx>')
api.add_resource(CommentListResource,'/board/<int:post_idx>/comments')
api.add_resource(CommentResource,'/comments/<int:comment_idx>')
api.add_resource(ProfessorListResource,'/professor')
api.add_resource(ProfessorResource,'/professor/<int:idx>')

api.add_resource(GetToken,'/token')
api.add_resource(RefreshToken,'/refresh_token')
api.add_resource(MailAuthentication,'/mailauth/<user_idx>')

api.add_resource(TestResource,'/test')      #테스트 후 삭제 바람
api.add_resource(MailTest,'/mail')          #테스트 후 삭제 바람