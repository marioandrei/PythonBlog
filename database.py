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