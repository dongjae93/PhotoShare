######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

#TODO Users to only view their own photo

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
#import flask.ext.login as flask_login
import flask_login

#for image uploading
from werkzeug import secure_filename
import os, base64
from flask_bootstrap import Bootstrap
import datetime
from datetime import date, datetime
from PIL import Image, ImageDraw


mysql = MySQL()
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '' #CHANGE THIS TO YOUR MYSQL PASSWORD
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def getUserList():	
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	rval = cursor.fetchall()
		
	return rval

class User(flask_login.UserMixin):
	pass


@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	
	cursor = conn.cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	
	
	return user

# get functions


def getUserInfo(uid):
	
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Users WHERE uid = '{0}'".format(uid))
	rval = cursor.fetchall()
	
	
	return rval

def getUserIdFromEmail(email):
	
	cursor = conn.cursor()
	cursor.execute("SELECT uid  FROM Users WHERE email = '{0}'".format(email))
	print cursor.fetchone()[0]
	rval=cursor.fetchone()[0]
	
	
	return rval

def getUserFNameFromUID(uid):
	
	cursor = conn.cursor()
	cursor.execute("SELECT firstname FROM Users WHERE uid = '{0}'".format(uid))
	rval=cursor.fetchone()[0]
	
	
	return rval

def getUserLastName(uid):
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT lastname FROM Users WHERE uid = '{0}'".format(uid))
	rval=cursor.fetchone()[0]
	
	
	return rval

def getUsersAlbums(uid):
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT aid, aname, uid, firstname, adate, cover FROM album NATURAL JOIN Users  WHERE uid = '{0}' ORDER BY adate DESC".format(uid))
	rval = cursor.fetchall()
	
	
	return rval

def getAIDfromAname(aname, uid):
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT AID FROM Album WHERE uid = '{0}' AND aname = '{1}'".format(uid, aname))
	rval=cursor.fetchone()[0]
	
	
	return rval

def getAnameFromAID(aid):
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT aname From Album WHERE aid= '{0}'".format(aid))
	rval=cursor.fetchone()[0]
	
	
	return rval


def getUsersPhotos(uid):
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT pid, data, caption, aid, likes, uid FROM photo WHERE uid = '{0}' ORDER BY pid DESC".format(uid))
	rval = cursor.fetchall()
	
	
	return rval #NOTE list of tuples, [(imgdata, pid), ...]

def getAllPhotos():
	
	cursor = conn.cursor()
	cursor.execute("SELECT pid, data, caption, aid, likes, uid FROM photo ORDER BY pid DESC")
	rval = cursor.fetchall()
	
	
	return rval

#SELECT pid, data, caption, aid, likes, uid, ctt, ct FROM Photo NATURAL JOIN ((SELECT pid, count(keyword) as ct from tag group by pid ORDER by ct DESC) T NATURAL JOIN (SELECT PID, count(keyword) as ctt from tag WHERE keyword = ANY(SELECT keyword FROM (SELECT keyword, count FROM numTag order by count DESC limit 5) A) GROUP BY pid ORDER BY ctt DESC) B) ORDER BY ctt DESC, ct
#SELECT pid, data, caption, aid, likes, uid, ctt, ct FROM Photo NATURAL JOIN ((SELECT pid, count(keyword) as ct from tag group by pid ORDER by ct DESC) T NATURAL JOIN (SELECT PID, count(keyword) as ctt from tag WHERE keyword = ANY(SELECT keyword FROM (SELECT keyword FROM numTag order by count DESC limit 5) A) GROUP BY pid ORDER BY ctt DESC) B) ORDER BY ctt DESC, ct
def youMayAlsoLike(uid):
	
	cursor = conn.cursor()
	cursor.execute("SELECT pid, data, caption, aid, likes, uid, ctt, ct FROM Photo NATURAL JOIN ((SELECT pid, count(keyword) as ct from tag group by pid ORDER by ct DESC) T NATURAL JOIN (SELECT PID, count(keyword) as ctt from tag WHERE keyword = ANY(SELECT keyword FROM (select uid, keyword, count(keyword) as ct from tag natural join photo group by uid, keyword HAVING uid = '{0}' order by ct desc limit 5) A) GROUP BY pid ORDER BY ctt DESC) B) ORDER BY ctt DESC, ct".format(uid))
	rval = cursor.fetchall()
	
	
	return rval

def getAllAlbums():
	
	cursor = conn.cursor()
	cursor.execute("SELECT A.aid, A.aname, U.uid, U.firstname, A.adate, A.cover FROM album A, Users U WHERE U.uid = A.uid ORDER BY A.adate DESC")
	rval = cursor.fetchall()
	
	
	return rval

def getPhotosInAlbum(aid):
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT pid, data, caption, aid, likes, uid FROM Photo WHERE aid = '{0}'".format(aid))
	rval = cursor.fetchall()
	
	
	return rval

def getTagsInAlbum(aid):
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT keyword from TAG NATURAL JOIN (SELECT pid from photo where aid='{0}') A WHERE tag.pid=A.pid".format(aid))
	rval = cursor.fetchall()
	
	
	return rval

# def getPhotosWithTags(tags):
#  	cusor = mysql.connect().cursor()
#  	photolist = set()
#  	for tag in tags.split(', '):
#  		cursor.execute("SELECT pid, data, caption, aid, likes, uid from Tag NATURAL JOIN Photo WHERE keyword = '{0}'".format(tag))
#  		photowithtag = cursor.fetchall()
#  		photolist.add(photowithtag)
#  	finallist = []
#  	for x in photolist:

# 	return photolist

def getPhotosWithATag(tag):
	 	
	cursor = conn.cursor()
	print cursor.execute("SELECT pid, data, caption, aid, likes, uid from Tag NATURAL JOIN Photo WHERE keyword='{0}'".format(tag))
	rval = cursor.fetchall()
	
	return rval

def getUsersPhotosWithATag(uid, tag):
	 	
	cursor = conn.cursor()
	print cursor.execute("SELECT pid, data, caption, aid, likes, uid from Tag NATURAL JOIN Photo WHERE keyword='{0}' AND uid='{1}'".format(tag, uid))
	rval = cursor.fetchall()
	
	return rval

def getAllComments():
	
	cursor = conn.cursor()
	cursor.execute("SELECT CID, UID, PID, comment, cdate FROM comment")
	rval = cursor.fetchall()
	
	return rval

def getPhotoComments(pid):
	
	cursor = conn.cursor()
	cursor.execute("SELECt UID, PID, comment, cdate, commenter, commenter_image from comment WHERE PID = '{0}'".format(pid))
	rval = cursor.fetchall()
	
	
	return rval

def getAlltags():
	
	cursor = conn.cursor()
	cursor.execute("SELECT keyword, PID FROM Tag")
	rval = cursor.fetchall()
	
	
	return rval

def getUserstags(uid):
	
	cursor = conn.cursor()
	cursor.execute("SELECT keyword, PID FROM Tag NATURAL JOIN Photo WHERE uid = '{0}'".format(uid))
	rval = cursor.fetchall()
	
	
	return rval

def getTopFiveUsersTag(uid):
	
	cursor = conn.cursor()
	cursor.exeute("select keyword, count(keyword) as howmany from tag natural join photo where uid = 6 GROUP BY keyword ORDERBY howmany DESC LIMIT 5")
	rval = cursor.fetchall()
	
	
	return rval

def suggestTags(tags):
	
	cursor = conn.cursor()
	tagset = set()
	for tag in tags.split(', '):
		tagset.add(tag)

	taglist = []
	for tag in tagset:
		taglist.append(tag)

	if len(taglist) == 1:
		cursor.execute("SELECT keyword, count(keyword) as ct FROM (SELECT PID from tag where PID IN (SELECT pid from tag where keyword='{0}')) A NATURAL JOIN tag group by keyword HAVING keyword NOT IN (SELECT keyword from tag where keyword='{0}') order by ct desc".format(taglist[0]))
	elif len(taglist) == 2:
		cursor.execute("SELECT keyword, count(keyword) as ct FROM (SELECT PID from tag where PID IN (SELECT pid from tag where keyword='{0}') AND PID IN (SELECT pid from tag where keyword='{1}')) A NATURAL JOIN tag group by keyword HAVING keyword NOT IN (SELECT keyword from tag where keyword='{0}' or keyword='{1}') order by ct desc".format(taglist[0], taglist[1]))
	elif len(taglist) == 3:
		cursor.execute("SELECT keyword, count(keyword) as ct FROM (SELECT PID from tag where PID IN (SELECT pid from tag where keyword='{0}') AND PID IN (SELECT pid from tag where keyword='{1}') AND PID IN (SELECT pid from tag where keyword='{2}')) A NATURAL JOIN tag group by keyword HAVING keyword NOT IN (SELECT keyword from tag where keyword='{0}' or keyword='{1}' or keyword='{2}') order by ct desc".format(taglist[0], taglist[1], taglist[2]))
	elif len(taglist) == 4:
		cursor.execute("SELECT keyword, count(keyword) as ct FROM (SELECT PID from tag where PID IN (SELECT pid from tag where keyword='{0}') AND PID IN (SELECT pid from tag where keyword='{1}') AND PID IN (SELECT pid from tag where keyword='{2}') AND PID IN (SELECT pid from tag where keyword='{3}')) A NATURAL JOIN tag group by keyword HAVING keyword NOT IN (SELECT keyword from tag where keyword='{0}' or keyword='{1}' or keyword='{2}' or keword='{3}') order by ct desc".format(taglist[0], taglist[1], taglist[2], taglist[3]))
	else:
		cursor.execute("SELECT keyword, count(keyword) as ct FROM (SELECT PID from tag where PID IN (SELECT pid from tag where keyword='{0}') AND PID IN (SELECT pid from tag where keyword='{1}') AND PID IN (SELECT pid from tag where keyword='{2}') AND PID IN (SELECT pid from tag where keyword='{3}') AND PID IN (SELECT pid from tag where keyword='{4}')) A NATURAL JOIN tag group by keyword HAVING keyword NOT IN (SELECT keyword from tag where keyword='{0}' or keyword='{1}' or keyword='{2}' or keword='{3}' or keyword='{4}') order by ct desc".format(taglist[0], taglist[1], taglist[2], taglist[3], taglist[4]))
	rval = cursor.fetchall()
	
	
	return rval


# tags = getTopFiveUsersTag(uid)
#
#
#select pid, keyword from tag where keyword='door' or keyword='banana' or keyword='lol' or keyword='art' or keyword='not'
# select pid, keyword from (select pid from tag where keyword='door' or keyword='banana' or keyword='lol' or keyword='art' or keyword='not') natural join tag
#select tag.pid, tag.keyword from (select pid from tag where keyword='door' or keyword='lol' or keyword='art') A natural join tag WHERE A.pid = tag.pid

#SELECT keyword, count(keyword) as ct FROM (SELECT PID from tag where PID IN (SELECT pid from tag where keyword='lol') AND PID IN (SELECT pid from tag where keyword='art') AND PID IN (SELECT pid from tag where keyword='door')) A NATURAL JOIN tag group by keyword HAVING keyword NOT IN (SELECT keyword from tag where keyword='door' or keyword='lol' or keyword='art') order by ct desc;
#
#
#SELECT PID from tag where PID IN (SELECT pid from tag where keyword='lol') AND PID IN (SELECT pid from tag where keyword='art') AND PID IN (SELECT pid from tag where keyword='door')

# 
# SELECT P.pid, count, caption from (SELECT PID, count(PID) as count from (SELECT PID, keyword from tag WHERE keyword = ANY(SELECT keyword FROM (SELECT keyword, count FROM numTag order by count DESC limit 5) A)) C group by pid ORDER BY count DESC) D, Photo P WHERE D.pid=P.pid;
# 
#
# SELECT pid, count(keyword) as ct from tag group by pid ORDER by count(keyword) DESC -> give me pid with number of tags
#
#SELECT PID, count(keyword) as ctt from tag WHERE keyword = ANY(SELECT keyword FROM (SELECT keyword, count FROM numTag order by count DESC limit 5) A) GROUP BY pid ORDER BY ct DESC ; -> gives me pid with num of toptags
#SELECT pid, caption, ctt, ct FROM Photo NATURAL JOIN ((SELECT pid, count(keyword) as ct from tag group by pid ORDER by ct DESC) T NATURAL JOIN (SELECT PID, count(keyword) as ctt from tag WHERE keyword = ANY(SELECT keyword FROM (SELECT keyword, count FROM numTag order by count DESC limit 5) A) GROUP BY pid ORDER BY ctt DESC) B)


def isEmailUnique(email):
	#use this to check if a email has already been registered
	
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		
		
		return False
	else:
		
		
		return True

def createAlbum(uid, aname):

		today = str(date.today())
		default = getdefaultprofilepic()
		
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Album (uid, aname, adate, cover) VALUES ('{0}', '{1}', '{2}', '{3}')".format(uid, aname, today, default))
		conn.commit()
		
		


def deleteAlbum(uid, aid):
	
		 	
		cursor = conn.cursor()
		cursor.execute("DELETE FROM Album WHERE uid = '{0}' AND aid = '{1}'".format(uid, aid))
		conn.commit()
		
		




def uploadPhoto(uid, image, caption, aname, tags):
	data = base64.standard_b64encode(image.read())
	
	
	cursor = conn.cursor()

	aid = getAIDfromAname(aname, uid)
	cursor.execute("INSERT INTO photo (uid, data, caption, aid) VALUES ('{0}', '{1}', '{2}', '{3}')".format(uid, data, caption, aid))
	
	addScore(uid)
	if tags:
		addTag(tags)
		addTagCount(tags)
	conn.commit()
	
	

def deletePhoto(uid, pid):
	minusScore(uid)
	 	
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Photo WHERE pid = '{0}'".format(pid))
	conn.commit()
	
	

def addTag(tags):
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT MAX(PID) FROM Photo WHERE UID = '{0}'".format(uid))
	pid = cursor.fetchone()[0]
	cursor.execute("SELECT keyword from NumTag")
	existingTag = cursor.fetchall()
	li = [x[0] for x in existingTag]
	for tag in tags.split(', '):
		print tag
		cursor.execute("INSERT INTO Tag (keyword, PID) VALUES ('{0}', '{1}')".format(tag, pid))
	conn.commit()
	
	

def addTagCount(tags):	
	for tag in tags.split(', '):
		 	
		cursor = conn.cursor()
		cursor.execute("SELECT keyword from NumTag")
		existingTag = cursor.fetchall()
		li = [x[0] for x in existingTag]
		if tag in li:
			cursor.execute("UPDATE numTag SET count = count+1 WHERE keyword = '{0}'".format(tag))
			conn.commit()
			conn.commit()
			conn.commit()

		else:
			cursor.execute("INSERT INTO numTag (keyword, count) VALUES ('{0}', 1)".format(tag))
			conn.commit()
			conn.commit()
			conn.commit()
			conn.commit()
	conn.commit()

def addLike(uid, pid):
	 	
	try:
		corsor = conn.cursor()
		cursor.execute("INSERT INTO like_photo (uid, pid) VALUES ('{0}', '{1}')".format(uid,pid))
		conn.commit()
		conn.commit()
		conn.commit()
		conn.commit()
		cursor.execute("UPDATE Photo SET likes = likes + 1 WHERE pid='{0}'".format(pid))
		conn.commit()
		conn.commit()
		conn.commit()
		conn.commit()
		conn.commit()
		
		
	except Exception as e:
		print 'alreadylikedthephoto'

		
		

def addScore(uid):
	 	
	cursor = conn.cursor()
	cursor.execute("UPDATE Scoreboard SET Score = Score+1 WHERE uid = '{0}'".format(uid))
	conn.commit()
	
	

def minusScore(uid):
	 	
	cursor = conn.cursor()
	cursor.execute("UPDATE Scoreboard SET Score = Score-1 WHERE uid = '{0}'".format(uid))
	conn.commit()
	
	

def showClickedAlbumsPhotos(aid):
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT pid, data, caption, aid, likes FROM Photo WHERE aid='{0}'".format(aid))
	photos = cursor.fetchall()
	
	
	return photos


def getdefaultprofilepic():
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT data from Photo WHERE pid = 69")
	rval = cursor.fetchone()[0]
	
	
	return rval


def addFriend(uid, fid):
	 	
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Friend (uid, fid) VALUES ('{0}', '{1}')".format(uid,fid))
	conn.commit()
	
	

def getTagsInAlbum(aid):
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT keyword, pid FROM (SELECT pid from Photo where aid = '{0}') P, Tag WHERE T.pid = P.pid".format(aid))
	rval = cursor.fetchall()
	
	
	return rval

def checkTagExist(tags):
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT keyword from tag")
	existingtag=cursor.fetchall()
	
	
	for tag in tags.split(', '):
		if str(tag) in str(existingtag):
			return True
		else: 
			return False
'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register/", methods=['GET'])
def register():
	return render_template('register.html', supress='True')  

@app.route("/register/", methods=['POST'])
def register_user():
	
	try:
		email=request.form.get('email')
		print email
		password=request.form.get('password')
		print password
		firstname=request.form.get('firstname')
		print firstname
		lastname=request.form.get('lastname')
		print lastname
		home=request.form.get('home')
		print home
		gender=request.form.get('gender')
		print gender
		dob=request.form.get('dob')
		print dob
		bio=request.form.get('bio')
		print bio
		profileImage=request.files['photo']

		photo_data = base64.standard_b64encode(profileImage.read())
		if request.files['photo'].filename == '':
			photo_data = getdefaultprofilepic()
		
	except Exception as e:
		print e
		print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	
	test =  isEmailUnique(email)
	if test:
		
		try:
			cursor = conn.cursor()
			print email
			cursor.execute("INSERT INTO Users (email, password, firstname, lastname, home, gender, dob, bio, profile_Image) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')".format(email, password, firstname, lastname, home, gender, dob, bio, photo_data))
			a = cursor.fetchone()
			conn.commit()
			print a
			#log user in
			user = User()
			user.id = email
			print user.id
			flask_login.login_user(user)
			print flask_login.login_user(user)
			print getUserIdFromEmail(flask_login.current_user.id)
			uid = getUserIdFromEmail(flask_login.current_user.id)
			today = str(date.today())
			print today
		except Exception as e:
			print e
			print "Something Went wrong"
			return flask.redirect(flask.url_for('register'))
		print cursor.execute("INSERT INTO Album (uid, aname, adate, cover) VALUES ('{0}', 'default', '{1}', '{2}')".format(uid, today, photo_data))
		aid = getAIDfromAname('default', uid)
		cursor.execute("INSERT INTO Photo (uid, aid, data, caption) VALUES ('{0}', '{1}', '{2}', 'profile')".format(uid,aid,photo_data))
		cursor.execute("INSERT INTO Scoreboard (uid) VALUES ('{0}')".format(uid))
		return render_template('profile.html', firstname=firstname, message='Account Created!')
		
	else:
		print "couldn't find all tokens"
		return render_template('register.html', message='Email Already Exists')

def getUserIdFromEmail(email):
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT uid  FROM Users WHERE email = '{0}'".format(email))
	rval = cursor.fetchone()[0]
	
	return rval

def isEmailUnique(email):
	#use this to check if a email has already been registered
	 	
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		
		return False
	else:
		
		return True
#end login code

@app.route('/profile', methods=['GET', 'POST'])
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	userInfo=getUserInfo(uid)
	uid = userInfo[0][0]
	print uid
	email = userInfo[0][1]
	print email
	firstname = userInfo[0][2]
	print firstname
	lastname = userInfo[0][3]
	print lastname
	dob = userInfo[0][4]
	print dob
	profile_Image = userInfo[0][5]
	bio = userInfo[0][6]
	print bio
	hometown = userInfo[0][7]
	print hometown
	gender = userInfo[0][8]
	print gender
	if flask.request.method == 'POST':
			if lastname == 'Guest':
				return render_template('unauth.html', firstname=firstname, lastname=lastname)
			else:
				if request.files['profile'] is not None:
					profile_Image = request.files['profile']
					data=base64.standard_b64encode(profile_Image.read())
					cursor = conn.cursor()
					cursor.execute("UPDATE Users SET profile_image='{0}' WHERE uid = '{1}'".format(data, uid))
					conn.commit()
					return render_template('profile.html',firstname=firstname, lastname=lastname, email=email, dob=dob, profile_Image=data, bio=bio, hometown=hometown, gender=gender, message="Here's your profile")
	else:
		return render_template('profile.html',firstname=firstname, lastname=lastname, email=email, dob=dob, profile_Image=profile_Image, bio=bio, hometown=hometown, gender=gender, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
@app.route('/findfriends', methods=['GET', 'POST'])

def findfriends():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	if flask.request.method == 'POST':
		print request.form.get('email')
		print request.form.get('lastname')
		if request.form.get('email') not in ['']:
			femail = request.form.get('email')
			fid = getUserIdFromEmail(femail)
			userInfo = getUserInfo(fid)
			
			return render_template('findfriends.html', firstname=firstname, lastname=lastname, users=userInfo, uid=uid)
		elif request.form.get('lastname') not in ['']:
			flastname = request.form.get('lastname')
			 	
			cursor = conn.cursor()
			cursor.execute("SELECT uid, email, firstname, lastname, dob, profile_Image, bio, home, gender FROM Users WHERE lastname = '{0}' AND uid != '{1}'".format(flastname, uid))
			userInfo=cursor.fetchall()
			
			return render_template('findfriends.html', firstname=firstname, lastname=lastname, users=userInfo, uid=uid)
		elif request.form.get('follow') not in ['']:
			fid = request.form.get('follow')
			addFriend(uid, fid)
			
			return render_template('findfriends.html', firstname=firstname, lastname=lastname, message= "Added!", uid=uid)
		else: 
			
			return render_template('findfriends.html', firstname=firstname, lastname=lastname, message="Could not find anyone with that email/lastname :(", uid=uid)
	else:
		if lastname == 'Guest':
			
			return render_template('unauth.html', firstname=firstname, lastname=lastname)		
		else:
			 	
			cursor = conn.cursor()
			
			cursor.execute("SELECT U.uid, U.email, U.firstname, U.lastname, U.dob, U.profile_Image from Users U, (SELECT FID from Friend where UID = '{0}') F WHERE F.FID = U.uid;".format(uid))
			friendlist = cursor.fetchall() 
			
			return render_template('findfriends.html', lastname=lastname, firstname=firstname, uid=uid)


@app.route('/findfriends/<int:uid>')
def ListMyFriends(uid):
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	
	
	cursor.execute("SELECT U.uid, U.email, U.firstname, U.lastname, U.dob, U.profile_Image FROM (SELECT fid from Friend WHERE Friend.uid = '{0}') F, Users U WHERE F.fid=U.uid".format(uid))
	friendlists = cursor.fetchall()
	
	return render_template('friendlist.html', lastname=lastname, firstname=firstname, uid=uid, friendlists=friendlists)






@app.route('/top')
def toptentags():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT keyword FROM numTag ORDER by count DESC LIMIT 10")
	toptags= cursor.fetchall()
	cursor.execute("SELECT U.firstname, S.score FROM Users U, Scoreboard S WHERE U.uid = S.uid ORDER BY S.score DESC LIMIT 10")
	topusers= cursor.fetchall()
	
	return render_template('top.html', firstname=firstname, lastname=lastname, toptags=toptags, topusers=topusers)

@app.route('/upload', methods=['GET', 'POST'])

def upload_file():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	if lastname == 'Guest':
		
		return render_template('unauth.html', firstname=firstname, lastname=lastname)
	
	elif flask.request.method == 'POST':
		print request.form.get('suggest')
		if request.form.get('suggest') is not None:
			tags = request.form.get('suggest')
			suggestions = suggestTags(tags)
			
			return render_template("upload.html", firstname=firstname, lastname=lastname, albums=getUsersAlbums(uid), suggestions=suggestions)
		
		elif request.form.get('upload') is not None:
			imgfile = request.files['photo']
			caption = request.form.get('caption')
			tags = request.form.get('tag')
			aname = request.form.get('aname')
			if aname == '':
				aname = 'default'
			
			try:
				aid = getAIDfromAname(aname, uid)
			except Exception as e:
				
				return render_template('upload.html', firstname=firstname, lastname=lastname, message="That Album does not exist! Create the album first!", albums=getUsersAlbums(uid))
			
			
			data = base64.standard_b64encode(imgfile.read())
			 	
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Photo (data, uid, caption, aid) VALUES ('{0}', '{1}', '{2}', '{3}')".format(data,uid, caption, aid))
			conn.commit()
			cursor.execute("SELECT MAX(pid) from photo")
			maxpid = cursor.fetchone()[0]
			cursor.execute("UPDATE Album SET cover = '{0}' WHERE uid = '{1}' AND aname = '{2}'".format(data, uid, aname))
			addScore(uid)
			try:
				addTag(tags)
			except Exception as e:
				print e
			addTagCount(tags)

			
			return render_template('photo.html', firstname=firstname, lastname=lastname , message='Photo uploaded!', photos=getUsersPhotos(uid), tags=getUserstags(uid), albums=getUsersAlbums(uid))
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		
		return render_template('upload.html', firstname=firstname, lastname=lastname, albums=getUsersAlbums(uid))
#end photo uploading code 


@app.route('/album', methods=['GET', 'POST'])
def album():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	if flask.request.method == 'GET':
		if lastname == 'Guest':
			
			return render_template('album.html', firstname = firstname, lastname = lastname, albums = getAllAlbums(), tags = getAlltags(), photos=getAllPhotos())
		else: 
			
			return render_template('album.html', firstname = firstname, lastname = lastname, albums = getUsersAlbums(uid), tags = getAlltags(), photos=getAllPhotos(), uid=uid)
		
	elif flask.request.method == 'POST':
		if lastname == 'Guest':
			
			return render_template('unauth.html', firstname = firstname, lastname = lastname, albums = getAllAlbums(), tags = getAlltags(), photos=getAllPhotos())
		
		elif request.form.get('delete') is not None:
			aid = request.form.get('delete')
			deleteAlbum(uid, aid)
			 	
			cursor = conn.cursor()
			cursor.execute("SELECT count(pid) from photo where aid = '{0}'".format(aid))
			numofpics=cursor.fetchone()[0]
			
			for numofpic in range(numofpics-1):
				minusScore(uid)
			
			return render_template('album.html', firstname=firstname, lastname = lastname, albums = getUsersAlbums(uid), tags = getAlltags(), photos=getAllPhotos(), uid=uid)
		
		elif request.form.get('create') is not None:
			aname = request.form.get('create')
			createAlbum(uid, aname)
			conn.commit()
			if request.form.get('create') == 'upload':
				
				return render_template('upload.html', firstname=firstname, lastname=lastname, albums=getUsersAlbums(uid), uid=uid)
			
			return render_template('album.html', firstname=firstname, lastname = lastname, albums = getUsersAlbums(uid), tags = getUserstags(uid), photos=getAllPhotos(), uid=uid)
		
		elif request.form.get('viewall') is not None:
			return render_template('album.html', firstname = firstname, lastname = lastname, albums = getAllAlbums(), tags = getAlltags(), photos=getAllPhotos(), uid=uid)

	return render_template('album.html', firstname=firstname, lastname = lastname, albums = getUsersAlbums(uid), tags = getAlltags(), photos=getAllPhotos(), uid=uid)

@app.route('/album/<int:aid>/edit', methods=['GET', 'POST'])
def editalbum(aid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT cover from album where aid='{0}'".format(aid))
	cover = cursor.fetchone()[0]

	if flask.request.method == 'GET':
		
		return render_template('edit.html', firstname=firstname, lastname = lastname, aid=aid)
	else: 
		if request.form.get('edit') is not None:
			if request.form.get('aname'):
				aname = request.form.get('aname')
				cursor.execute("Update Album SET aname='{0}' WHERE aid='{1}'".format(aname, aid))
				conn.commit()
			if request.form.get('adate') is not None:
				adate=request.form.get('adate')	
				cursor.execute("Update Album SET adate='{0}' WHERE aid='{1}'".format(adate, aid))
				conn.commit()
		
		return render_template('album.html', firstname=firstname, lastname = lastname, albums = getUsersAlbums(uid), tags = getAlltags(), photos=getAllPhotos(), uid=uid)


@app.route('/photo', methods=['GET', 'POST'])
def photo():
	 	
	cursor = conn.cursor()
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	
	if flask.request.method == 'GET':
		if lastname == 'Guest':

			return render_template('photo.html', firstname = firstname, lastname = lastname, photos=getAllPhotos(), albums=getAllAlbums(), tags=getAlltags())
		else:

			return render_template('photo.html', firstname=firstname, lastname=lastname , message='Explore your Photo!', photos=getUsersPhotos(uid), tags=getAlltags(), albums=getUsersAlbums(uid), uid=uid)
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		firstname = getUserFNameFromUID(uid)
		lastname = getUserLastName(uid)
		
		if request.form.get('clickedAlbum') is not None:
			 	
			cursor = conn.cursor()
			aid = request.form.get('clickedAlbum')
			cursor.execute("SELECT aname FROM Album WHERE aid='{0}'".format(aid))
			
			return render_template('photo.html', firstname = firstname, lastname = lastname, title=cursor.fetchone()[0], photos=showClickedAlbumsPhotos(aid),  tags=getAlltags(), albums=getAllAlbums(), uid=uid)
		elif request.form.get('clickedTag') is not None:
			 	
			cursor = conn.cursor()
			tag=request.form.get('clickedTag')
			
			return render_template('photo.html', firstname = firstname, lastname = lastname, title=tag, photos=getPhotosWithATag(tag), clickedTag='True', tags=getAlltags(), albums=getAllAlbums(), uid=uid)
		
		elif request.form.get('delete') is not None:
			pid = request.form.get('delete')
			deletePhoto(uid, pid)
			return render_template('photo.html', firstname=firstname, lastname=lastname , message='Photo Deleted!', photos=getUsersPhotos(uid), tags=getAlltags(), albums=getUsersAlbums(uid), uid=uid)
		else:
			return render_template('photo.html', firstname=firstname, lastname=lastname , message='Explore your Photo!', photos=getUsersPhotos(uid), tags=getAlltags(), albums=getAllAlbums(), uid=uid)

@app.route('/photo/<tag>')
def phototag(tag):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	if lastname != 'Guest':
		return render_template('photo.html', firstname = firstname, lastname = lastname, ttitle=tag, photos=getUsersPhotosWithATag(uid, tag), tags=getAlltags(), albums=getAllAlbums(), uid=uid)
	else: 
		return render_template('photo.html', firstname = firstname, lastname = lastname, ttitle=tag, photos=getPhotosWithATag(tag), tags=getAlltags(), albums=getAllAlbums(), uid=uid)

@app.route('/photo/<tag>/viewall')
def phototagviewall(tag):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	return render_template('photo.html', firstname = firstname, lastname = lastname, ttitle=tag, photos=getPhotosWithATag(tag), tags=getAlltags(), albums=getAllAlbums(), uid=uid, viewall='True')

@app.route('/photo/<int:aid>')
def photoalbum(aid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	aname = getAnameFromAID(aid)

	return render_template('photo.html', firstname=firstname, lastname=lastname, atitle=aname, photos=getPhotosInAlbum(aid), tags=getAlltags(), albums=getAllAlbums(), uid=uid)


@app.route('/photo/<int:pid>/edit', methods=['GET', 'POST'])
def editphoto(pid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	
	if flask.request.method == 'GET':
		return render_template('edit.html', firstname=firstname, lastname = lastname, pid=pid)
	else: 
		if request.form.get('edit') is not None:
			 	
			cursor = conn.cursor()
			if request.form.get('caption'):
				caption = request.form.get('caption')
				cursor.execute("Update Photo SET caption='{0}' WHERE pid='{1}'".format(caption, pid))
				conn.commit()
			if request.form.get('tag') is not None:
				tags=request.form.get('tag')
				cursor.execute("DELETE FROM Tag where pid = '{0}'".format(pid))
				conn.commit()
				conn.commit()
				conn.commit()
				for tag in tags.split(', '):
					cursor.execute("INSERT INTO Tag (keyword, PID) VALUES ('{0}', '{1}')".format(tag, pid))
					conn.commit()
			
		return render_template('photo.html', firstname=firstname, lastname=lastname , message='Photo Editted!', photos=getUsersPhotos(uid), tags=getAlltags(), albums=getUsersAlbums(uid), uid=uid)

@app.route('/photo/<int:pid>/comment', methods=['GET', 'POST'])
def commentphoto(pid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT pid, data, caption, aid, likes, uid FROM photo where pid = '{0}'".format(pid))
	photo = cursor.fetchone()
	ownerid = photo[5]
	cursor.execute("SELECT firstname from Photo NATURAL JOIN Users WHERE pid='{0}'".format(pid))
	owner = cursor.fetchone()
	cursor.execute("SELECT aid, aname, adate from Photo Natural JOIN Album WHERE pid='{0}'".format(pid))
	albuminfo = cursor.fetchone()
	comments = getPhotoComments(pid) #TODO
	
	if flask.request.method == 'GET':
		return render_template('comment.html', firstname=firstname, lastname=lastname, photo=photo, owner=owner, albuminfo=albuminfo, tags=getUserstags(ownerid), comments=comments, ownerid=ownerid, uid=uid)

	else:
		print request.form.get('comment')

		if request.form.get('comment') is not None:

			comment = request.form.get('comment')
			 	
			cursor = conn.cursor()
			cursor.execute("SELECT firstname, lastname, profile_image from Users where uid = '{0}'".format(uid))
			commenter = cursor.fetchone()
			commenter_image = commenter[2]
			commenter = str(commenter[0]) + " " + str(commenter[1])
				
			cdate = str(date.today())
			cursor.execute("INSERT INTO Comment (uid, pid, comment, cdate, commenter, commenter_image) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(uid, pid, comment, cdate, commenter, commenter_image))
			if lastname != 'Guest':
				addScore(uid)
			conn.commit()
			conn.commit()
			conn.commit()
			return render_template('comment.html', firstname=firstname, lastname=lastname, photo=photo, owner=owner, albuminfo=albuminfo, tags=getUserstags(ownerid), comments=comments, ownerid=ownerid, uid=uid)

		elif request.form.get('like') is not None:
			print request.form.get('like')
			pid = request.form.get('like')
			addLike(uid, pid)			 	
			cursor = conn.cursor()
			cursor.execute("SELECT firstname from Photo NATURAL JOIN Users WHERE pid='{0}'".format(pid))
			owner = cursor.fetchone()
			print owner
			cursor.execute("SELECT pid, data, caption, aid, likes, uid FROM photo where pid = '{0}'".format(pid))
			photo = cursor.fetchone()
			ownerid = photo[5]
			print ownerid
			cursor.execute("SELECT aid, aname, adate from Photo Natural JOIN Album WHERE pid='{0}'".format(pid))
			albuminfo = cursor.fetchone()
			comments = getPhotoComments(pid)
			
			return render_template('comment.html', firstname=firstname, lastname= lastname, photo=photo, owner=owner, albuminfo=albuminfo, tags=getUserstags(ownerid), comments=comments, ownerid=ownerid, uid=uid)
		return render_template('comment.html', firstname=firstname, lastname=lastname, photo=photo, owner=owner, albuminfo=albuminfo, tags=getUserstags(ownerid), comments=comments, ownerid=ownerid, uid=uid)

@app.route('/photo/<int:pid>/likes', methods=['GET'])
def likephoto(pid):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	 	
	cursor = conn.cursor()
	cursor.execute("SELECT firstname, lastname FROM (SELECT UID FROM LIKE_PHOTO WHERE PID = '{0}') L, USERS WHERE L.UID = Users.uid".format(pid))
	likelists=cursor.fetchall()
	return render_template('like.html', firstname=firstname, lastname=lastname, likelists=likelists, uid=uid)

@app.route('/photo/<int:uid>/mayalsolike', methods=['GET'])
def maylike(uid):
	photos = youMayAlsoLike(uid)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	if lastname == 'Guest':
		return render_template('unauth.html', firstname=firstname, lastname=lastname)
	else:
		return render_template('photo.html', firstname = firstname, lastname = lastname, photos=photos, albums=getAllAlbums(), tags=getAlltags(), uid=uid)

@app.route('/search', methods=['GET', 'POST'])
def photosearch():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	if flask.request.method == 'GET':
		return render_template('search.html', firstname=firstname, lastname=lastname)
	else:
		
		tags = request.form.get('tags')
		print tags
		print checkTagExist(tags)
		if checkTagExist(tags):
			photos=[]
			for tag in tags.split(', '):
				print tag
				photos+=getPhotosWithATag(tag)

			return render_template('photo.html', firstname=firstname, lastname=lastname, photos=photos, albums=getAllAlbums(), tags=getAlltags(), uid=uid)
		else:
			return render_template('search.html', firstname=firstname, lastname=lastname, message="Could not find any photo with the tag :(")

#default page  
@app.route("/index", methods=['GET'])
def index():
	return render_template('index.html')

@app.route("/", methods=['GET'])
def hi():
	return flask.redirect(flask.url_for('index'))

@app.route("/main", methods=['GET','POST'])
def main():
	
	uid = getUserIdFromEmail(flask_login.current_user.id)
	
	firstname = getUserFNameFromUID(uid)
	lastname = getUserLastName(uid)
	return render_template('hello1.html', firstname= firstname, lastname=lastname, message="Welcome to Photoshare! Let's Explore Photos", photos=getAllPhotos(), albums=getAllAlbums(), tags=getAlltags())
	# , photos=getAllPhotos(), comments=getAllComments(), likes=getAllLikes(), top10users=getTop10Users(), top10tags=getTop10Tags(), mayalsolike=mayalsolike(), tags=getAlltags())

@app.route('/login', methods=['GET', 'POST'])

def login():
	if flask.request.method == 'GET':
		return flask.redirect(flask.url_for('index'))
	#The request method is POST (page is recieving data)
	if flask.request.method == 'POST':
		if request.form.get('password') == '':
			if request.form.get('email') == '':
			
				 	
				cursor = conn.cursor()
				cursor.execute("INSERT INTO Users (firstname, lastname) VALUES ('Guest', 'Guest')")
				conn.commit()
				cursor.execute("SELECT MAX(UID) FROM Users")
				guestid=cursor.fetchone()[0]
				guest = 'Guest' + str(guestid)
				cursor.execute("UPDATE Users SET firstname = '{0}', email = '{0}' WHERE uid = '{1}'".format(guest,guestid))
				conn.commit()
				defaultpic = getdefaultprofilepic()
				cursor.execute("UPDATE Users SET profile_image = '{0}' WHERE uid = '{1}'".format(defaultpic, guestid))
				user = User()
				user.id = guest
				flask_login.login_user(user)
				return flask.redirect(flask.url_for('main'))
		else:
			email = flask.request.form['email']
			 	
			cursor = conn.cursor()
	#check if email is registered
			if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
				data = cursor.fetchall()
				pwd = str(data[0][0] )
				if flask.request.form['password'] == pwd:
					user = User()
					user.id = email
					flask_login.login_user(user) #okay login in user
					return flask.redirect(flask.url_for('main')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"



@app.route('/logout')
def logout():
	flask_login.logout_user()
	return flask.redirect(flask.url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    #example of formatting a string, and creating a link
    return render_template('error404.html')





if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)
