# -*- coding: utf-8 -*-
# 한글 인코딩은 위와 같이 주석으로 적용해야함.
# render template : html 불러오기
# request : 사용자 요청
# json : string to json
# pymysql : python mysql
# CORS : 외부 포트 접근 허용
from flask import Flask, render_template,request,json
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

# 전역 변수 지정
con = None
cursor = None

# DB 접속
def getCursor() :
	global con, cursor
	con = pymysql.connect(
		host='localhost',	# DB HOST
		user='root', 		# DB USER
		password='nif',     # DB PW
		db='20180403',		# DB NAME
		autocommit=True, 	# python은 query 실행 후 commit을 해줘야 하는데, 이렇게 지정하면 자동으로 해줌
		charset='utf8'		# 문자열 세팅은 utf8로
	)
	cursor = con.cursor(pymysql.cursors.DictCursor)	 # 전역변수로 커서 생성, DictCursor : 결과를 dictionary 형태로 받아옴

# DB 연결 종료
def closeCon() :
	con.close()

# 메인페이지
@app.route("/")
def main() :
	# 렌더링 페이지 지정
	return render_template("index.html")

# 게시물 목록
@app.route("/boardList")
def boardList() :
	# list 쿼리문
	sql = "SELECT * FROM board order by `date` desc";
	getCursor()	# DB 연결
	cursor.execute(sql) # 쿼리문 실행
	data = cursor.fetchall() # 실행 결과 목록 가져오기
	closeCon() # 연결 종료
	return json.dumps(data) # 실행 결과를 json으로 반환
	
# boardInsert 접근시 게시물 추가 후 추가된 index값 반환
@app.route("/boardInsert", methods=['POST'])
def boardInsert() :
	_name = request.form['name']		# 사용자가 입력한 name 값
	_subject = request.form['subject']	# 사용자가 입력한 subject 값
	_content = request.form['content']	# 사용자가 입력한 content 값
	sql = "INSERT INTO board SET name=%s, subject=%s, content=%s, date=now();" # query문 작성0
	getCursor()	# DB 연결
	cursor.execute(sql,(_name,_subject,_content))	# 각 %s를 _name, _subject, _content로 치환
	lastid = cursor.lastrowid	# 추가된 데이터의 index 값
	closeCon()	# DB 연결 종료
	return json.dumps({"lastid":lastid})	# index값 반환

# /boardView 접근시 해당 게시물 데이터 반환
@app.route("/boardView/<idx>")
def boardView(idx) :
	sql = "SELECT * FROM board where idx=%s";
	getCursor();
	cursor.execute(sql,(idx))
	data = cursor.fetchone()
	closeCon();
	return json.dumps(data)

# /boardUpdate 접근시 해당 게시물 데이터 업데이트 및 반환
@app.route("/boardUpdate/<idx>", methods=['POST'])
def boardUpdate(idx) :
	_name = request.form['name']
	_subject = request.form['subject']
	_content = request.form['content']
	sql = "UPDATE board SET name=%s, subject=%s, content=%s where idx=%s;"
	getCursor()
	cursor.execute(sql,(_name,_subject,_content,idx))
	closeCon()
	return boardView(idx)	# 수정된 데이터 반환


# 게시물 삭제
@app.route("/boardDelete/<idx>")
def boardDelete(idx) :
	sql = "DELETE FROM board where idx=%s"
	getCursor()
	cursor.execute(sql,(idx))
	closeCon()
	return "true"

if __name__ == "__main__" : 
	app.run(host='0.0.0.0');