#run.py
#run server

from app2 import create_app
app=create_app('config')    #read settings from config.py

if __name__=='__main__':
    app.run(host=app.config['HOST']),
    port=app.config['PORT'],
    debug=app.config['DEBUG']