#config.py
#configuration of flask app running factors

DEBUG=False              #app running debug option. Must off running on operating server.
PORT=5000               #flask app port num
HOST="0.0.0.0"        #flask app host
SQLALCHEMY_TRACK_MODIFICATIONS=True
SQLALCHEMY_DATABASE_URI="mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}?charset={CHARSET}"\
    .format(DB_USER="root",DB_PASS="14959",DB_ADDR="220.149.235.59:3306",DB_NAME="dkswcm",CHARSET="utf8")
        #SQLALCHEMY connection target
SQLALCHEMY_COMMIT_ON_TEARDOWN=True
BUNDLE_ERRORS=True      #Request Parser Error Handling Option. If true, all errors on request will be returned at once,
                        #while false return only first.
JWT_SECRET_KEY="software" #secret key for create JSON Web Token. Need to change before service.