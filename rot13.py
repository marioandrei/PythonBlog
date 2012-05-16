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
import webapp2
import cgi
import re
import string

def escape_html(s):
	return cgi.escape(s, quote = True)

rot13_form="""<html><body>
    <h2>Enter some text to ROT13:</h2>
    <form method="post">
      <textarea name="text" style="height: 100px; width: 400px;">%(text)s</textarea>
      <br>
      <input type="submit">
    </form>
  

</body></html>"""

sign_up_form="""
<!DOCTYPE html>

<html>
  <head>
    <title>Sign Up</title>
    <style type="text/css">
      .label {text-align: right}
      .error {color: red}
    </style>

  </head>

  <body>
    <h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">
            Username
          </td>
          <td>
            <input type="text" name="username" value="%(username)s">
          </td>
          <td class="error">
            
          </td>
        </tr>

        <tr>
          <td class="label">
            Password
          </td>
          <td>
            <input type="password" name="password" value="">
          </td>
          <td class="error">
            
          </td>
        </tr>

        <tr>
          <td class="label">
            Verify Password
          </td>
          <td>
            <input type="password" name="verify" value="">
          </td>
          <td class="error">
            
          </td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value="">
          </td>
          <td class="error">
            
          </td>
        </tr>
      </table>

      <input type="submit">
    </form>
  </body>

</html>
"""

form="""
<form method="post">
	<label> Day
		<input type="text" name="day" value="%(day)s"> 
	</label>

	<label> Month
		<input type="text" name="month" value="%(month)s"> 
	</label>
		
	<label> Year
		<input type="text" name="year" value="%(year)s"> 
	</label>
	<div style="color: red">%(error)s</div>
	<br>
	<br>


	<input type="submit">
</form>

"""

months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']

month_abbvs=dict((m[:3].lower(),m) for m in months)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")

def valid_username(username):
    return USER_RE.match(username)
def valid_password(password):
    return USER_RE.match(password)

def rot13(s):
	return s.encode("rot13")


def valid_month(month):
	if month:
		short_month=month[:3].lower()
		return month_abbvs.get(short_month)
		

def valid_day(day):
	if day and day.isdigit():
		day=int(day)
		if day>0 and day<=31:
			return day

def valid_year(year):
	if year and year.isdigit():
		year=int(year)
		if year>1900 and year<2020:
			return year

          

class MainPage(webapp2.RequestHandler):
	def write_form(self, error="", month="", day="", year=""):
		self.response.out.write(form %{"error": error, "month": escape_html(month), "day": escape_html(day), "year": escape_html(year) })
	
	def get(self):
		self.write_form()

	def post(self):
		user_month = self.request.get('month')
		user_day = self.request.get('day')
		user_year = self.request.get('year')

		month = valid_month(user_month)
		day = valid_day(user_day)
		year = valid_year(user_year)

		if not(month and day and year):
			self.write_form("That doesn't look valid to me, friend.", user_month, user_day, user_year)
		else:
			self.redirect("/thanks")

class ThanksHandler(webapp2.RequestHandler):
	def get(self):
		self.response.out.write("THANKS")

class SignupHandler(webapp2.RequestHandler):
	"""docstring for SignupHandler"""
	def write_signup_form(self, username=""):
		self.response.out.write(sign_up_form %{"username": username })
	
	def get(self):
		self.write_signup_form()

	def post(self):
		username=self.request.get('username')
		string.equal

		if :
			pass
		self.request.get('password')
#si es valido el username, el password es el mismo y valido y si el correo
# es valido (comprobar las primar parte @ y el dominio . com) 

		self.redirect("/thanks")


	

		
class Rot13Handler(webapp2.RequestHandler):
	"""pagina que convierte txto a Rot13"""
	
	
	def write_form_rot(self, text=""):
		self.response.out.write(rot13_form %{"text": escape_html(text) })
	
	def get(self):
		self.write_form_rot()

	def post(self):
		user_text = self.request.get('text')
		#self.response.out.write(texto)
		self.write_form_rot(rot13(user_text))

app = webapp2.WSGIApplication([('/', MainPage),
	('/thanks', ThanksHandler),
	('/rot13', Rot13Handler),
	('/signup', SignupHandler)], debug=True)
