import sqlite3
from flask import flash
from flask_bcrypt import Bcrypt

# handleDb to Handle initial Db operations
def handleDb():
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    # Create roles table
    c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='roles' """)
    if c.fetchone()[0]!=1 : 
        c.execute("""CREATE TABLE roles (adminId INTEGER PRIMARY KEY,
                                        role TEXT,
                                        cFeed INTEGER,
                                        rFeed INTEGER,
                                        uFeed INTEGER,
                                        dFeed INTEGER)""")
        conn.commit()
        c.execute("INSERT INTO roles VALUES (:adminId,:role,:cFeed,:rFeed,:uFeed,:dFeed)",{'adminId':0,'role':'admin','cFeed':1,'rFeed':1,'uFeed':1,'dFeed':1})
        c.execute("INSERT INTO roles VALUES (:adminId,:role,:cFeed,:rFeed,:uFeed,:dFeed)",{'adminId':1,'role':'user','cFeed':1,'rFeed':1,'uFeed':0,'dFeed':0})

    # Create users table
    c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users' """)
    if c.fetchone()[0]!=1 : 
        c.execute("""CREATE TABLE users (userId INTEGER PRIMARY KEY AUTOINCREMENT,
                                        adminId INTEGER,
                                        firstname TEXT,
                                        lastname TEXT,
                                        email TEXT,
                                        password TEXT,
                                        cFeed INTEGER,
                                        rFeed INTEGER,
                                        uFeed INTEGER,
                                        dFeed INTEGER,
                                        FOREIGN KEY(adminId) REFERENCES roles(adminId))""")  
        conn.commit()
        bcrypt = Bcrypt()
        c.execute("INSERT INTO users (adminId,firstname,lastname,email,password,cFeed,rFeed,uFeed,dFeed) VALUES (:adminId,:firstname,:lastname,:email,:password,:cFeed,:rFeed,:uFeed,:dFeed)",{'adminId':0,'firstname':'admin','lastname':'admin','email':'admin@admin.in','password':bcrypt.generate_password_hash('admin').decode('utf-8'),'cFeed':1,'rFeed':1,'uFeed':1,'dFeed':1})
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
def registerUser(first_name,last_name,email,password,role):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("SELECT * FROM roles where role=?",(role,))
    role = c.fetchone()
    c.execute("INSERT INTO users (adminId,firstname,lastname,email,password,cFeed,rFeed,uFeed,dFeed) VALUES (:adminId,:firstname,:lastname,:email,:password,:c,:r,:u,:d)",{'adminId':role[0],'firstname':first_name,'lastname':last_name,'email':email,'password':password,'c':role[2],'r':role[3],'u':role[4],'d':role[5]})
    conn.commit()
    conn.close()
    
#getXml function fetches all the RSS feeds from the database.
def getXml():
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("SELECT * FROM feedXmls")
    records = c.fetchall()
    conn.commit()
    conn.close()
    return records

#Updates the database with new feeds.Handles multiple copies in the database if any
def getFeeds(allFeeds,userInput=0):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    for feeds in allFeeds:
        c.execute("SELECT * FROM feeds WHERE feedTitle = ?",(feeds.feedTitle,))
        result=c.fetchone()
        flag=1
        if(result!=None):
            c.execute("SELECT * FROM feeds WHERE feedTitle = ? AND category = ?",(feeds.feedTitle,feeds.category))
            result=c.fetchone()
            if(result!=None):
                flag=0
        if(flag==1):
            result=c.execute("SELECT * FROM users WHERE userId = ?",(feeds.userId,))
            if(result==None):
                conn.commit()
                conn.close()    
                return 0
            c.execute("INSERT INTO feeds(feedTitle,summary,time,imageUrl,category,author,link,likes,dislikes,dispTime,logo,userId) VALUES (:feedTitle,:summary,:time,:imageUrl,:category,:author,:link,:likes,:dislikes,:dispTime,:logo,:userId)",{'feedTitle':feeds.feedTitle,'summary':feeds.summary,'time':feeds.time,'imageUrl':feeds.imageUrl,'category':feeds.category,'author':feeds.author,'link':feeds.link,'likes':0,'dislikes':0,'dispTime':feeds.dispTime,'logo':feeds.logo,'userId':feeds.userId})
            if userInput==1:
                conn.commit()
                conn.close()
                return 1
    c.execute("SELECT * FROM feeds")
    records = c.fetchall()
    conn.commit()
    conn.close()
    if userInput==1 and flag==0:
        return 0
    return records
    
#Select email to check if there is no matching email   
def selectEmail(email):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("SELECT * FROM users where email = ?",(email,))
    records = c.fetchone()
    conn.commit()
    conn.close()
    return records
    
#Add comment for userId in feedid
def addComment(feedId,userId,comment):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("INSERT INTO comments (userId,feedId,comment) VALUES (:userId,:feedId,:comment)",{'userId':userId,'feedId':feedId,'comment':comment})
    conn.commit()
    conn.close()
    return {'post': 'posted'}

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
        return {'Format': 'False'}
    return returnDict

#Add feedUrl and category
def feedUrlAdd(url,newCategory):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    record=c.execute("SELECT feedXml,category FROM feedXmls WHERE feedXml=(:url) and category=(:category)",{'url':url,'category':newCategory})
    if record:
        conn.commit()
        conn.close()
        return {'Format': 'False'}
    c.execute("INSERT INTO feedXmls (feedXml,category) VALUES (:url,:category)",{'url':url,'category':newCategory})
    records = c.fetchone()
    conn.commit()
    conn.close()
    return {'Format': 'True'}

# New Role appending in Database
def newRole(role,create,read,update,delete):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("SELECT * FROM roles where role=? and cFeed=? and rFeed=? and uFeed=? and dFeed=?",(role,create,read,update,delete))
    records = c.fetchone()
    if records:
        conn.commit()
        conn.close()
        return {'Format':'False','message':'Role already exist'}, 401
    c.execute("INSERT INTO roles (role,cFeed,rFeed,uFeed,dFeed) VALUES (:role,:create,:read,:update,:delete)",{'role':role,'create':create,'read':read,'update':update,'delete':delete})
    conn.commit()
    conn.close()
    return {'Format':'True'}, 200

def feedEdit(title,summary,category,author,link,feedId):
    conn = sqlite3.connect('Feeds.db')
    c = conn.cursor()
    c.execute("UPDATE feeds SET feedTitle = (:title), summary = (:summary), category = (:category), author = (:author), link = (:link) WHERE feedId = (:id)",{'title':title,'summary':summary,'category':category,'author':author,'link':link,'id':feedId})
    feed=c.fetchone()
    conn.commit()
    conn.close()
    return feed

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
    
def checkFeedId(feedId):
    conn = sqlite3.connect('Feeds.db')
    c = conn.cursor()
    c.execute("SELECT * FROM feeds where feedId = (:value)",{'value':feedId})
    record = c.fetchone()
    conn.commit()
    conn.close()
    if record:
        return 1
    else:
        return 0

def checkUserId(userId):
    conn = sqlite3.connect('Feeds.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users where userId = (:value)",{'value':userId})
    record = c.fetchone()
    conn.commit()
    conn.close()
    if record:
        return 1
    else:
        return 0

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
            rolesDict['Values'].append({'Role':rows[1],'Create': rows[2],'Read':rows[3],'Edit':rows[4],'Delete':rows[5]})
        return rolesDict, 200
    else:
        return {'Format':'False'}, 401
        
def updateRole(role,c,r,u,d,userId=None):
    conn = sqlite3.connect('Feeds.db')
    cur= conn.cursor()
    cur.execute("SELECT * FROM roles where role=?",(role,))
    records = cur.fetchone()
    if records:
        if(userId==None):
            cur.execute("SELECT adminId FROM roles where role=?",(role,))
            records = cur.fetchone()
            cur.execute("UPDATE roles set cFeed=(?),rFeed=(?),uFeed=(?),dFeed=(?) where adminId=(?)",(c,r,u,d,records[0]))
            cur.execute("UPDATE users set cFeed=(?),rFeed=(?),uFeed=(?),dFeed=(?) where adminId=(?)",(c,r,u,d,records[0]))
        else:
            cur.execute("SELECT adminId FROM roles where role=?",(role,))
            records = cur.fetchone()
            cur.execute("UPDATE users set cFeed=?,rFeed=?,uFeed=?,dFeed=? where userId=?",(c,r,u,d,userId))
            
        conn.commit()
        conn.close()
        return {'Format':'True'}, 200
    else:
        conn.commit()
        conn.close()
        return {'Format':'False'}, 401
    

def deleteFeed(feedId,userId):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("DELETE FROM feeds WHERE feedId=? and userId=?",(feedId,userId))    
    conn.commit()
    conn.close()
    
def deleteUser(userId):
    conn = sqlite3.connect('Feeds.db')
    c= conn.cursor()
    c.execute("DELETE FROM users WHERE userId=?",(userId,))
    conn.commit()
    conn.close()
    

    