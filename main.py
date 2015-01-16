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
import jinja2
import os
import google.appengine.api.mail
from google.appengine.ext import db
from google.appengine.api import mail

template_dir=os.path.join(os.path.dirname(__file__), 'templates')
jinja_env=jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape=True)
########################################### For DB ###########################################################
class Clue(db.Model):    
    group=db.StringProperty(required = True, indexed=True)
    to = db.StringProperty(required = True)
    clue = db.StringProperty(required = True)
    created=db.DateTimeProperty(auto_now_add = True)
    

########################################### End of DB ###########################################################

########################################### For Log in ###########################################################
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
	    self.response.out.write(*a, **kw)
		
    def render_str(self,template,**params):
	    t=jinja_env.get_template(template)
	    return t.render(params)
		
    def render(self, template, **kw):
	    self.write(self.render_str(template, **kw))
	

class Login(Handler):
    def get(self):
	    self.render("formforlogin.html",error="")

class Loginpost(Handler):
    def post(self):
        submit=self.request.get('Submit')
        
        if submit:
            username = self.request.get('Username')
            password = self.request.get('Password')   
            #if  str(username):
            #    self.response.out.write("Enter User name")
            #if  password:
             #   self.response.out.write("Enter password")
            if username and password:
                User_tuple=db.GqlQuery("SELECT * From Users WHERE username =:user ", user=username)	
                verify_user=User_tuple.get()
                if verify_user.password == password:
                    self.redirect("/clues?group=%s" %username)
                else:
                    error="Password is invalid!"
                    self.render("formforlogin.html",error=error) 
                    #self.response.out.write("Username or password is invalid!")
            else:
                error=" Username or password is invalid!"
                self.render("formforlogin.html",error=error)
                
        else:    
            self.redirect("/main")
	#self.redirect("/main")
########################################### End of Log in ########################################################

########################################### start of random assigning ########################################################    
class Homepage(Handler):
    def get(self):
        #self.response.out.write("Welcome aboard")
        group=self.request.get("group")
        names=self.request.get_all('Name')
        emails=self.request.get_all('Email')
        names=[str(name) for name in names]
        emails=[str(email) for email in emails]
        #for email in emails:
         #   if not mail.is_email_valid(email):
          #      error="Email is not valid."
        namecount=0
        emailcount=0
        for name in names:
            if name:
                namecount=namecount+1
        for email in emails:
            if email:
                emailcount=emailcount+1
        if namecount==emailcount:
            self.render("addparticipants.html", names=names,emails=emails,message="",error="")
            #participants=dict(zip(names,emails)) #dictionary of all names and corresponding emails
        else:
            if namecount>emailcount:
                names.remove(names[0])
            if emailcount>namecount:
                emails.remove(emails[0])
            self.render("formforlogin", names=names,emails=emails,message="",error="Enter both names and email")
        
    def post(self):
        group=self.request.get("group")
        names=self.request.get_all('Name')
        emails=self.request.get_all('Email')
        names=[str(name) for name in names]
        emails=[str(email) for email in emails]
        #names=names.split()
        add=self.request.get("Add")
        play=self.request.get("Play")
        post=self.request.get('Postaclue')
        if add:
            #for name,email in zip(names,emails):
                #if not name or not email:
                    #self.render("addparticipants.html",names=names,emails=emails,error="Enter both name and email")
                    #self.redirect("/homepage?error=Enter both values")
                    #self.response.write("Enter both name and email")
                
            #self.render("addparticipants.html", names=names,emails=emails,error="")            
            
            namecount=0
            emailcount=0
            for name in names:
                if name:
                    namecount=namecount+1
            for email in emails:
                if email:
                    emailcount=emailcount+1
            if namecount==emailcount:
                self.render("addparticipants.html", names=names,emails=emails,message="",error="")
            #participants=dict(zip(names,emails)) #dictionary of all names and corresponding emails
            else:
                if namecount>emailcount:
                    names.remove(names[0])
                if emailcount>namecount:
                    emails.remove(emails[0])
                self.render("addparticipants.html", names=names,emails=emails,message="",error="Enter both name and email")
            
            
        elif play:
            names=self.request.get_all('Name')
            emails=self.request.get_all('Email')
            names=[str(name) for name in names]
            emails=[str(email) for email in emails]
            namecount=0
            emailcount=0
            
            names.remove(names[0])
            emails.remove(emails[0])
            for name in names:
                if name:
                    namecount=namecount+1
            for email in emails:
                if email:
                    emailcount=emailcount+1
            if namecount == emailcount  and names and emails and namecount>1:
                assignednames=[]
                for name in range(namecount-1):
                    assignednames.append(names[name+1])
                assignednames.append(names[0])
                #for email in range(len(emails)):
                #    message=mail.EmailMessage(sender="<arpita.9118@gmail.com>",subject="Ho Ho Ho! Message from santa")
                #    message.body=""" You are secret santa of <%s>""" %assignednames[email]
                #for email in emails:
                #    message.to="<%s>"%email
                #    message.send()
                
                for email in range(len(emails)):
                    mail.send_mail(sender="<arpita.9118@gmail.com>", to="<%s>"%emails[email],subject="Ho Ho Ho!!",
                                body="""Hello
                                       You are secret santa of %s.
                                     
                                        Merry Christmas!"""  %assignednames[email])
                self.render("addparticipants.html", names=names,emails=emails,message="An email has been sent to all participants")
        
            else:
                self.render("addparticipants.html", names=names,emails=emails,message="Enter proper information")
        
        else:
            self.redirect('/clues?group=%s' %group)
        
########################################### end of random assigning ########################################################     
         
############################################ start of posting clues ########################################################    
class Clues(Handler):
    def render_front(self):
        group=self.request.get("group")
        clues_tuple=db.GqlQuery("Select * from Clue WHERE group=:group ORDER BY created DESC ",group=group)
        #clues_tuple=clues_tuple.get()
        self.render("postclues.html",clues_tuple=clues_tuple)
    
    def get(self):
        self.render_front()   

    def post(self):
        group=self.request.get("Group")
        to=self.request.get("To")
        clue=self.request.get("Clue")
        if to and clue and group:
            c=Clue(group=group,to=to,clue=clue)            
            c.put()
            self.redirect("/clues")
        logout=self.request.get("Logout")
        if logout:
            self.redirect("/")
            
        #self.render_front()        
	
########################################### End of posting clues ########################################################


########################################### For registration #######################################################
#functions for validation
def valid_user(user):
	if user.isalnum():
		
		return user
		
def valid_password(password):
	if password.isalnum():
		return password
		
def match_password(conpass,password):
	if conpass == password:
		return conpass
		
def valid_email(email):
	if mail.is_email_valid(email):
		return email

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
	    self.response.out.write(*a, **kw)
		
    def render_str(self,template,**params):
	    t=jinja_env.get_template(template)
	    return t.render(params)
		
    def render(self, template, **kw):
	    self.write(self.render_str(template, **kw))
	
class MainHandler(Handler):
    def write_form(self,error="",Username="",Password="",confirmpassword="",email=""):
	    self.render("formforregistration.html" ,error=error,Username=Username,Password=Password,confirmpassword=confirmpassword,email=email)
	    
		#self.response.write(form % {"error":error,"Username":Username,"Password":Password,"confirmpassword":confirmpassword,"email":email})
	
    def get(self):
	    self.render("formforregistration.html")
		
class Users(db.Model):    
    username = db.StringProperty(required = True, indexed=True)
    password = db.StringProperty(required = True)
    email=db.StringProperty()    
		
class TestHandler(Handler):
    def write_form(self,error="",Username="",Password="",confirmpassword="",email=""):
       
         self.render("formforregistration.html" ,error=error,Username=Username,Password=Password,confirmpassword=confirmpassword,email=email)
        #self.response.write(form % {"error":error,"Username":Username,"Password":Password,"confirmpassword":confirmpassword,"email":email})
        
    def post(self):
         Username=self.request.get('Username')
         Password=self.request.get("Password")
         confirmpassword=self.request.get("confirmpassword")		
         email=self.request.get("email")
         user=valid_user(Username)
         password=valid_password(Password)
         conpass=match_password(confirmpassword,Password)
         ma=valid_email(email)
         if user and password and conpass and ma:
            User_tuple=db.GqlQuery("SELECT * From Users WHERE username =:user ", user=user)
            User_tuple=User_tuple.get()          
            if not User_tuple:
                u= Users(username=user,password=password,email=ma)
                u.put()
                self.redirect("/thanks?group=%s" %user)		
            else:
                self.write_form("User already exists",Username,Password,confirmpassword,email)                           
         else:
            self.write_form("This is not valid, my friend",Username,Password,confirmpassword,email)
            
			
class Thanks(webapp2.RequestHandler):
    def get(self):
        group=self.request.get("group")
        self.response.out.write("Thanks for registering")
        self.redirect("/homepage?group=%s" %group)   
        
	
		

#class TestHandler(webapp2.RequestHandler):
#	def post(self):
#		q=self.request.get("q")
#		self.response.write(q)

################################################# End of registration #########################################################
app = webapp2.WSGIApplication([
    ('/main', MainHandler),('/testhandler',TestHandler),('/thanks',Thanks),('/',Login),('/homepage',Homepage),('/loginpost',Loginpost),('/clues',Clues)
], debug=True)
