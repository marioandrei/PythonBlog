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


def render_str(template,**params):
	t=jinja_env.get_template(template)
	return t.render(params)

# Blog Handler

class BlogHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)

	def render_str(self, template, **params):
		return render_str(template,**params)

	def render(self, template,**kw):
		self.write(self.render_str(template,**kw))


def render_post(response, post):
	response.out.write('<h2>'+post.title+'</h2>')
	response.out.write(post.text)

# Handler de la pagina principal (no del blog, del site)
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



## Handler pagina original

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



### Handlers de cada POST

def blog_key(name='default'):
	return db.Key.from_path('blogs',name)

class Post(db.Model):
	"""Base de datos del Blog"""
	title=db.StringProperty(required=True)
	text=db.TextProperty(required=True)
	created=db.DateTimeProperty(auto_now_add=True) #como en SI1!
	modified=db.DateTimeProperty(auto_now=True)
	permalink=db.IntegerProperty()

	def render(self):
		self._render_text = self.text.replace('/n','<br>')
		return render_str("post.html",p= self)


class BlogMainPage(BlogHandler):
	def get(self):
		posts = db.GqlQuery("select * from Post order by created desc limit 10")
		self.render('front.html', posts = posts) 




class PostPage(BlogHandler):
	"""handler del cada post individual"""
	def get(self,post_id):
		key=db.Key.from_path('Post',int(post_id),parent=blog_key())
		post = db.get(key)

		#si no existe, devolvemos error
		if not post:
			self.error(404)
			return
		self.render("permalink.html", post=post)

class NewPost(BlogHandler):
	"""handler del creador de post"""
	def get(self):
		self.render("newpost.html")

	def post(self):
		title = self.request.get('title')
		text = self.request.get('text')

		if title and text:
			p = Post(parent = blog_key(), title = title, text = text)
			p.put()
			self.redirect('/blog/%s' % str(p.key().id()))
		else:
			error = "title and text must be filled!"
			self.render("newpost.html", title=title, text=text, error=error)

app = webapp2.WSGIApplication([('/', MainPage),
	('/blog/?', BlogMainPage),
	('/blog/([0-9]+)',PostPage),
	('/blog/newpost', NewPost)], debug=True)
#app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
