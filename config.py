#config.py
#configuration of flask app running factors

DEBUG=True              #app running debug option
PORT=5000               #flask app port num
HOST="127.0.0.1"        #flask app host
SQLALCHEMY_TRACK_MODIFICATIONS=True
SQLALCHEMY_DATABASE_URI="mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}?charset={CHARSET}"\
    .format(DB_USER="root",DB_PASS="14959",DB_ADDR="220.149.235.59:3306",DB_NAME="dkswcm",CHARSET="utf8")
        #SQLALCHEMY connection target
