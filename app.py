import gevent.monkey
gevent.monkey.patch_all()
from werkzeug.serving import run_with_reloader
from werkzeug.debug import DebuggedApplication
from gevent.pywsgi import WSGIServer
from werkzeug.serving import run_simple


from flask import *
from bs4 import BeautifulSoup
import requests
from functools import wraps
import os
import hashlib
from db import get_session, user_exists, add_user, get_token, find_token, check_user, revoke_token
import json
import base64

app = Flask(__name__)

app.secret_key = "not a random string"
session = get_session()

def encrypt_string(hash_string):
	sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
	return sha_signature

def verify_token(f):
	@wraps(f)
	def decorated_func(*args, **kwargs):
		token = request.args.get("token")
		found, username = find_token(session, token)
		if(not token or not found):
			return redirect("/bye")
		return f(*args, **kwargs)
	return decorated_func

@app.route("/")
def index():
	return redirect("/login")

@app.route("/listfile")
@verify_token
def listfile():
	token = request.args.get("token")
	found, username = find_token(session, token)
	lst = os.listdir(app.static_folder+"\\"+username)
	# return render_template("listfile.html", data = lst, token = token)
	return jsonify(username = username,token = token, list = lst)

@app.route("/bye")
def bye():
	return "bye"

@app.route("/revoke")
@verify_token
def revoke():
	token = request.args.get("token")
	found, token = revoke_token(session, token)
	return jsonify(success = found, token = token)

@app.route("/getsavefile")
@verify_token
def getSaveFile():
	token = request.args.get("token")
	found, username = find_token(session, token)

	id = request.args.get("id")
	if(not id):
		try:
			lst = os.listdir(app.static_folder+"//"+username)
			lst.sort(key = lambda x: os.path.getmtime(app.static_folder+"//"+username+"//"+x))
			id = lst[-1]
		except IndexError:
			return jsonify(error = "Not Found!")

	filename = username +"//"+id
	with open(app.static_folder+'//'+filename,"r") as f:
		data = f.read()
		return jsonify(username = username, id = id, data = data)
	# return send_from_directory(app.static_folder,filename, as_attachment = True, attachment_filename = "save_"+id)

@app.route("/sendsavefile", methods=["POST", "GET"])
@verify_token
def sendSaveFile():
	if(request.method == "POST"):
		token = request.args.get("token")
		found, username = find_token(session, token)
		file = request.form["data"]
		foldername = app.static_folder+"//"+username
		if(not os.path.exists(foldername)):
			os.mkdir(foldername)
		
		lst = os.listdir(app.static_folder+"/"+username)
		cnt = len(lst)
		id = str(cnt)

		filename = foldername+"//"+id
		with open(filename,"w") as f:
			f.write(file)
		return render_template("post.html",token = token, error = "Done")
	return render_template("post.html",token = request.args.get("token"))

@app.route("/parse")
@verify_token
def parse():
	token = request.args.get("token")
	found, username = find_token(session, token)

	id = request.args.get("id")
	if(not id):
		try:
			lst = os.listdir(app.static_folder+"//"+username)
			id = lst[-1]
		except IndexError:
			return jsonify(error = "Not Found!")
	filename = username +"//"+id
	savefile = {}
	savefile["Money"] = 0
	savefile["TargetHP"] = 0
	savefile["Tick"] = 0
	savefile["NormalTower"] = []
	savefile["MachineGunTower"] = []
	savefile["SniperTower"] = []
	savefile["NormalEnemy"] = []
	savefile["BossEnemy"] = []
	savefile["TankerEnemy"] = []
	savefile["SmallerEnemy"] = []
	savefile["NormalSpawner"] = []
	savefile["SmallerSpawner"] = []
	savefile["BossSpawner"] = []
	savefile["TankerSpawner"] = []
	with open(app.static_folder+'//'+filename,"r") as f:
		decoded_file = base64.b64decode(f.readline().encode())
		file = decoded_file.decode().split("\n")
		n = int(file[0])
		for i in range(1, n):
			line = file[i]
			data = line.split(" ")
			index = data[0]
			if(index == "Money" or index == "TargetHP" or index == "Tick"):
				value = int(data[1])
				savefile[index] = value
			else:
				savefile[index].append(data[1:])
	return jsonify(savefile)



@app.route("/login", methods = ["POST", "GET"])
def login():
	if(request.method == "POST"):
		username = request.form["username"]
		password = request.form["password"]
		
		success, msg = check_user(session, username, password)
		if(success):
			return redirect(url_for("listfile", token = msg))
		else:
			return render_template("login.html", error = msg)
	return render_template("login.html")

@app.route("/register", methods = ["POST", "GET"])
def register():
	if(request.method == "POST"):
		username = request.form["username"]
		password = request.form["password"]
		re_password = request.form["confirm-password"]
		
		success, msg = add_user(session, username, password, re_password)
		if(success):
			os.mkdir(app.static_folder+"//"+username)
			return redirect(url_for("listfile", token = msg))
			
		else:
			return render_template("register.html", error = msg)
	return render_template("register.html")

def run_server():
	app.jinja_env.auto_reload = True
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
	app.config["JSON_SORT_KEYS"] = False
	http_server = WSGIServer(('0.0.0.0', 80), DebuggedApplication(app))
	http_server.serve_forever()

if __name__ == '__main__':
	run_with_reloader(run_server)