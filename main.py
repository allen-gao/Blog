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

from google.appengine.ext import db
from random import randint

template_dir= os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


# The following Handler class is obtained for CS253 on Udacity
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Data(db.Model):
	title = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
	def render_front(self, title="", content="", error_message=""):
		data = db.GqlQuery("SELECT * FROM Data ORDER BY created DESC")
		self.render("form.html", title=title, content=content, error_message=error_message, data=data)

	def get(self):
		self.render_front()
	def post(self):
		title = self.request.get("subject")
		content = self.request.get("content")
		if title == "" and content == "":
			self.render_front(error_message="You're missing the title and content!")
		elif title == "":
			self.render_front(content=content, error_message="You're missing the title!")
		elif content == "":
			self.render_front(title=title, error_message="You're missing the blog's content!")
		else:
			content = Data(title = title, content = content)
			post = content.put()
			self.redirect("/post/%s" % post.id())

class MainPage(Handler):
	def get(self):
		data = db.GqlQuery("SELECT * FROM Data ORDER BY created DESC")
		self.render("main_page.html", data=data)

class PostHandler(Handler):
	def get(self, id):
		id = int(id)
		post = Data.get_by_id(int(id))
		self.render("single_post.html", subject=post.title, content=post.content, id=id, time=post.created)


def valid_username(username):
	USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
	return USER_RE.match(username)


def valid_password(password):
	USER_RE = re.compile(r"^.{3,20}$")
	return USER_RE.match(password)


def valid_email(email):
	USER_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
	return email == "" or USER_RE.match(email)


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
        if not valid_email(email):
        	p_email_error = "Please enter a valid email"
        if not valid_password(p1):
        	p1_error = "Please enter a valid password"
        if p1 != p2:
        	p2_error = "The passwords don't match"
        if valid_username(username) and valid_password(p1) and (p1 == p2) and valid_email(email):
        	self.response.headers.add_header("Set-Cookie", str("name=%s" % username))
        	self.redirect("/welcome")
        else:
        	self.render("signup.html", name=username, p1="", p2="", email=email, name_error=p_name_error, p1_error=p1_error, p2_error=p2_error, email_error=p_email_error)
   
class WelcomeHandler(Handler):
	def get(self):
		name = self.request.cookies.get("name")
		self.write("Welcome, %s" % name)


app = webapp2.WSGIApplication([
	('/newpost', MainHandler), 
	('/post/(\d+)', PostHandler), 
	('/', MainPage),
	('/signup', SignupHandler),
	('/welcome', WelcomeHandler)
	], debug=True)
