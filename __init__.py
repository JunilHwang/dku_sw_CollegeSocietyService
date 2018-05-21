# -*- coding: utf-8 -*-
# 한글 인코딩은 위와 같이 주석으로 적용해야함.
# render template : html 불러오기
# request : 사용자 요청
# json : string to json
# pymysql : python mysql
# CORS : 외부 포트 접근 허용
from flask import Flask, render_template,json,request
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
		host='220.149.235.59',	# DB HOST
		user='root', 			# DB USER
		password='14959',     	# DB PW
		db='dkswcm',			# DB NAME
		autocommit=True, 		# python은 query 실행 후 commit을 해줘야 하는데, 이렇게 지정하면 자동으로 해줌
		charset='utf8')
	cursor = con.cursor(pymysql.cursors.DictCursor)	 # 전역변수로 커서 생성, DictCursor : 결과를 dictionary 형태로 받아옴

# DB 연결 종료
def closeCon() :
	con.close()

# 회원 추가
@app.route("/member", methods=['POST'])
def memberInsert() :
	_id = request.form['id']
	_pw = request.form['pw']
	_name = request.form['name']
	_nickname = request.form['nickname']
	_email = request.form['email']
	_undergrad_number = request.form['undergrad_number']
	getCursor()
	sql = 'SELECT count(*) as cnt from member where id=%s'
	cursor.execute(sql,(_id))
	data = cursor.fetchone()
	print data
	if data.get('cnt') > 0 :
		return "false"
	sql = '''
		INSERT INTO member SET
		id=%s,
		pw=%s,
		name=%s,
		nickname=%s,
		email=%s,
		undergrad_number=%s,
		college='단국대학교',
		major='소프트웨어학과',
		regdate=now()
	'''
	cursor.execute(sql,(_id,_pw,_name,_nickname,_email,_undergrad_number))
	lastid = cursor.lastrowid
	closeCon()
	return "true"

# 회원 정보 변경
@app.route("/member/<idx>", methods=['PUT'])
def memberUpdate(idx) :
	getCursor()
	if request.form.get('pw', 0) != 0 :
		_name = request.form['name']
		_nickname = request.form['nickname']
		_email = request.form['email']
		sql = '''
			UPDATE member SET
			name=%s,
			nickname=%s,
			email=%s
			where idx = %s
		'''
		_list = (_name,_nickname,_email,idx)
	else :
		_pw = request.form['pw']
		sql = '''
			UPDATE member SET
			pw=%s
			where idx = %s
		'''
		_list = (_pw,idx)
	cursor.execute(sql,_list)
	closeCon()
	return "true"

# 로그인
@app.route("/login", methods=['POST'])
def memberLogin() :
	_id = request.form['id']
	_pw = request.form['pw']
	sql = 'SELECT * FROM member WHERE id=%s and pw=%s'
	getCursor()
	cursor.execute(sql,(_id,_pw))
	data = cursor.fetchone()
	print data
	return json.dumps(data)

# 카테고리 목록
@app.route("/categoryList", methods=['GET'])
def categoryList() :
	# list 쿼리문
	sql = "SELECT * FROM category order by idx asc";
	getCursor()	# DB 연결
	cursor.execute(sql) # 쿼리문 실행
	data = cursor.fetchall() # 실행 결과 목록 가져오기
	closeCon() # 연결 종료
	return json.dumps(data) # 실행 결과를 json으로 반환

# 게시물 목록
@app.route("/boardList/<category>", methods=["GET"])
def boardList(category) :
	# list 쿼리문
	sql = "SELECT * FROM board where category=%s order by `reg_date` desc";
	getCursor()	# DB 연결
	cursor.execute(sql,(category)) # 쿼리문 실행
	data = cursor.fetchall() # 실행 결과 목록 가져오기
	closeCon() # 연결 종료
	#return "boardList" # 실행 결과를 json으로 반환
	return json.dumps(data) # 실행 결과를 json으로 반환
	
# boardInsert 접근시 게시물 추가 후 추가된 index값 반환
@app.route("/board/<category>", methods=['POST'])
def boardInsert(category) :
	_writer = request.form['writer']		# 사용자가 입력한 name 값
	_subject = request.form['subject']	# 사용자가 입력한 subject 값
	_content = request.form['content']	# 사용자가 입력한 content 값
	sql = '''
		INSERT INTO board SET
		-- parent=0,
		-- od=0,
		-- depth=0,
		subject=%s,
		writer=%s,
		content=%s,
		reg_date=now(),
		category=%s;
	''' # query문 작성
	getCursor()	# DB 연결
	cursor.execute(sql,(_subject,_writer,_content,category))	# 각 %s를 _name, _subject, _content로 치환
	lastid = cursor.lastrowid	# 추가된 데이터의 index 값
	closeCon()	# DB 연결 종료
	return json.dumps({"lastid":lastid})	# index값 반환

# /boardView 접근시 해당 게시물 데이터 반환
@app.route("/board/<idx>", methods=['GET'])
def boardView(idx) :
	sql = 'UPDATE board SET hit = hit+1 where idx=%s;'
	getCursor()
	cursor.execute(sql,(idx))
	closeCon();
	sql = '''
		SELECT 	b.*, m.name as writerName
		FROM 	board b
		join 	member m on b.writer = m.idx
		where 	b.idx=%s;
	'''
	getCursor()
	cursor.execute(sql,(idx))
	data = cursor.fetchone()
	closeCon();
	return json.dumps(data)

# /boardUpdate 접근시 해당 게시물 데이터 업데이트 및 반환
@app.route("/board/<idx>", methods=['PUT'])
def boardUpdate(idx) :
	_subject = request.form['subject']
	_content = request.form['content']
	sql = "UPDATE board SET subject=%s, content=%s where idx=%s;"
	getCursor()
	cursor.execute(sql,(_subject,_content,idx))
	closeCon()
	return "true"	# 수정된 데이터 반환


# 게시물 삭제
@app.route("/board/<idx>", methods=['DELETE'])
def boardDelete(idx) :
	sql = "DELETE FROM board where idx=%s"
	getCursor()
	cursor.execute(sql,(idx))
	closeCon()
	return "true"

# 교수 정보 가져오기
@app.route("/professor", methods=['GET'])
def professorList() :
	sql = '''
		SELECT 	p.*, f.origin_name, f.file_name
		FROM 	professor p
		JOIN 	files f on p.idx = f.idx and f.table = 'professor'
	'''
	getCursor()
	cursor.execute(sql)
	data = cursor.fetchall()
	closeCon()
	print data
	return json.dumps(data)

# 교수 정보 가져오기
@app.route("/professor/<idx>", methods=['GET'])
def professorGet(idx) :
	sql = '''
		SELECT 	p.*, f.origin_name, f.file_name
		FROM 	professor p
		JOIN 	files f on p.idx = f.idx and f.table = 'professor'
		where 	p.idx = %s
	'''
	getCursor()
	cursor.execute(sql,(idx))
	data = cursor.fetchone()
	closeCon()
	return json.dumps(data)

# if __name__ == "__main__" : 
# 	app.run(host='0.0.0.0',debug=True,threaded=True);