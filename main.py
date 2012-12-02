# Pie Blog
# A web application by Mario Andrei Pantoja Maguina
import os
import webapp2
import jinja2
import random
import hashlib
import hmac
import re

# thanks to Damien Miller.
# and Shay Erlichmen for bcrypt 
import bcrypt




from signup import *

#string and db
from string import letters
from google.appengine.ext import db

#de donde pilla jinja los templates
template_dir=os.path.join(os.path.dirname(__file__),'templates')
jinja_env=jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)



# el secreto usado para crear el hash+salt 
secret = 'fart'

#definimos las funciones que crean el hash+salta
#una que lo crea y devuelve el hash concatenado con
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

# el render de jinja necesita un html (template) y
# una sere de parametros que seran los valores que se
# reemplazaran

def render_str(template,**params):
	t=jinja_env.get_template(template)
	return t.render(params)





##############################################################
# Blog Handler
##############################################################

class BlogHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)

	def render_str(self, template, **params):
		params['user'] = self.user
		return render_str(template,**params)

	def render(self, template,**kw):
		self.write(self.render_str(template,**kw))

	def set_secure_cookie(self, name, val):
		cookie_val = make_secure_val(val)
		self.response.headers.add_header(
			'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))
	
	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, user):
		self.set_secure_cookie('user_id', str(user.key().id()))

	def logout(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))

def render_post(response, post):
	response.out.write('<h2><a href="/blog/post/'+post.id+'">'+post.title+' </a></h2>')
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





##############################################################
# db models
##############################################################

class Art(db.Model):
	"""Base de datos for Art"""
	title=db.StringProperty(required=True)
	art=db.TextProperty(required=True)
	created=db.DateTimeProperty(auto_now_add=True) #como en SI1!

class User(db.Model):
	"""Base de datos de usuarios"""
	username=db.StringProperty(required=True)
	#never store the password in plain text
	password=db.StringProperty(required=True)
	realname=db.StringProperty(required=False)
	#avatar = db.BlobProperty()


class Post(db.Model):
	"""Base de datos del Blog"""
	title=db.StringProperty(required=True)
	text=db.TextProperty(required=True)
	created=db.DateTimeProperty(auto_now_add=True) #como en SI1!
	modified=db.DateTimeProperty(auto_now=True)
	permalink=db.IntegerProperty()

	#para convertir el texto con saltos de linea a html.
	def render(self):
		self._render_text = self.text.replace('/n','<br>')
		return render_str("post.html",p= self)


##############################################################
## Handler pagina original
##############################################################

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


##############################################################
### Handlers del Blog
##############################################################

def blog_key(name='default'):
	return db.Key.from_path('blogs',name)


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

class PostPageHuman(BlogHandler):
	"""handler del cada post individual"""
	def get(self, post_id, title):
		#print title
		#print "query<br>"
		query = db.GqlQuery("SELECT __key__ FROM Post WHERE title= :1",title.replace('-',' '))
		#print query
		post=query.get()
	
		ID= post.id()
		#print ID key=db.Key.from_path('Post',int(ID),parent=blog_key())
		key=db.Key.from_path('Post',int(post_id),parent=blog_key())

		#key=db.Key.from_path('Post', ID)
		#print key
		post=db.get(key)
		#self.render('permalink.html', post = post) 
		#mensaje="names"

		#ID=names.id()
		#key=db.Key.from_path('Post', ID)
		#post=db.get(key)
		if not post:
			self.error(404)
			return
		self.render('permalink.html', post=post)

##############################################################
### Handlers del SignUp y Login
##############################################################
class SignUpHandler(Handler):
	"""Clase que controla el formulario de Sign Up"""
	def get(self):
		self.render("signup.html")

	def post(self):
		username=self.request.get('username')
		password=self.request.get('password')
		verify=self.request.get('verify')
		realname=self.request.get('realname')



		if not valid_username(username):
			error="no es valido ese username"
			self.render("signup.html", error_username=error)

		if not valid_password(password):
			error="no es valido ese password"
			self.render("signup.html", error_password=error)

		hashed = bcrypt.hashpw(password, bcrypt.gensalt())

		if username and password:
			u=User(username=username, password=password, realname=realname)
			u.put()
			self.redirect("/dashboard")
		else:
			error="tiene que rellenar los campos!"
			self.render("signup.html", error=error)

class Login(BlogHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')



##############################################################
### dashboard
##############################################################

class DashboardHandler(BlogHandler):
    def get(self):
        if self.user:
            self.render('dashboard.html', username = self.user.name)
        else:
            self.redirect('/signup')


##############################################################
### Nuevo Post
##############################################################

class NewPost(BlogHandler):
	"""handler del creador de post"""
	def get(self):
		self.render("newpost.html")

	def post(self):
		title = self.request.get('title')
		text = self.request.get('text')
		permalink=title.replace(' ','-')
		#truncate permalink
		#control if it already exists?
		permalink=permalink[:40]
		if title and text:
			p = Post(parent = blog_key(), title = title, text = text)
			p.put()
			#self.redirect('/blog/post/%s' % str(p.key().id()))
			self.redirect('/blog/post/%s/%s' % (str(p.key().id()), permalink))

		else:
			error = "title and text must be filled!"
			self.render("newpost.html", title=title, text=text, error=error)




##############################################################
###
###      ##############################################
###      ##      ##                    ##           ### 
###      ##      ##                    ##           ### 
###      ##########                    ################
### 
##############################################################


app = webapp2.WSGIApplication([('/', MainPage),
	('/blog/?', BlogMainPage),
	('/signup', SignUpHandler),
	('/blog/dashboard', DashboardHandler),
	('/blog/post/([0-9]+)/*',PostPage),
	('/blog/post/([0-9]+)/([a-z,A-Z,0-9]+)',PostPageHuman),
	('/blog/newpost', NewPost)], debug=True)
#app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
