#config.py
#configuration of flask app running factors
import os
import datetime
DEBUG=True              #app running debug option. Must off running on operating server.
PORT=5000               #flask app port num
HOST="0.0.0.0"        #flask app host
SQLALCHEMY_TRACK_MODIFICATIONS=False
SQLALCHEMY_COMMIT_ON_TEARDOWN=True
SQLALCHEMY_DATABASE_URI="mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}?charset={CHARSET}"\
    .format(DB_USER=os.environ.get('DB_USER'),DB_PASS=os.environ.get('DB_PASS'),
            DB_ADDR=os.environ.get('DB_ADDR'),DB_NAME=os.environ.get('DB_NAME'),CHARSET="utf8")
    #SQLALCHEMY connection target
BUNDLE_ERRORS=True      #Request Parser Error Handling Option. If true, all errors on request will be returned at once,
                        #while false return only first.
JWT_SECRET_KEY=os.environ.get('JWT_SECRET')
JWT_ACCESS_TOKEN_EXPIRES=datetime.timedelta(hours=1)    #if 'False' token will not revoke
JWT_REFRESH_TOKEN_EXPIRES=False
#secret key for create JSON Web Token. Need to change before service.
MAIL_USERNAME=os.environ.get('MAIL_USERNAME')   #for mail extension
MAIL_PASSWORD=os.environ.get('MAIL_PASS')
FLASKY_MAIL_SUBJECT_PREFIX="[DKUCSS]"
FLASKY_MAIL_SENDER="no-reply@dkswcm.nn"