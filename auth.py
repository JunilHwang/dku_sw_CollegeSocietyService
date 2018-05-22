#-*- coding: utf-8 -*-
from flask import g
from flask_restful import Resource
from flask_httpauth import HTTPBasicAuth        #for http authentication
from flask_jwt_extended import JWTManager, jwt_required
from models import member

auth=HTTPBasicAuth()
jwt=JWTManager()

@auth.verify_password
def verify_user_password(id,pw):
    user=member.query.filter_by(id=id).first()
    if not user or not user.verify_password(pw):
        return False
    g.user=user
    return True

class AuthRequiredResource(Resource):
    #method_decorators=[auth.login_required]
    method_decorators=[jwt_required]

@auth.error_handler
def auth_error():
    return "Wrong ID/Password. Access Denied."

@jwt.user_claims_loader     #토큰 생성시 추가적인 정보를 토큰에 담는다.
def add_claims_to_access_token(identity):   #user id와 nickname, index를 포함
    query=member.query.filter_by(id=identity).first()
    return {
        "id":identity,
        "index":query.idx,
        "nickname":query.nickname
        }