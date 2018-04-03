from flask.ext.mysql import MySQL

class mydb :
	def setDB(self,app) :
		self.app = app

	def getCursor() :
		app = self.app;
		app.config['MYSQL_DATABASE_USER'] = 'root'
		app.config['MYSQL_DATABASE_PASSWORD'] = 'nif'
		app.config['MYSQL_DATABASE_DB'] = '20180403'
		app.config['MYSQL_DATABASE_HOST'] = 'localhost'
		mysql.init_app(app)
		con = mysql.connect()
		cursor = con.cursor();
		return cursor

	def fetchAll(sql) :
		print "dd"
		return "dd"
		# cursor = self.getCursor()
		# cursor.execute(sql)
		# row_headers=[x[0] for x in cursor.description] #this will extract row headers
		# data = cursor.fetchall()
		# json_data=[]
		# for result in data:
		# 	json_data.append(dict(zip(row_headers,result)))
		# return "json.dumps(json_data)"

	def fetch(sql) :
		cursor = self.getCursor()
		cursor.execute(sql)
		row_headers=[x[0] for x in cursor.description] #this will extract row headers
		data = cursor.fetchall()
		return json.dumps(dict(zip(row_headers,data)))