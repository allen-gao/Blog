#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import webapp2
import jinja2
import re
import hashlib
import random
import string

from google.appengine.ext import db
from random import randint

template_dir= os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

import userkey
user_key = userkey.key

# The following Handler class is obtained from CS253 on Udacity
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Posts(db.Model):
	title = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	user = db.StringProperty(required = True)

class Users(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class NewPostHandler(Handler):
	def render_front(self, title="", content="", error_message=""):
		data = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC LIMIT 10")
		self.render("newpost.html", title=title, content=content, error_message=error_message, data=data, 
					valid_cookie=check_username_cookie(self.request.cookies.get("name")))
	def get(self):
		self.render_front()
	def post(self):
		title = self.request.get("subject")
		content = self.request.get("content")
		if check_username_cookie(self.request.cookies.get("name")) == False:
			self.redirect('/signup')
		elif title == "" and content == "":
			self.render_front(error_message="You're missing the title and content!")
		elif title == "":
			self.render_front(content=content, error_message="You're missing the title!")
		elif content == "":
			self.render_front(title=title, error_message="You're missing the blog's content!")
		else:
			user_id = (self.request.cookies.get("name")).split('|')[0]
			users = db.GqlQuery("SELECT * FROM Users")
			user = "Anonymous"
			for x in users:
				if user_id == str(x.key().id()):
					user = x.username


			content = Posts(title = title, content = content, user=user)
			post = content.put()
			self.redirect("/post/%s" % post.id())

class MainPage(Handler):
	def get(self):
		data = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC LIMIT 25")
		self.render("main_page.html", data=data, valid_cookie=check_username_cookie(self.request.cookies.get("name")))

class PostHandler(Handler):
	def get(self, id):
		id = int(id)
		post = Posts.get_by_id(int(id))
		self.render("single_post.html", subject=post.title, content=post.content, id=id, time=post.created.strftime("%B %d, %Y"))


def valid_username(username):
	USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
	return USER_RE.match(username)


def valid_password(password):
	USER_RE = re.compile(r"^.{3,20}$")
	return USER_RE.match(password)


def valid_email(email):
	USER_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
	return email == "" or USER_RE.match(email)

def create_user_hash(username):
	return username + '|' + hashlib.sha256(user_key + username).hexdigest()

def check_username_cookie(hash):
	if not isinstance(hash, basestring):
		return False
	list = hash.split('|')
	if len(list) != 2:
		return False
	return hash == create_user_hash(list[0])

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw):
    salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    list = h.split(',')
    salt = list[1]
    print salt
    hash = list[0]
    return hashlib.sha256(name + pw + salt).hexdigest() == hash

def taken_username(username):
	lower_name = username.lower()
	data = db.GqlQuery("SELECT * FROM Users")
	for x in data:
		if lower_name == (x.username).lower():
			return True
	return False
        	

class SignupHandler(Handler):
    def get(self):
    	self.render("signup.html", name="", p1="", p2="", email="", name_error="", p1_error="", p2_error="", email_error="")
    def post(self):
    	username = self.request.get("username")
    	p1 = self.request.get("password")
    	p2 = self.request.get("verify")
    	email = self.request.get("email")
    	# Here are the placeholders:
    	p_name_error = ""
    	p_email_error = ""
    	p1_error = ""
    	p2_error = ""
        if not valid_username(username):
        	p_name_error = "Please enter a valid username"
        if taken_username(username):
        	p_name_error = "Username already taken!"
        if not valid_email(email):
        	p_email_error = "Please enter a valid email"
        if not valid_password(p1):
        	p1_error = "Please enter a valid password"
        if p1 != p2:
        	p2_error = "The passwords don't match"
        if valid_username(username) and valid_password(p1) and (p1 == p2) and valid_email(email) and not taken_username(username):
        	user = Users(username=username, password=make_pw_hash(username, p1))
        	id = user.put().id()
        	hash = create_user_hash(str(id))
        	self.response.headers.add_header("Set-Cookie", str("name=%s" % hash))
        	self.redirect("/welcome")
        self.render("signup.html", name=username, p1="", p2="", email=email, name_error=p_name_error, p1_error=p1_error, p2_error=p2_error, email_error=p_email_error)
   

class WelcomeHandler(Handler):
	def get(self):
		hash = self.request.cookies.get("name", "")
		if check_username_cookie(hash):
			list = hash.split('|')
			id = list[0]
			data = db.GqlQuery("SELECT * FROM Users")
			name = "new user"
			for x in data:
				if id == str(x.key().id()):
					name = x.username
			self.render("welcome.html", name=name)
		else:
			self.redirect('/signup')

class LoginHandler(Handler):
	def get(self):
		self.render("login.html")
	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		data = db.GqlQuery("SELECT * FROM Users")
		for x in data:
			if x.username == username:
				if valid_pw(username, password, x.password):
					hash = create_user_hash(str(x.key().id()))
					self.response.headers.add_header("Set-Cookie", str("name=%s; Path=/" % hash))
					self.redirect('/welcome')
		self.render("login.html", error="Incorrect Username/Password")


class LogoutHandler(Handler):
        def get(self):
                self.response.headers.add_header("Set-Cookie", str("name=; Path=/"))
                self.redirect('/signup')



app = webapp2.WSGIApplication([
	('/newpost', NewPostHandler), 
	('/post/(\d+)', PostHandler), 
	('/', MainPage),
	('/signup', SignupHandler),
	('/welcome', WelcomeHandler),
	('/login', LoginHandler),
	('/logout', LogoutHandler)
	], debug=True)
