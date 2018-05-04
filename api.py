#api.py

from flask import jsonify
from flask_restful import Api,Resource,reqparse
from models import *
import status

api=Api()
#class MainPage(Resource):
#    def get(self):
#        return 200

#api.add_resource(MainPage,'/')