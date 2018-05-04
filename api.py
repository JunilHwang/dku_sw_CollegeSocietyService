#api.py

from flask import jsonify,request,render_template
from flask_restful import Api,Resource,reqparse
from models import *
import status

api=Api()