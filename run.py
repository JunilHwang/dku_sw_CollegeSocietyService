#run.py
#run server

from app2 import app

app.run(host=app.config['HOST']),
port=app.config['PORT'],
debug=app.config['DEBUG']