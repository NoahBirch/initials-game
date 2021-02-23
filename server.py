#!/usr/bin/env python  
  
from http.server import BaseHTTPRequestHandler,HTTPServer
from initials_database import InitialsDatabase
import json
import os  

#Create custom HTTPRequestHandler class  
class HTTPRequestHandler(BaseHTTPRequestHandler): 
	
	def do_DBFUNC_FETCH1(self):
		"""Calls a db func and fetches one value from db, returns that one object"""
		db = InitialsDatabase()

		self.send_response(200)
		self.send_header('Content-type','application/json')  
		self.end_headers() 

		content_len = int(self.headers.get('Content-Length'))
		post_body = (self.rfile.read(content_len)).decode("utf-8").split("|")
		db_func = post_body.pop(0)
		print('dbfunc = ', db_func)
		db_args = post_body
		print("db_args = ", db_args)

		method_to_call = None
		try:
			method_to_call = getattr(db, db_func)
		except AttributeError:
			raise NotImplementedError("Class `{}` does not implement `{}`".format(db.__class__.__name__, method_to_call))

		#Heres where we call our db function and get our return data. 
		return_data = method_to_call(*db_args)
		if return_data == None:
			self.send_response(404)
			return
			

		if type(return_data) == tuple:
			return_data = return_data[0]

		print("returning : ", return_data)

		json_string = json.dumps(return_data)
		self.wfile.write(json_string.encode(encoding='utf_8')) 

		return

	def do_DBFUNC_1FETCH2(self):
		"""Calls a db func and fetches one value from db, returns that one object"""
		db = InitialsDatabase()

		self.send_response(200)
		self.send_header('Content-type','application/json')  
		self.end_headers() 

		content_len = int(self.headers.get('Content-Length'))
		post_body = (self.rfile.read(content_len)).decode("utf-8")
		post_body = json.loads(post_body)

		print(type(post_body))
		print(post_body)

		db_func = post_body["func"]
		print('dbfunc = ', db_func)
		db_args = post_body["data"]
		print("db_args = ", db_args)



		method_to_call = None
		try:
			method_to_call = getattr(db, db_func)
		except AttributeError:
			raise NotImplementedError("Class `{}` does not implement `{}`".format(db.__class__.__name__, method_to_call))

		#Heres where we call our db function and get our return data. 
		return_data = method_to_call(db_args)
		if return_data == None:
			self.send_response(404)
			return
			

		if type(return_data) == tuple:
			return_data = return_data[0,1]

		print("returning : ", return_data)

		json_string = json.dumps(return_data)
		self.wfile.write(json_string.encode(encoding='utf_8')) 

		return

	def do_DBFUNC_ANSWERS_COMMIT(self):
		"""Calls a db func and fetches one value from db, returns that one object"""
		db = InitialsDatabase()

		self.send_response(200)
		self.send_header('Content-type','application/json')  
		self.end_headers() 

		content_len = int(self.headers.get('Content-Length'))
		post_body = (self.rfile.read(content_len)).decode("utf-8")
		post_body = json.loads(post_body)

		print(type(post_body))
		print(post_body)

		game_id = post_body["game_id"]
		print("game id:", game_id)

		user_id = post_body["user_id"]
		print("user_id:", game_id)

		data = post_body["data"]
		print("data:", data)

		db.commit_game_answers_to_db_NEW(game_id, user_id, data)

		return

	def do_GET(self):  
		rootdir = 'c:/xampp/htdocs/' #file location  
		try:  
			if self.path.endswith('.html'):  
				f = open(rootdir + self.path) #open requested file  

				#send code 200 response  
				self.send_response(200)  

				#send header first  
				self.send_header('Content-type','text-html')  
				self.end_headers()  

				#send file content to client  
				self.wfile.write(f.read())  
				f.close()  
				return  

		except IOError:  
			self.send_error(404, 'file not found')  

def run(): 
	print('http server is starting...')  

	#ip and port of servr  
	#by default http server port is 80  
	server_address = ('127.0.0.1', 5000)  
	httpd = HTTPServer(server_address, HTTPRequestHandler)

	print('http server is running...')  
	httpd.serve_forever()  

if __name__ == '__main__': 
	run()  