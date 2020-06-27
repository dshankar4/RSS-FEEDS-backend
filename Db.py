from flask import flash,Flask
from flask_sqlalchemy import SQLAlchemy
from __main__ import app,login_manager,bcrypt
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
from models import Feeds,FeedXmls,Roles,Users,Comments,UserLike,SpecialRights
db.create_all()

# handleDb to Handle initial Db operations
def handleDb():
    if not Roles.query.all():
        db.session.add(Roles('admin'))
        db.session.commit()
        db.session.add(Roles('user'))
        db.session.commit()
    if not Users.query.all():
        db.session.add(Users('admin','admin','admin@admin.in',bcrypt.generate_password_hash('admin').decode('utf-8'),1))
        db.session.commit()
        db.session.add(Users('user','user','user@user.in',bcrypt.generate_password_hash('user').decode('utf-8'),2))
        db.session.commit()
    if not SpecialRights.query.all():
        db.session.add(SpecialRights(1,True,True,True,True,True,True,True,True,True,True))
        db.session.commit()
    if not FeedXmls.query.all():
        db.session.add(FeedXmls('https://www.hindustantimes.com/rss/topnews/rssfeed.xml','Headline'))
        db.session.add(FeedXmls('https://www.hindustantimes.com/rss/india/rssfeed.xml','India'))
        db.session.add(FeedXmls('https://www.hindustantimes.com/rss/tech/rssfeed.xml','Tech'))
        db.session.add(FeedXmls('https://www.hindustantimes.com/rss/education/rssfeed.xml','Education'))
        db.session.add(FeedXmls('https://www.hindustantimes.com/rss/business/rssfeed.xml','Business'))
        db.session.commit()


#Register user    
def registerUser(first_name,last_name,email,password,roles):
    exist=Roles.query.filter_by(role=roles).first()    
    if exist:
        db.session.add(Users(first_name,last_name,email,password,exist.adminId))
        db.session.commit()

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
            db.session.commit()
            if userInput==1:
                return 1
    
    if userInput==1 and flag==0:
        return 0
    
    feeds_exist=Feeds.query.all()
    records=[]
    for rows in feeds_exist:
        records.append((rows.feedId,rows.feedTitle,rows.summary,rows.time,rows.imageUrl,rows.category,rows.author,rows.link,rows.likes,rows.dislikes,rows.dispTime,rows.logo,rows.userId))
    return records
    
#Select email to check if there is no matching email   
def selectEmail(email):
    user=Users.query.filter_by(email=email).first()
    if user:
        return [user.adminId,user.userId,user.firstname,user.lastname,user.email,user.password]
    else:
        return None

#Add comment for userId in feedid
def addComment(feedId,userId,comment):
    db.session.add(Comments(userId,feedId,comment))
    db.session.commit()
    return {'message':'comment posted','format':'True'}

#Add feedUrl and category
def feedUrlAdd(url,newCategory):
    record=FeedXmls.query.filter_by(feedxml=url,category=newCategory).first()    
    if record:
        conn.commit()
        conn.close()
        return {'message':'Bad Request','Format': 'False'}
    db.session.add(FeedXmls(url,newCategory))
    db.session.commit()
    return {'message':'url added','Format': 'True'}


#Get comments for the feedId
def getComment(feedId):
    comments=Comments.query.filter_by(feedId=feedId)
    returnDict={}
    returnDict['Format']='True'
    returnDict['values']=list()
    for rows in comments:
        returnDict['values'].append({'userId':rows.userId,'comment':rows.comment})
    if len(returnDict['values'])==0:
        return {'message':'invalid commentId','Format': 'False'}
    return returnDict

#Edit feed
def feedEdit(title,summary,category,author,link,feedId):
    rows=Feeds.query.filter_by(feedId=feedId).first()
    rows.feedTitle=title
    rows.summary=summary
    rows.category=category
    rows.author=author
    rows.link=link
    db.session.commit()
    return [rows.feedId,rows.feedTitle,rows.summary,rows.time,rows.imageUrl,rows.category,rows.author,rows.link,rows.likes,rows.dislikes,rows.dispTime,rows.logo,rows.userId]

#likes
def addLikes(userId,feedId):
    records=UserLike.query.filter_by(feedId=feedId,userId=userId).first()
    if records:
        if bool(records.like) == False and bool(records.dislike) == True:
            records.like=True
            records.dislike=False
            db.session.commit()
            record=Feeds.query.filter_by(feedId=feedId).first()
            record.likes+=1
            record.dislikes-=1
            db.session.commit()
        else:
            return False
    else:
        db.session.add(UserLike(userId,feedId,1,0))
        record=Feeds.query.filter_by(feedId=feedId).first()
        record.likes+=1
        db.session.commit()
    
    return True
        
#dislikes
def addDislikes(userId,feedId):
    records=UserLike.query.filter_by(feedId=feedId,userId=userId).first()    
    if records:
        if bool(records.like) == True and bool(records.dislike) == False:
                records.like=False
                records.dislike=True
                db.session.commit()
                record=Feeds.query.filter_by(feedId=feedId).first()
                record.likes-=1
                record.dislikes+=1
                db.session.commit()
        else:
            return False
    else:
        db.session.add(UserLike(userId,feedId,0,1))
        record=Feeds.query.filter_by(feedId=feedId).first()
        record.dislikes+=1
        db.session.commit()
    
    return True

#check feed Id    
def checkFeedId(feedId):
    userId=Feeds.query.filter_by(feedId=feedId).first()
    if userId:
        return 1
    else:
        return 0

#check user Id
def checkUserId(userId):
    userId=Users.query.filter_by(userId=userId).first()
    if userId:
        return 1
    else:
        return 0


# New Role appending in Database
def newRole(role):
    newRole=Roles.query.filter_by(role=role).first()
    if newRole:
        return {'Format':'False','message':'Role already exist'}, 401
    db.session.add(Roles(role))
    db.session.commit()
    return {'message':'role added','Format':'True'}, 200

#To display all roles
def getRole():
    roles=Roles.query.all()
    rolesDict={}
    record=[]
    for rows in roles:
        record.append((rows.adminId,rows.role))
    if record:
        rolesDict['Values']=list()
        for rows in record:
            rolesDict['Values'].append({'adminId':rows[0],'Role':rows[1]})
        return {'roles':rolesDict,'format':'True'}, 200
    else:
        return {'message':'role doesnt exist','Format':'False'}, 401

#To delete a role
def deleteRole(adminId):
    newRole=Roles.query.filter_by(adminId=adminId).first()
    if newRole:
        db.session.delete(newRole)
        db.session.commit()
        return {'Format':'True'}, 200
    else:
        return {'Format':'False'}, 401

#get Access
def getAccess(userId):
    rights=SpecialRights.query.all()
    record=[]
    for rows in rights:
        record.append((rows.colId,rows.userId,rows.cFeed,rows.rFeed,rows.uFeed,rows.dFeed,rows.rolesTable,rows.usersTable,rows.feedsTable,rows.userLikeTable,rows.commentTable,rows.feedXmlsTable))    
    rolesDict={}
    if record:
        rolesDict['Values']=list()
        for rows in record:
            rolesDict['Values'].append({'userId':rows[1],'cFeed':rows[2],'rFeed':rows[3],'uFeed':rows[4],'dFeed':rows[5],'rowsTable':rows[6],'usersTable':rows[7],'feedsTable':rows[8],'userLikeTable':rows[9],'commentTable':rows[10],'feedXmlsTable':rows[11]})
        return {'access':rolesDict,'format':'True'}, 200
    else:
        return {'message':'no access right','Format':'False'}, 401

#update access
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

#delete access
def deleteAccess(id):
    specialRights=SpecialRights.query.filter_by(colId=id).first()
    if specialRights:
        db.session.delete(specialRights)
        db.session.commit()
        return {"message":"access deleted"}
    else:
        return {"message":"incorrect access"}

#delete feed
def deleteFeed(feedId,userId):
    feed=Feeds.query.filter_by(feedId=feedId,userId=userId).first()
    if feed:
        db.session.delete(feed)
        db.session.commit()
        return {"message":"feed deleted"}
    else:
        return {"message":"Bad Request"}

#delete user   
def deleteUser(userId):
    user=Users.query.filter_by(userId=userId).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return {"message":"user deleted"}
    else:
        return {"message":"Bad Request"}

# Get rights    
def getSpecialRights(userId):
    rights=SpecialRights.query.filter_by(userId=userId)    
    records=[]
    for rows in rights:
        records.append((rows.colId,rows.userId,rows.cFeed,rows.rFeed,rows.uFeed,rows.dFeed,rows.rolesTable,rows.usersTable,rows.feedsTable,rows.userLikeTable,rows.commentTable,rows.feedXmlsTable))
    return records 

#delete comment
def commentDelete(commentId):
    comment=Comments.query.filter_by(commentId=commentId).first()
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return {"message":"comment deleted",'format':'True'}
    else:
        return {"message":"comment doesn't exist",'format':'False'}

#get User
def getUser(userId):
    feeds=Feeds.query.filter_by(userId=userId).first()    
    if feeds:
        records=[]
        for rows in feeds:         
            records.append({'feedId':rows.feedId,'feedTitle':rows.feedTitle,'summary':rows.summary,'dispTime':rows.dispTime,'imgUrl':rows.imageUrl,'category':rows.category,'author':rows.author,'link':rows.link,'like':rows.likes,'dislike':rows.dislikes,'time':rows.time,'logo':rows.logo,'userId':rows.userId})
        conn.commit()
        conn.close()
        return {'feeds':records,'format':'True'}
    else:
        return {"message":"no feeds",'format':'False'}

#get post
def getPost(feedId):
    feeds=Feeds.query.filter_by(feedId=feedId).first()
    if feeds:
        return [{'feedId':feeds.feedId,'feedTitle':feeds.feedTitle,'summary':feeds.summary,'dispTime':feeds.dispTime,'imgUrl':feeds.imageUrl,'category':feeds.category,'author':feeds.author,'link':feeds.link,'like':feeds.likes,'dislike':feeds.dislikes,'time':feeds.time,'logo':feeds.logo,'userId':feeds.userId}]
    else:
        return {"message":"no feeds",'format':'False'}








