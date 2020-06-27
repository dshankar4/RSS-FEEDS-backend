from Db import db
from flask_login import UserMixin
from flask_admin import Admin, AdminIndexView
class MyAdminIndexView(AdminIndexView):
    def is_visible(self):
        return False
    def is_accessible(self):
        return current_user.is_authenticated

# Feeds class stores the details and appends day to day informations and feeds.
class feeds:
    def __init__(self,feedTitle,summary,time,imageUrl,category,author,link,dispTime,logo,userId):
        self.feedTitle=feedTitle
        self.summary=summary
        self.time=time
        self.imageUrl=imageUrl
        self.category=category
        self.author=author
        self.link=link
        self.dispTime=dispTime
        self.logo=logo
        self.userId=userId

class FeedXmls(db.Model):
    __tablename__="feedXmls"
    feedXmlId=db.Column('feedXmlId',db.Integer,primary_key=True)
    feedXml=db.Column('feedXml',db.String)
    category=category=db.Column('category',db.String)
    
    def __init__(self,feedXml,category):
        self.feedXml=feedXml
        self.category=category
        
class Roles(db.Model):
    __tablename__="roles"
    adminId= db.Column('adminId',db.Integer,primary_key=True)
    role=db.Column('role',db.String,unique=True, nullable=False)
    
    def __init__(self,role):
        self.role=role

    
class Users(db.Model,UserMixin):
    __tablename__="users"
    userId=db.Column('userId',db.Integer,primary_key=True)
    adminId=db.Column('adminId',db.Integer,db.ForeignKey('roles.adminId'))
    roles = db.relationship("Roles", backref='adminId_roles')
    firstname=db.Column('firstname',db.String)
    lastname=db.Column('lastname',db.String)
    email=db.Column('email',db.String,unique=True)
    password=db.Column('password',db.String)
    
    def __init__(self,first_name,last_name,email,password,adminId):
        self.adminId=adminId
        self.firstname=first_name
        self.lastname=last_name
        self.email=email
        self.password=password
        
    def get_id(self):
        return (self.userId)
    
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
    likes=db.Column('likes',db.Integer)
    dislikes=db.Column('dislikes',db.Integer)
    dispTime=db.Column('dispTime',db.String)
    logo=db.Column('logo',db.String)

    def __init__(self,userId,feedTitle,summary,time,imageUrl,category,author,link,likes,dislikes,dispTime,logo):
        self.userId=userId
        self.feedTitle=feedTitle
        self.summary=summary
        self.time=time
        self.imageUrl=imageUrl
        self.category=category
        self.author=author
        self.link=link
        self.likes=likes
        self.dislikes=dislikes
        self.dispTime=dispTime
        self.logo=logo

class Comments(db.Model):
    __tablename__="comments"
    commentId=db.Column('commentId',db.Integer,primary_key=True)
    userId=db.Column('userId',db.Integer,db.ForeignKey('users.userId'))
    users = db.relationship("Users", backref='userId_comments')
    feedId=db.Column('feedId',db.Integer,db.ForeignKey('feeds.feedId'))
    feeds = db.relationship("Feeds", backref='feedId_comments')
    comment=db.Column('comment',db.String)

    def __init__(self,userId,feedId,comment):
        self.userId=userId
        self.feedId=feedId
        self.comment=comment

class UserLike(db.Model):
    __tablename__="userLike"
    userId=db.Column('userId',db.Integer,db.ForeignKey('users.userId'))
    users = db.relationship("Users", backref='userId_userlike')
    feedId=db.Column('feedId',db.Integer,db.ForeignKey('feeds.feedId'))
    feeds = db.relationship("Feeds", backref='feedId_userlike')
    like=db.Column('like',db.Boolean)
    dislike=db.Column('dislike',db.Boolean)
    likeId=db.Column('likeId',db.Integer,primary_key=True)
    
    def __init__(self,userId,feedId,like,dislike):
        self.userId=userId
        self.feedId=feedId
        self.like=like
        self.dislike=dislike
        
        
class SpecialRights(db.Model):
    __tablename__="specialRights"
    colId= db.Column('colId',db.Integer,primary_key=True)
    userId=db.Column('userId',db.Integer,db.ForeignKey('users.userId'))
    users = db.relationship("Users", backref='userId_specialRights')
    cFeed= db.Column('cFeed',db.Boolean)
    rFeed= db.Column('rFeed',db.Boolean)
    uFeed= db.Column('uFeed',db.Boolean)
    dFeed= db.Column('dFeed',db.Boolean)
    rolesTable=db.Column('rolesTable',db.Boolean)
    usersTable=db.Column('usersTable',db.Boolean)
    feedsTable=db.Column('feedsTable',db.Boolean)
    userLikeTable=db.Column('userLikeTable',db.Boolean)
    commentTable=db.Column('commentTable',db.Boolean)
    feedXmlsTable=db.Column('feedXmlsTable',db.Boolean)

    def __init__(self,userId,cFeed,rFeed,uFeed,dFeed,rolesTable,usersTable,feedsTable,userLikeTable,commentTable,feedXmlsTable):
        self.userId=userId
        self.cFeed=cFeed
        self.rFeed=rFeed
        self.uFeed=uFeed
        self.dFeed=dFeed
        self.rolesTable=rolesTable
        self.usersTable=usersTable
        self.feedsTable=feedsTable
        self.userLikeTable=userLikeTable
        self.commentTable=commentTable
        self.feedXmlsTable=feedXmlsTable
        
