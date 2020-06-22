from models import feeds
from Db import selectEmail,registerUser,addComment,getComment,feedEdit,feedUrlAdd,addLikes,addDislikes
from Db import newRole,getFeeds,checkUserId,checkFeedId,getRole,updateRole,deleteFeed,deleteUser
from flask import Flask,request,render_template
from data import returnData,filtersort,returnRecord,returnNoRepRecord
from flask_bcrypt import Bcrypt
from flask_jwt_extended import  JWTManager,create_access_token
from flask_restful import Resource, Api
from datetime import datetime
import feedparser
import os
import re
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)
app.config['SECRET_KEY']=os.environ.get('SECRET_KEY')
app.config['JWT_SECRET_KEY']=os.environ.get('JWT_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///feeds.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db= SQLAlchemy(app) 
admin=Admin(app)

accessToken=None
records=returnRecord()
recordsNoRep=returnNoRepRecord(records)
data=returnData(records)
allFeeds=data[0]
category=data[1]

# Register
class register(Resource):
    def post(self):
        first_name = request.get_json()['first_name']
        last_name = request.get_json()['last_name']
        email = request.get_json()['email']
        password = bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')
        records=selectEmail(email)
        def hasNumbers(inputString):
            return any(char.isdigit() for char in inputString)
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if(bool(hasNumbers(first_name))==True or bool(hasNumbers(last_name))==True or len(password)<8 or bool(re.search(regex,email))==False ):
            return {'Format': 'False'}, 401
        if records==None:
            registerUser(first_name,last_name,email,password,'user')
            access_token = create_access_token(identity = {'email': email})
            accessToken=access_token
            return {"access_token": access_token}, 201
        else:
            return {'access_token': 'None'}, 401

# Login
class login(Resource):
    def post(self):
        email = request.get_json()['email']
        password = request.get_json()['password']
        records=selectEmail(email)
        if records==None:
            return {'Format': 'False'}, 401    
        elif bcrypt.check_password_hash(records[5], password):
            getRole(records[1])
            access_token = create_access_token(identity = {'email': email})
            accessToken=access_token
            return {"access_token": access_token}, 201
        else:   
            return {'Format': 'False'}, 401

# Returns category
class categoryList(Resource):
    def get(self):
        return {'category': category}, 200

# Get Feed by passing id
class getFeedById(Resource):
    def get(self,feedId):
        if checkFeedId(feedId):
            return {'format':'True','feeds': post, 'id': 'True'}, 200
        else:
            return {'format':'False'}, 401


# Returns feeds,keys of feeds,apply sorts and filters.
# Feeds returned after all the filters and sorts
class getValuesById(Resource):
    def get(self,category,filterType,order,time,page,key=None,search=None):
        feeds=[]
        records=returnRecord()
        recordsNoRep=returnNoRepRecord(records)
        result = filtersort(category.capitalize(),filterType,order,time,records,recordsNoRep,key,search)
        if filterType == "likes":
            if len(result[0][filterType][int(key)])%10 < 5:
                pageno=round(len(result[0][filterType][int(key)])/10)+1
            else:
                pageno=round(len(result[0][filterType][int(key)])/10)
            if pageno == page:
                i=page
                lp=len(result[0][filterType][int(key)])-((round(len(result[0][filterType][int(key)])/10)))*10
                print("feeds2",lp)
                for i in range(i*10-10,(i*10-10)+lp):
                    feeds.append(result[0][filterType][int(key)][i])
            elif pageno > page: 
                i=page
                for i in range(i*10-10,i*10):
                    feeds.append(result[0][filterType][int(key)][i])
            else:
                return {'Format': 'False'} ,400
        else:
            if len(result[0][filterType][key.capitalize()])%10 < 5:
                pageno=round(len(result[0][filterType][key.capitalize()])/10)+1
            else:
                pageno=round(len(result[0][filterType][key.capitalize()])/10) 
            if pageno == page:
                i=page
                lp=len(result[0][filterType][key.capitalize()])%10
                for i in range(i*10-10,i*10-10+lp):
                    feeds.append(result[0][filterType][key.capitalize()][i])
            elif pageno > page: 
                i=page
                for i in range(i*10-10,i*10):
                    feeds.append(result[0][filterType][key.capitalize()][i])
            else:
                return {'Format': 'False'} ,400
        return feeds, 200

# Get feed values
class getValues(Resource):
    def get(self,category,filterType,order,time,key=None,search=None):
        records=returnRecord()
        recordsNoRep=returnNoRepRecord(records)
        result = filtersort(category.capitalize(),filterType,order,time,records,recordsNoRep,key,search)
        return result, 200

# Handled get and post comments
class handleComment(Resource):
    def get(self,feedId=1):
        if checkFeedId(feedId):
            return getComment(feedId),200
        else:
            return {'Format': 'False'}, 400
    def post(self):
        feedId = request.get_json()['feedId']
        userId = request.get_json()['userId']
        comments = request.get_json()['comments']
        if checkFeedId(feedId) and checkUserId(userId):
            return addComment(feedId,userId,comments), 200
        else:
            return {'Format': 'False'}, 400

# User Template, A new feed by user            
class userTemplate(Resource):
    def post(self):
        feedsList=[]
        userId=request.get_json()['userId']
        feedTitle=request.get_json()['feedTitle']
        summary=request.get_json()['summary']        
        imageUrl=request.get_json()['imageUrl']
        category=request.get_json()['category']
        author=request.get_json()['author']
        link=request.get_json()['link']
        logo='https://th.bing.com/th/id/OIP.w2McZSq-EYWxh02iSvC3xwHaHa?pid=Api&rs=1'
        likes=0,
        dislikes=0,
        time= datetime.now()
        time=str(time.strftime('%Y-%m-%d %H:%M:%S'))+'+5:30' 
        times = datetime.strptime(time[:19],'%Y-%m-%d %H:%M:%S')
        dispTime= str(times.strftime('%H:%M:%S %d %B %Y,%A'))
        d = datetime.strptime(dispTime[:5],"%H:%M")
        dispTime=str(d.strftime("%I:%M %p"))+' on '+dispTime[8:]
        feedsList.append(feeds(feedTitle,summary,time,imageUrl,category,author,link,dispTime,logo,userId))
        
        if len(feedTitle)==0 or len(summary)==0 or len(author)==0 or checkUserId(userId)==0:
            return {'Format':'False'}, 400
        if len(imageUrl)==0:
            imageUrl='https://www.zylogelastocomp.com/wp-content/uploads/2019/03/notfound.png'
        if len(category)==0:
            category='Headline'
        value=getFeeds(feedsList,1)
        if value==0:
            return {'Format':'False'}, 400
        else:
            return {'Format':'True'}, 200

# Edit a feed
class  editFeed(Resource):
    def post(self, feedId):
        title = request.get_json()['title']
        summary = request.get_json()['summary']
        category=request.get_json()['category']
        author=request.get_json()['author']
        link=request.get_json()['link']
        fId = checkFeedId(feedId)
        if fId:
            records=feedEdit(title,summary,category,author,link,feedId)
            return {'Format': 'True'}, 200
        else:
            return {'Format': 'False'}    

# Admin
# Adding a new feedXml
class addUrl(Resource):
    def post(self):
        url = request.get_json()['url']
        parsed=feedparser.parse(url)
        categoryUrl = request.get_json()['category'].capitalize()
        if categoryUrl in category:
            if len(parsed.feed)!=0:
                feedUrl = feedUrlAdd(url,categoryUrl)
                return feedUrl
        return {'Format': 'False'}

# Admin
# Adding a new role        
class addRole(Resource):
    def post(self):
        role = request.get_json()['role']
        create = request.get_json()['create']
        read = request.get_json()['read']
        update = request.get_json()['update']
        delete = request.get_json()['delete']
        return newRole(role,create,read,update,delete), 200

# Admin         
# Adding a new role by admin
class adminRegister(Resource):
    def post(self):
        first_name = request.get_json()['first_name']
        last_name = request.get_json()['last_name']
        email = request.get_json()['email']
        role = request.get_json()['role']
        password = bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')
        records=selectEmail(email)
        if records==None:
            registerUser(first_name,last_name,email,password,role)
            access_token = create_access_token(identity = {'email': email})
            accessToken=access_token
            return {"access_token": access_token}, 201
        else:
            return {'Format': 'False'}, 401

# Increase dislikes
class incrementDislikes(Resource):
    def post(self,userId,feedId):
        uId = checkUserId(userId)
        if uId:
            fId = checkFeedId(feedId)
            if fId:
                disLikes = addDislikes(userId,feedId)
                return {'Format': 'True'}, 200              
            else:
                return {'Format': 'False'}, 400
        else:
            return {'Format': 'False'}, 400

# Increase likes
class incrementLikes(Resource):
    def post(self,userId,feedId):
        uId = checkUserId(userId)
        if uId:
            fId = checkFeedId(feedId)
            if fId:
                likes = addLikes(userId,feedId)
                return {'Format': 'True'}, 200              
            else:
                return {'Format': 'False'}, 400
        else:
            return {'Format': 'False'}, 400

# Admin    
# Handle roles
class handleRoles(Resource):
    def get(self,role=None,c=None,r=None,u=None,d=None,userId=None):
        if role==None and userId==None:
            return getRole()
        elif role!=None and userId==None:
            return updateRole(role,c,r,u,d)
        else:
            if checkUserId(userId):
                return updateRole(role,c,r,u,d,userId)
            else:
                return {'Format': 'False'}, 401

# Admin
# Delete User
class deleteUserById(Resource):
    def get(self,userId):
        if checkUserId(userId):
            deleteUser(userId)
            return {'Format': 'True'}, 200              
        else:
            return {'Format': 'False'}, 401

# Admin
# Delete Feed
class deleteFeedById(Resource):
    def get(self,feedId,userId):
        if checkFeedId(feedId) and checkUserId(userId):
            deleteFeed(feedId,userId)
            return {'Format': 'True'}, 200              
        else:
            return {'Format': 'False'}, 401


api.add_resource(register,'/users/register')
api.add_resource(login,'/users/login')
api.add_resource(categoryList,'/category')
api.add_resource(getFeedById,'/feed/<int:feedId>')
api.add_resource(getValues,'/types/<string:category>/<string:filterType>/<string:order>/<string:time>')
api.add_resource(getValuesById,'/types/<string:category>/<string:filterType>/<string:order>/<string:time>/<int:page>/<string:key>/<string:search>','/types/<string:category>/<string:filterType>/<string:order>/<string:time>/<int:page>/<string:key>')
api.add_resource(handleComment,'/comment','/comment/<string:feedId>')
api.add_resource(userTemplate,'/usertemplate')
api.add_resource(editFeed,'/edit/<int:feedId>')
api.add_resource(incrementLikes,'/incrementLikes/<int:userId>/<int:feedId>')
api.add_resource(incrementDislikes,'/incrementDislikes/<int:userId>/<int:feedId>')
api.add_resource(addUrl,'/addUrl')
api.add_resource(addRole,'/addRole')
api.add_resource(handleRoles,'/roles','/roles/<string:role>/<int:c>/<int:r>/<int:u>/<int:d>','/roles/<string:role>/<int:c>/<int:r>/<int:u>/<int:d>/<int:userId>')
api.add_resource(deleteUserById,'/users/delete/<int:userId>')
api.add_resource(deleteFeedById,'/users/deletefeed/<int:feedId>/<int:userId>')

class FeedXmls(db.Model):
    __tablename__="feedXmls"
    feedXmlId=db.Column('feedXmlId',db.Integer,primary_key=True)
    feedXml=db.Column('feedXml',db.String)
    category=category=db.Column('category',db.String)

class Roles(db.Model):
    __tablename__="roles"
    adminId= db.Column('adminId',db.Integer,primary_key=True)
    role=db.Column('role',db.String)
    cFeed= db.Column('cFeed',db.Boolean)
    rFeed= db.Column('rFeed',db.Boolean)
    uFeed= db.Column('uFeed',db.Boolean)
    dFeed= db.Column('dFeed',db.Boolean)

class Users(db.Model):
    __tablename__="users"
    userId=db.Column('userId',db.Integer,primary_key=True)
    adminId=db.Column('adminId',db.Integer,db.ForeignKey('roles.adminId'))
    roles = db.relationship("Roles", backref='adminId_roles')
    firstname=db.Column('firstname',db.String)
    lastname=db.Column('lastname',db.String)
    password=db.Column('password',db.Unicode)
    email=db.Column('email',db.String)
    cFeed=db.Column('cFeed',db.Boolean)
    rFeed=db.Column('rFeed',db.Boolean)
    uFeed=db.Column('uFeed',db.Boolean)
    dFeed=db.Column('dFeed',db.Boolean)
    
class Feeds(db.Model):
    __tablename__="feeds"
    feedId=db.Column('feedId',db.Integer,primary_key=True)
    userId=db.Column('userId',db.Integer,db.ForeignKey('users.userId'))
    users = db.relationship("Users", backref='userId_feeds')
    feedTitle=db.Column('feedTitle',db.String)
    summary=db.Column('summary',db.String)
    time=db.Column('time',db.String)
    imageUrl=db.Column('imageUrl',db.String)
    category=db.Column('category',db.String)
    author=db.Column('author',db.String)
    link=db.Column('link',db.String)
    likes=db.Column('likes',db.Boolean)
    dislikes=db.Column('dislikes',db.Boolean)
    dispTime=db.Column('dispTime',db.String)
    logo=db.Column('logo',db.String)

class Comments(db.Model):
    __tablename__="comments"
    commentId=db.Column('commentId',db.Integer,primary_key=True)
    userId=db.Column('userId',db.Integer,db.ForeignKey('users.userId'))
    users = db.relationship("Users", backref='userId_comments')
    feedId=db.Column('feedId',db.Integer,db.ForeignKey('feeds.feedId'))
    feeds = db.relationship("Feeds", backref='feedId_comments')
    comment=db.Column('comment',db.String)

class UserLike(db.Model):
    __tablename__="userLike"
    userId=db.Column('userId',db.Integer,db.ForeignKey('users.userId'))
    users = db.relationship("Users", backref='userId_userlike')
    feedId=db.Column('feedId',db.Integer,db.ForeignKey('feeds.feedId'))
    feeds = db.relationship("Feeds", backref='feedId_userlike')
    like=db.Column('like',db.Boolean)
    dislike=db.Column('dislike',db.Boolean)
    likeId=db.Column('likeId',db.Integer,primary_key=True)

db.create_all()

admin.add_view(ModelView(Roles, db.session))
admin.add_view(ModelView(FeedXmls, db.session))
admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(Feeds, db.session))
admin.add_view(ModelView(Comments, db.session))
admin.add_view(ModelView(UserLike, db.session))

if __name__=='__main__':
    app.run(debug=True)
