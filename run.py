#run.py
#run server

from app2 import app
import views

if __name__=='__main__':
    app.run(host=app.config['HOST']),
    port=app.config['PORT'],
    debug=app.config['DEBUG']