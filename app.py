from flask import Flask,request,render_template,redirect, url_for,flash
from flask_bcrypt import Bcrypt
from flask_jwt_extended import  JWTManager,create_access_token
from flask_restful import Resource, Api
from datetime import datetime
from sqlalchemy import event
from flask_admin import Admin, AdminIndexView
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user,login_required
import feedparser
import os
import re

app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)
app.config['SECRET_KEY']=os.environ.get('SECRET_KEY')
app.config['JWT_SECRET_KEY']=os.environ.get('JWT_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///feeds.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['FLASK_ADMIN_SWATCH'] = 'Darkly' 
login_manager= LoginManager()
login_manager.init_app(app)
    
class MyAdminIndexView(AdminIndexView):
    def is_visible(self):
        return False
    def is_accessible(self):
        return current_user.is_authenticated
admin=Admin(app,name='Admin Panel',template_mode='bootstrap3',index_view=MyAdminIndexView())

from Db import FeedXmls,Roles,Users,Feeds,Comments,UserLike,SpecialRights,db
from Db import handleDb,getXml,getFeeds
from data import returnRecord,returnNoRepRecord,returnData,filtersort
from Db import selectEmail,registerUser,addComment,getComment,feedEdit,feedUrlAdd,addLikes,addDislikes
from Db import newRole,getFeeds,checkUserId,checkFeedId,getRole,deleteRole,deleteFeed,deleteUser,getSpecialRights, commentDelete,getUser, getAccess, updateAccess,deleteAccess,getPost
from admin import Controllers,RolesController,UsersController,FeedsController,UserLikeController,CommentController,FeedXmlsController,Controller
from admin import hashPass,load_user,adminLogin,adminLogout
from models import feeds



records=returnRecord()
recordsNoRep=returnNoRepRecord(records)
data=returnData(records)
allFeeds=data[0]
category=data[1]
print(category)
#Register
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
            return {'message':'Bad Request','Format': 'False'}, 401
        if records==None:
            registerUser(first_name,last_name,email,password,'user')
            access_token = create_access_token(identity = {'email': email})
            accessToken=access_token
            return {"access_token": access_token,'message':'registered successfully','Format': 'True'}, 201
        else:
            return {'message':'user exist','Format': 'Fasle'}, 401

# Login
class login(Resource):
    def post(self):
        email = request.get_json()['email']
        password = request.get_json()['password']
        records=selectEmail(email)
        if records==None:
            return {'message':'Bad Request','Format': 'False'}, 401    
        elif bcrypt.check_password_hash(records[5], password):
            access_token = create_access_token(identity = {'email': email})
            accessToken=access_token
            return {"access_token": access_token,'message':'loggedin successfully','Format': 'True'}, 201
        else:   
            return {'message':'invalid username or password','Format': 'False'}, 401

# Returns category
class categoryList(Resource):
    def get(self):
        return {'category': category,'Format':'True'}, 200

# Get Feed by passing id
class getFeedById(Resource):
    def get(self,feedId):
        if checkFeedId(feedId):
            post=getPost(feedId)
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
                for i in range(i*10-10,(i*10-10)+lp):
                    feeds.append(result[0][filterType][int(key)][i])
            elif pageno > page: 
                i=page
                for i in range(i*10-10,i*10):
                    feeds.append(result[0][filterType][int(key)][i])
            else:
                return {'message':'Invalid key','Format': 'False'} ,400
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
                return {'message':'Invalid key','Format': 'False'} ,400
        return {'feed':feeds,'format':'True'}, 200

# Get feed values
class getValues(Resource):
    def get(self,category,filterType,order,time,key=None,search=None):
        records=returnRecord()
        recordsNoRep=returnNoRepRecord(records)
        result = filtersort(category.capitalize(),filterType,order,time,records,recordsNoRep,key,search)
        return result, 200

# Handled get and post comments
class handleComment(Resource):
    def get(self):
        feedId = request.get_json()['feedId']
        if checkFeedId(feedId):
            return getComment(feedId),200
        else:
            return {'message':'invalid feedId','Format': 'False'}, 400
    def post(self):
        feedId = request.get_json()['feedId']
        userId = request.get_json()['userId']
        comments = request.get_json()['comments']
        if checkFeedId(feedId) and checkUserId(userId):
            return addComment(feedId,userId,comments), 200
        else:
            return {'message':'feedid or userid doesnt exist','Format': 'False'}, 400
    
    def delete(self):
        commentId = request.get_json()['commentId']
        comment = commentDelete(commentId)
        return comment


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
            return {'message':'Bad Request','Format':'False'}, 400
        if len(imageUrl)==0:
            imageUrl='https://www.zylogelastocomp.com/wp-content/uploads/2019/03/notfound.png'
        if len(category)==0:
            category='Headline'
        value=getFeeds(feedsList,1)
        if value==0:
            return {'message':'Bad Request','Format':'False'}, 400
        else:
            return {'message':'Feed added','Format':'True'}, 200

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
            return {'message':'Feed edited','Format': 'True'}, 200
        else:
            return {'message':'Bad Request','Format': 'False'}    

# Admin
# Adding a new feedXml
class addUrl(Resource):
    def post(self):
        url = request.get_json()['url']
        parsed=feedparser.parse(url)
        categoryUrl = request.get_json()['category']
        if categoryUrl in category:
            if len(parsed.feed)!=0:
                feedUrl = feedUrlAdd(url,categoryUrl)
                return feedUrl
        return {'message':'category not found','Format': 'False'}, 400

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
            return {"access_token": access_token,'message':'registered successfully','Format': 'True'}, 201
        else:
            return {'message':'user exist','Format': 'Fasle'}, 401

# Increase dislikes
class incrementDislikes(Resource):
    def post(self,userId,feedId):
        uId = checkUserId(userId)
        if uId:
            fId = checkFeedId(feedId)
            if fId:
                disLikes = addDislikes(userId,feedId)
                if disLikes==True:
                    return {'message':'post disliked','Format': 'True'}, 200              
                else:
                    return {'message':'post already disliked','Format': 'False'}, 400              
            else:
                return {'message':'feedid doesnt exist','Format': 'False'}, 400
        else:
            return {'message':'userid doesnt exist','Format': 'False'}, 400

# Increase likes
class incrementLikes(Resource):
    def post(self,userId,feedId):
        uId = checkUserId(userId)
        if uId:
            fId = checkFeedId(feedId)
            if fId:
                likes = addLikes(userId,feedId)
                if likes==True:
                    return {'message':'post liked','Format': 'True'}, 200              
                else:
                    return {'message':'post already liked','Format': 'False'}, 400              
            else:
                return {'message':'feedid doesnt exist','Format': 'False'}, 400
        else:
            return {'message':'userid doesnt exist','Format': 'False'}, 400

# Admin
# Delete User
class deleteUserById(Resource):
    def get(self,userId):
        if checkUserId(userId):
            deleteUser(userId)
            return {'message':'user deleted','Format': 'True'}, 200              
        else:
            return {'message':'Bad Request','Format': 'False'}, 401

# Admin
# Delete Feed
class deleteFeedById(Resource):
    def get(self,feedId,userId):
        if checkFeedId(feedId) and checkUserId(userId):
            return deleteFeed(feedId,userId)
        else:
            return {'message':'Bad Request','Format': 'False'}, 401

class user(Resource):
    def get(self,userId):
        user = getUser(userId)
        return user

class role(Resource):
    def get(self):
        return getRole()  
    def delete(self):
        id = request.get_json()['id']
        return deleteRole(id)
    def post(self):
        role = request.get_json()['role']
        return newRole(role)

class access(Resource):
    def get(self):
        userId = request.get_json()['userId']
        return getAccess(userId=None)    
    def post(self):
        userId = request.get_json()['userId']
        colId = request.get_json()['colId']
        cFeed = request.get_json()['cFeed']
        rFeed = request.get_json()['rFeed']
        uFeed = request.get_json()['uFeed']
        dFeed = request.get_json()['dFeed']
        rolesTable = request.get_json()['rolesTable']
        usersTable = request.get_json()['usersTable']
        feedsTable = request.get_json()['feedsTable']
        userLikeTable= request.get_json()['userLikeTable']
        commentTable= request.get_json()['commentTable']
        feedXmlsTable= request.get_json()['feedXmlsTable']
        return updateAccess(userId,colId,cFeed,rFeed,uFeed,dFeed,rolesTable,usersTable,feedsTable,userLikeTable,commentTable,feedXmlsTable)
    def delete(self):
        id = request.get_json()['id']
        return deleteAccess(id)


#App routes
api.add_resource(register,'/users/register')
api.add_resource(login,'/users/login')
api.add_resource(categoryList,'/category')
api.add_resource(getFeedById,'/feed/<int:feedId>')
api.add_resource(getValues,'/types/<string:category>/<string:filterType>/<string:order>/<string:time>')
api.add_resource(getValuesById,'/types/<string:category>/<string:filterType>/<string:order>/<string:time>/<int:page>/<string:key>/<string:search>','/types/<string:category>/<string:filterType>/<string:order>/<string:time>/<int:page>/<string:key>')
api.add_resource(handleComment,'/comment')
api.add_resource(userTemplate,'/usertemplate')
api.add_resource(editFeed,'/edit/<int:feedId>')
api.add_resource(incrementLikes,'/incrementLikes/<int:userId>/<int:feedId>')
api.add_resource(incrementDislikes,'/incrementDislikes/<int:userId>/<int:feedId>')
api.add_resource(addUrl,'/addUrl')
api.add_resource(deleteUserById,'/users/delete/<int:userId>')
api.add_resource(deleteFeedById,'/users/deletefeed/<int:feedId>/<int:userId>')
api.add_resource(user,'/user/<int:userId>')
api.add_resource(role,'/role')
api.add_resource(access,'/access')

db.create_all()
#Admin Panel
admin.add_view(RolesController(Roles, db.session,category="Roles"))
admin.add_view(UsersController(Users, db.session))
admin.add_view(Controller(SpecialRights, db.session,category="Roles"))
admin.add_view(FeedXmlsController(FeedXmls, db.session,category="Feeds"))
admin.add_view(FeedsController(Feeds, db.session,category="Feeds"))
admin.add_view(CommentController(Comments, db.session,category="Feeds"))
admin.add_view(UserLikeController(UserLike, db.session,category="Feeds"))
admin.add_link(MenuLink(name='Logout',url="/logout"))


if __name__=='__main__':
    app.run(debug=True)

