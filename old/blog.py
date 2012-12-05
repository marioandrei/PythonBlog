# A web application by Mario Andrei Pantoja Maguina
import os
import webapp2
import jinja2

import re

#import blog

from string import letters

from google.appengine.ext import db

template_dir=os.path.join(os.path.dirname(__file__),'templates')
jinja_env=jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
	"""auxiliares para los templates"""
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)
	def render_str(self, template, **params):
		t=jinja_env.get_template(template)
		return t.render(params)
	def render(self, template,**kw):
		self.write(self.render_str(template,**kw))

class Art(db.Model):
	"""Base de datos for Art"""
	title=db.StringProperty(required=True)
	art=db.TextProperty(required=True)
	created=db.DateTimeProperty(auto_now_add=True) #como en SI1!


class MainPage(Handler):
	def render_index(self, title="", art="", error=""):
		arts = db.GqlQuery("SELECT * FROM Art "
			" ORDER BY created DESC ")
		self.render("index.html",title=title,art=art,error=error, arts=arts)

	def get(self):
		self.render_index()

	def post(self):
		title=self.request.get("title")
		art=self.request.get("art")

		if title and art:
			a=Art(title=title, art=art)
			a.put()
			self.redirect("/")
		else:
			error="we need both a title and some artwork"
			self.render_index(title,art,error)  



### new


class BlogHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)

	def render_str(self, template, **params):
		t=jinja_env.get_template(template)
		return t.render(params)

	def render(self, template,**kw):
		self.write(self.render_str(template,**kw))

class Post(db.Model):
	"""Base de datos del Blog"""
	title=db.StringProperty(required=True)
	text=db.TextProperty(required=True)
	created=db.DateTimeProperty(auto_now_add=True) #como en SI1!
	permalink=db.IntegerProperty()

class BlogMainPage(Handler):
	def render_index(self, title="", art="", error=""):
		arts = db.GqlQuery("SELECT * FROM Art "
			" ORDER BY created DESC ")
		self.render("blog.html",title=title,art=art,error=error, arts=arts)

	def get(self):
		self.render_index()

	def post(self):
		title=self.request.get("title")
		art=self.request.get("art")

		if title and art:
			a=Art(title=title, art=art)
			a.put()
			self.redirect("/blog")
		else:
			error="we need both a title and some artwork"
			self.render_index(title,art,error)  

app = webapp2.WSGIApplication([('/', MainPage),
	('/blog', BlogMainPage),
	('/blog/newpost', BlogMainPage)], debug=True)
#app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
