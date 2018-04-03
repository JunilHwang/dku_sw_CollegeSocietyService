from flask import Flask, render_template,request,json
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

con = None
cursor = None

def getCursor() :
	global con, cursor
	con = pymysql.connect(
		host='localhost',
		user='root',
		password='nif',
		db='20180403',
		autocommit=True,
		charset='utf8'
	)
	cursor = con.cursor(pymysql.cursors.DictCursor)

def closeCon() :
	con.close()

@app.route("/")
def main() :
	return render_template("index.html")

@app.route("/boardInsert", methods=['POST'])
def boardInsert() :
	_name = request.form['name']
	_subject = request.form['subject']
	_content = request.form['content']
	sql = "INSERT INTO board SET name=%s, subject=%s, content=%s, date=now();"
	getCursor()
	cursor.execute(sql,(_name,_subject,_content))
	lastid = cursor.lastrowid
	closeCon()
	return json.dumps({"lastid":lastid})

@app.route("/boardList")
def boardList() :
	sql = "SELECT * FROM board";
	getCursor()
	cursor.execute(sql)
	data = cursor.fetchall()
	closeCon()
	return json.dumps(data)

@app.route("/boardView")
def boardView() :
	sql = "SELECT * FROM board order by idx desc limit 1";
	getCursor();
	cursor.execute(sql)
	data = cursor.fetchone()
	closeCon();
	return json.dumps(data)



if __name__ == "__main__" : 
	app.run(host='0.0.0.0');