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
import uuid

import webapp2
import os
import hashlib
import time
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template


signupPath = os.path.join(os.path.dirname(__file__), 'signupform.html')
loginPath = os.path.join(os.path.dirname(__file__), 'loginform.html')
welcomePath = os.path.join(os.path.dirname(__file__), 'welcome.html')
blogPath = os.path.join(os.path.dirname(__file__), 'blogform.html')
contentPath = os.path.join(os.path.dirname(__file__), 'blogcontent.html')



class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def makeHash(self,pwd):
        return hashlib.sha256(pwd).hexdigest()


class Users(ndb.Model):
    userName = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    emailId = ndb.StringProperty(required=True)

class Blogs(ndb.Model):
    name = ndb.StringProperty(required=True)
    title = ndb.StringProperty(required=True)
    content = ndb.StringProperty(required=True)
    millis = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)


class Cookies(ndb.Model):
    name = ndb.StringProperty(required=True)



class Welcome(Handler):
    def get(self):
        cookie = str(self.request.cookies.get('user',""))
        if cookie:
            user = ndb.Key(Cookies,cookie).get()
            userName = user.name
        else:
            userName = ""
        blog = Blogs.query().order(-ndb.DateTimeProperty("created"))

        self.write(template.render(welcomePath, {"blog": blog,"userName":userName}))


class Login(Handler):
    def get(self):
        if self.request.cookies.get('user',""):
            self.redirect('/')
        else:
            self.write(template.render(loginPath, {"error":""}))

    def post(self):
        userName = self.request.get("userName")
        password = self.makeHash(self.request.get("password"))


        if userName and password:
            try:
                u = Users.query(Users.userName == userName).get()
                if u.password == password:

                    user = Cookies.query(Cookies.name == userName).get()
                    try:
                        cookie = user.key.id()
                        self.response.headers.add_header('Set-Cookie', '%s=%s'%("user",str(cookie)))
                        self.redirect('/')
                    except:
                        self.write("exception")


                else:
                    template_value = {
                        "error":"please enter valid details",
                        "name": userName,
                    }
                    self.write(template.render(loginPath, template_value))
            except:
                template_value={
                    "error":"please signup first",
                    "name":userName
                }
                self.write(template.render(loginPath, template_value))
        else:
            template_value={
                "error":"please fill every section",
                "name":userName
            }
            self.write(template.render(loginPath, template_value))


class Signup(Handler):
    def get(self):
        if self.request.cookies.get('user',""):
            self.redirect('/')
        else:
            self.write(template.render(signupPath, {"error": ""} ))

    def post(self):
        userName = self.request.get("username")
        password = self.makeHash(self.request.get("password"))
        emailId=self.request.get("emailId")
        cookie = str(uuid.uuid1())


        if userName and password and emailId:
            if Users.query(Users.userName == userName).get():
                template_value = {"error":"username already exists"}
                self.write(template.render(signupPath,template_value))
            else:
                cookieStore = Cookies(id=cookie, name=userName)
                cookieStore.put()
                userStore = Users(userName=userName, password=password,emailId=emailId)
                userStore.put()
                self.response.headers.add_header('Set-Cookie','%s=%s'%("user",str(cookie)))
                self.redirect('/')

        else:
            template_value = {
                "error": "please fill every section",
                "name":userName,
                "password":password,
                "emailId":emailId
            }
            self.write(template.render(signupPath, template_value))

class CreateBlog(Handler):
    def get(self):
        self.write(template.render(blogPath,{"blogtitle":""}))
    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        millis = int(round(time.time() * 1000))
        cookie = str(self.request.cookies.get('user', ""))

        user = ndb.Key(Cookies, cookie).get()
        name = user.name

        if title and content and name:
            blogStore = Blogs(name=name, title=title, content=content, millis=millis)
            blogStore.put()

            self.redirect('/')
        else:
            self.write(template.render(blogPath,{"error":"please provide necessary contents"}))


class EditBlog(Handler):


    def get(self,id):
        cookie = str(self.request.cookies.get('user', ""))
        if cookie:
            user = ndb.Key(Cookies, cookie).get()
            userName = user.name
            blog = ndb.Key(Blogs, int(id)).get()
            name = blog.name

        if name == userName:

            title = blog.title
            content = blog.content
            template_value = {
            "blogtitle":title,
            "content":content
            }
            self.write(template.render(blogPath,template_value))
        else:
            self.write("you cant change others blog")

    def post(self,id):
        editedtitle = self.request.get("title")
        content = self.request.get("content")
        #cookie = str(self.request.cookies.get('user', ""))

        #user = ndb.Key(Cookies, cookie).get()
        #name = user.name
        if id:
            blog = ndb.Key(Blogs, int(id)).get()
            blog.title = editedtitle
            blog.content = content
            blog.put()
            self.write("updated successfully")
            self.redirect('/')
        else:
            self.write("something went wrong please try again")


class DeleteBlog(Handler):
    def get(self,id):
        cookie = str(self.request.cookies.get('user', ""))
        if cookie:
            user = ndb.Key(Cookies, cookie).get()
            userName = user.name
            blog = ndb.Key(Blogs, int(id)).get()
            name = blog.name
            if name == userName:
                ndb.Key(Blogs, int(id)).delete()
                self.redirect('/')

        else:
            self.write("you cant delete others blog")




class DisplayContent(Handler):
    def get(self,id):

        bl = ndb.Key(Blogs, int(id)).get()
        content = bl.content
        title = bl.title
        name = bl.name

        cookie = str(self.request.cookies.get('user', ""))
        if cookie:
            user = ndb.Key(Cookies, cookie).get()
            userName = user.name
        else:
            userName = ""
        template_value = {
            "name": name,
            "title": title,
            "content": content,
            "username": userName,
            "id":id
        }
        self.write(template.render(contentPath, template_value))


class Logout(Handler):
    def get(self):
        self.response.delete_cookie('user')
        #self.response.headers.add_header('Set-Cookie', 'user=')
        self.redirect('/')



app = webapp2.WSGIApplication([('/', Welcome),
                               ('/login',Login),
                               ('/signup', Signup),
                               ('/logout', Logout),
                               ('/createblog',CreateBlog),
                               ('/editblog/(\d+)', EditBlog),
                               ('/deleteblog/(\d+)', DeleteBlog),
                               ('/displaycontent/(\d+)',DisplayContent)], debug=True)