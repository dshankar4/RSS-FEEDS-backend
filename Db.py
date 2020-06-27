from flask import flash,Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from __main__ import app,login_manager,admin
from sqlalchemy import event
from flask_admin import Admin, AdminIndexView
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user,login_required
import sqlite3

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///feeds.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db= SQLAlchemy(app)

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
    
    def __init__(first_name,last_name,email,password,adminId):
        self.adminId=exist
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
    feedTitle=db.Column('feedTitle',db.String,unique=True)
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
        
db.create_all()

# handleDb to Handle initial Db operations
def handleDb():
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    # Create roles table
    c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='roles' """)
    if c.fetchone()[0]!=1 : 
        c.execute("""CREATE TABLE roles (adminId INTEGER PRIMARY KEY,
                                        role TEXT)""")
        conn.commit()
        c.execute("INSERT INTO roles VALUES (:adminId,:role)",{'adminId':1,'role':'admin'})
        c.execute("INSERT INTO roles VALUES (:adminId,:role)",{'adminId':2,'role':'user'})
        conn.commit()
        
    # Create users table
    c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users' """)
    if c.fetchone()[0]!=1 : 
        c.execute("""CREATE TABLE users (userId INTEGER PRIMARY KEY AUTOINCREMENT,
                                        adminId INTEGER,
                                        firstname TEXT,
                                        lastname TEXT,
                                        email TEXT,
                                        password TEXT,
                                        FOREIGN KEY(adminId) REFERENCES roles(adminId))""")  
        conn.commit()
        bcrypt = Bcrypt()
        c.execute("INSERT INTO users (adminId,firstname,lastname,email,password) VALUES (:adminId,:firstname,:lastname,:email,:password)",{'adminId':1,'firstname':'admin','lastname':'admin','email':'admin@admin.in','password':bcrypt.generate_password_hash('admin').decode('utf-8')})
        c.execute("INSERT INTO users (adminId,firstname,lastname,email,password) VALUES (:adminId,:firstname,:lastname,:email,:password)",{'adminId':2,'firstname':'user','lastname':'user','email':'user@user.in','password':bcrypt.generate_password_hash('user').decode('utf-8')})
        conn.commit()
        
    # Create specialRights table
    c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='specialRights' """)
    if c.fetchone()[0]!=1 : 
        c.execute("""CREATE TABLE specialRights (colId INTEGER PRIMARY KEY AUTOINCREMENT,
                                        userId INTEGER,
                                        cFeed INTEGER,
                                        rFeed INTEGER,
                                        uFeed INTEGER,
                                        dFeed INTEGER,
                                        rolesTable INTEGER,
                                        usersTable INTEGER,
                                        feedsTable INTEGER,
                                        userLikeTable INTEGER,
                                        commentTable INTEGER,
                                        feedXmlsTable INTEGER,
                                        FOREIGN KEY(userId) REFERENCES users(userId))""")
        conn.commit()
        c.execute("INSERT INTO specialRights(userId,cFeed,rFeed,uFeed,dFeed,rolesTable,usersTable,feedsTable,userLikeTable,commentTable,feedXmlsTable) VALUES (:userId,:cFeed,:rFeed,:uFeed,:dFeed,:rolesTable,:usersTable,:feedsTable,:userLikeTable,:commentTable,:feedXmlsTable)",{'userId':1,'cFeed':1,'rFeed':1,'uFeed':1,'dFeed':1,'rolesTable':1,'usersTable':1,'feedsTable':1,'userLikeTable':1,'commentTable':1,'feedXmlsTable':1})

    # Create feeds table 
    c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='feeds' """)
    if c.fetchone()[0]!=1 : 
        c.execute("""CREATE TABLE feeds (feedId INTEGER PRIMARY KEY AUTOINCREMENT,
                                        feedTitle TEXT,
                                        summary TEXT,
                                        time TEXT,
                                        imageUrl TEXT,
                                        category TEXT,
                                        author TEXT,
                                        link TEXT,
                                        likes INTEGER,
                                        dislikes INTEGER,
                                        dispTime TEXT,
                                        logo TEXT,
                                        userId INTEGER,
                                        FOREIGN KEY(userId) REFERENCES users(userId))""")
        conn.commit()
    # Create userLike table
    c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='userLike' """)
    if c.fetchone()[0]!=1 : 
        c.execute("""CREATE TABLE userLike (userId TEXT,
                                            feedId INTEGER,
                                            like INTEGER,
                                            dislike INTEGER,
                                            likeId INTEGER PRIMARY KEY AUTOINCREMENT,
                                            FOREIGN KEY(userId) REFERENCES users(userId),
                                            FOREIGN KEY(FeedId) REFERENCES feeds(feedId))""")
        conn.commit()
    # Create comments table
    c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='comments' """)
    if c.fetchone()[0]!=1 : 
        c.execute("""CREATE TABLE comments (userId TEXT,
                                            feedId INTEGER,
                                            comment TEXT,
                                            commentId INTEGER PRIMARY KEY AUTOINCREMENT,
                                            FOREIGN KEY(userId) REFERENCES users(userId),
                                            FOREIGN KEY(FeedId) REFERENCES feeds(feedId))""")
        conn.commit()

    # Create feedXmlS table 
    c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='feedXmls' """)
    if c.fetchone()[0]!=1 :
        c.execute("""CREATE TABLE feedXmls (feedXmlId INTEGER PRIMARY KEY AUTOINCREMENT,
                                            feedXml TEXT,
                                            category TEXT)""")
        conn.commit()
        c.execute("INSERT INTO feedXmls (feedXml,category) VALUES (:feedXml,:category)",{'feedXml':'https://www.hindustantimes.com/rss/topnews/rssfeed.xml','category':'Headline'})
        c.execute("INSERT INTO feedxmls (feedXml,category) VALUES (:feedXml,:category)",{'feedXml':'https://www.hindustantimes.com/rss/india/rssfeed.xml','category':'India'})
        c.execute("INSERT INTO feedxmls (feedXml,category) VALUES (:feedXml,:category)",{'feedXml':'https://www.hindustantimes.com/rss/sports/rssfeed.xml','category':'Sports'})
        c.execute("INSERT INTO feedxmls (feedXml,category) VALUES (:feedXml,:category)",{'feedXml':'https://www.hindustantimes.com/rss/tech/rssfeed.xml','category':'Tech'})
        c.execute("INSERT INTO feedxmls (feedXml,category) VALUES (:feedXml,:category)",{'feedXml':'https://www.hindustantimes.com/rss/education/rssfeed.xml','category':'Education'})
        c.execute("INSERT INTO feedxmls (feedXml,category) VALUES (:feedXml,:category)",{'feedXml':'https://www.hindustantimes.com/rss/business/rssfeed.xml','category':'Business'})
        c.execute("INSERT INTO feedxmls (feedXml,category) VALUES (:feedXml,:category)",{'feedXml':'https://www.hindustantimes.com/rss/lifestyle/rssfeed.xml','category':'Lifestyle'})
        conn.commit()
    conn.close()
    

#Register user    
def registerUser(first_name,last_name,email,password,roles):
    exist=Roles.query.filter_by(role=roles).first()    
    if exist:
        db.session.add(Users(first_name,last_name,email,password,exist.adminId))
    

#getXml function fetches all the RSS feeds from the database.
def getXml():
    feeds_exist=FeedXmls.query.all()
    records=[]
    for rows in feeds_exist:
        records.append((rows.feedXmlId,rows.feedXml,rows.category))
    return records


#Updates the database with new feeds.Handles multiple copies in the database if any
def getFeeds(allFeeds,userInput=0):
    for feeds in allFeeds:
        exist=Feeds.query.filter_by(feedTitle=feeds.feedTitle).first()    
        flag=1
        if exist:
            exist=Feeds.query.filter_by(feedTitle=feeds.feedTitle,category=feeds.category).first()    
            if exist:
                flag=0
        
        if(flag==1):
            exist=Users.query.filter_by(userId=feeds.userId).first()    
            if not exist:    
                return 0
            db.session.add(Feeds(feeds.userId,feeds.feedTitle,feeds.summary,feeds.time,feeds.imageUrl,feeds.category,feeds.author,feeds.link,0,0,feeds.dispTime,feeds.logo))
            if userInput==1:
                return 1
    
    if userInput==1 and flag==0:
        return 0
    
    feeds_exist=FeedXmls.query.all()
    records=[]
    for rows in feeds_exist:
        records.append((rows.feedXmlId,rows.feedXml,rows.category))
    return records
    
#rp
#Select email to check if there is no matching email   
def selectEmail(email):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("SELECT * FROM users where email = ?",(email,))
    records = c.fetchone()
    conn.commit()
    conn.close()
    return records

#Shankar    
#Add comment for userId in feedid
def addComment(feedId,userId,comment):
    db.session.add(Comments(userId,feedId,comment))
    db.session.commit()
    return {'message':'comment posted','format':'True'}

#rp
#Get comments for the feedId
def getComment(feedId):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("SELECT * FROM comments WHERE feedId=?",(feedId,))
    comments=c.fetchall()
    conn.commit()
    conn.close()
    returnDict={}
    returnDict['Format']='True'
    returnDict['values']=list()
    for rows in comments:
        returnDict['values'].append({'userId':rows[0],'comment':rows[2]})
    if len(returnDict['values'])==0:
        return {'message':'invalid commentId','Format': 'False'}
    return returnDict

#shankar
#Add feedUrl and category
def feedUrlAdd(url,newCategory):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    record=FeedXmls.query.filter_by(feedxml=url,category=newCategory).first()    
    if record:
        conn.commit()
        conn.close()
        return {'message':'Bad Request','Format': 'False'}
    db.session.add(FeedXmls(url,newCategory))
    db.session.commit()
    return {'message':'url added','Format': 'True'}

#rp
def feedEdit(title,summary,category,author,link,feedId):
    conn = sqlite3.connect('Feeds.db')
    c = conn.cursor()
    c.execute("UPDATE feeds SET feedTitle = (:title), summary = (:summary), category = (:category), author = (:author), link = (:link) WHERE feedId = (:id)",{'title':title,'summary':summary,'category':category,'author':author,'link':link,'id':feedId})
    feed=c.fetchone()
    conn.commit()
    conn.close()
    return feed

#rp
def addLikes(userId,feedId):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("SELECT * FROM userLike where feedId = ? and userId=?",(feedId,userId))
    records = c.fetchone()
    if records:
        if records[2] == 0:
            c.execute("update userLike set like=(:like),dislike=(:dislike) where userId=(:userId) and feedId=(:feedId)",{'like':"1",'dislike':"0",'userId':userId,'feedId':feedId})
            c.execute("update feeds set likes=likes+1,dislikes=dislike-1 where feedId=(:feedId)",{'feedId':feedId})
        else:
            return {"message":"liked before itself"}
    else:
        c.execute("INSERT INTO userLike (userId,feedId,like,dislike) VALUES (:userId,:feedId,:like,:dislike)",{'userId':userId,'feedId':feedId,'like':"1","dislike":"0"})
        c.execute("update feeds set likes=likes+1 where feedId=(:feedId)",{'feedId':feedId})
    conn.commit()
    conn.close()
    return records
        
#rp
def addDislikes(userId,feedId):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("SELECT * FROM userLike where feedId = ? and userId=?",(feedId,userId))
    records = c.fetchone()
    if records:
        if records[3] == 0:
            c.execute("update userLike set like=(:like),dislike=(:dislike) where userId=(:userId) and feedId=(:feedId)",{'like':"0",'dislike':"1",'userId':userId,'feedId':feedId})
            c.execute("update feeds set likes=likes-1,dislikes=dislikes+1 where feedId=(:feedId)",{'feedId':feedId})
        else:
            return {"message":"disliked before itself"}
    else:
        c.execute("INSERT INTO userLike (userId,feedId,like,dislike) VALUES (:userId,:feedId,:like,:dislike)",{'userId':userId,'feedId':feedId,'like':"0","dislike":"1"})
        c.execute("update feeds set dislikes=dislikes+1 where feedId=(:feedId)",{'feedId':feedId})
    conn.commit()
    conn.close()
    return records

#shankar    
def checkFeedId(feedId):
    userId=Feeds.query.filter_by(feedId=feedId).first()
    if userId:
        return 1
    else:
        return 0

#shankar
def checkUserId(userId):
    userId=Users.query.filter_by(userId=userId).first()
    if userId:
        return 1
    else:
        return 0

#shankar
# New Role appending in Database
def newRole(role):
    newRole=Roles.query.filter_by(role=role).first()
    if newRole:
        return {'Format':'False','message':'Role already exist'}, 401
    db.session.add(Roles(role))
    db.session.commit()
    return {'message':'role added','Format':'True'}, 200

#rp
#To display all roles
def getRole():
    conn = sqlite3.connect('Feeds.db')
    c = conn.cursor()
    c.execute("SELECT * FROM roles")
    record = c.fetchall()
    conn.commit()
    conn.close()
    rolesDict={}
    if record:
        rolesDict['Values']=list()
        for rows in record:
            rolesDict['Values'].append({'adminId':rows[0],'Role':rows[1]})
        return {'roles':rolesDict,'format':'True'}, 200
    else:
        return {'message':'role doesnt exist','Format':'False'}, 401

#shankar
#To delete a role
def deleteRole(adminId):
    newRole=Roles.query.filter_by(adminId=adminId).first()
    if newRole:
        db.session.delete(newRole)
        db.session.commit()
        return {'Format':'True'}, 200
    else:
        return {'Format':'False'}, 401

#rp
def getAccess(userId):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("SELECT * FROM specialRights")
    record = c.fetchall()
    conn.commit()
    conn.close()
    rolesDict={}
    if record:
        rolesDict['Values']=list()
        for rows in record:
            rolesDict['Values'].append({'userId':rows[1],'cFeed':rows[2],'rFeed':rows[3],'uFeed':rows[4],'dFeed':rows[5],'rowsTable':rows[6],'usersTable':rows[7],'feedsTable':rows[8],'userLikeTable':rows[9],'commentTable':rows[10],'feedXmlsTable':rows[11]})
        return {'access':rolesDict,'format':'True'}, 200
    else:
        return {'message':'no access right','Format':'False'}, 401

#shankar
def updateAccess(userId,colId,cFeed,rFeed,uFeed,dFeed,rolesTable,usersTable,feedsTable,userLikeTable,commentTable,feedXmlsTable):
    specialRights=SpecialRights.query.filter_by(colId=colId).first()
    if specialRights:
        specialRights.userId=userId
        specialRights.cFeed=cFeed
        specialRights.rFeed=rFeed
        specialRights.uFeed=uFeed
        specialRights.dFeed=dFeed
        specialRights.rolesTable=rolesTable
        specialRights.usersTable=usersTable
        specialRights.feedsTable=feedsTable
        specialRights.userLikeTable=userLikeTable
        specialRights.commentTable=commentTable
        specialRights.feedXmlsTable=feedXmlsTable
        db.session.commit()
        return {"message":"updated",'format':'True'}
    else:
        db.session.add(SpecialRights(userId,cFeed,rFeed,uFeed,dFeed,rolesTable,usersTable,feedsTable,userLikeTable,commentTable,feedXmlsTable))
        db.session.commit()
        return {"message":"new role",'fomrat':'True'}

#shankar
def deleteAccess(id):
    specialRights=SpecialRights.query.filter_by(colId=id).first()
    if specialRights:
        db.session.delete(specialRights)
        db.session.commit()
        return {"message":"access deleted"}
    else:
        return {"message":"incorrect access"}

#shankar
def deleteFeed(feedId,userId):
    feed=Feeds.query.filter_by(feedId=feedId,userId=userId).first()
    if feed:
        db.session.delete(feed)
        db.session.commit()
        return {"message":"feed deleted"}
    else:
        return {"message":"Bad Request"}

#shankar   
def deleteUser(userId):
    user=Users.query.filter_by(userId=userId).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return {"message":"user deleted"}
    else:
        return {"message":"Bad Request"}

#rp
def getSpecialRights(userId):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("SELECT * FROM specialRights WHERE userId=?",(userId,))
    records=c.fetchall()
    conn.commit()
    conn.close()
    return records

#shankar
def commentDelete(commentId):
    comment=Comments.query.filter_by(commentId=commentId).first()
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return {"message":"comment deleted",'format':'True'}
    else:
        return {"message":"comment doesn't exist",'format':'False'}

#rp
def getUser(userId):
    conn = sqlite3.connect('Feeds.db')
    c = conn.cursor()
    c.execute("SELECT * FROM feeds where userId = (:userId)",{'userId':userId})
    record = c.fetchall()
    if record:
        records=[]
        for feed in record:
            records.append({'id':feed[0],'feedTitle':feed[1],'summary':feed[2],'dispTime':feed[3],'imgUrl':feed[4],'category':feed[5],'author':feed[6],'link':feed[7],'like':feed[8],'dislike':feed[9],'time':feed[10],'logo':feed[11],'userId':feed[12]})
        conn.commit()
        conn.close()
        return {'feeds':records,'format':'True'}
    else:
        return {"message":"no feeds",'format':'False'}









