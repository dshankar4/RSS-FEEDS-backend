from Db import handleDb,getXml,getFeeds
from models import feeds

import feedparser
from pytz import timezone
import dateutil.parser
import re
from datetime import date,datetime
import dateutil.relativedelta

#Gets the RSS feeds and split it into a dictionary.
#feedxmls is a dictionary with category as keys.
def splitFeeds():
    record=getXml()
    feedxmls=dict()
    for value in record:
        if value[2] in feedxmls:
            feedxmls[value[2]].append(value[1])
        else:
            feedxmls[value[2]]=list()
            feedxmls[value[2]].append(value[1])
    return feedxmls

#It parses all the RSS feeds and returns the parsed feeds as dictionary
def parseFeeds(feedxmls):
        feedparsed=dict()
        for keys in feedxmls:
            feedparsed[keys] = [feedparser.parse(feedxml) for feedxml in feedxmls[keys]]
        return feedparsed

#Cleans the data. Unwanted data and parsing images from the Rss feeds.
#Finally getting from Database and store it into class object and returning the class object.
def cleanData(feedparsed):
    allFeeds=[]
    for keys in feedparsed:
        for feednews in feedparsed[keys]:
            for feed in feednews['entries']:
                feedTitle=feed['title']
                link=feed['link']
                time = feed['published']
                utc=timezone('UTC')
                ist=timezone('Asia/Kolkata')
                time = str(dateutil.parser.parse(time).astimezone(utc).astimezone(ist))
                summary=feed['summary']
                clean = re.compile('<.*?>')
                summary = re.sub(clean,'',summary)
                imageUrl='https://www.zylogelastocomp.com/wp-content/uploads/2019/03/notfound.png'
                logo='https://th.bing.com/th/id/OIP.w2McZSq-EYWxh02iSvC3xwHaHa?pid=Api&rs=1'
                author=None
                for Keys in feed:
                    if(Keys=='author' and len(feed['author'])!=0):
                        author=feed['author']
                    if(Keys=='media_content'):
                        imageUrl=feed['media_content'][0]['url']
                        if(len(imageUrl)==0):
                            imageUrl='https://www.zylogelastocomp.com/wp-content/uploads/2019/03/notfound.png'
                category=keys
                times=datetime.strptime(time[:19],'%Y-%m-%d %H:%M:%S')
                dispTime= str(times.strftime('%H:%M:%S %d %B %Y,%A'))
                d = datetime.strptime(dispTime[:5],"%H:%M")
                dispTime=str(d.strftime("%I:%M %p"))+' on '+dispTime[8:] 
                allFeeds.append(feeds(feedTitle,summary,time,imageUrl,category,author,link,dispTime,logo,1))           
    return getFeeds(allFeeds)

#Read records from database and return.
#to avoid unnecasary calls every call.
def returnRecord():
    handleDb()
    records=cleanData(parseFeeds(splitFeeds()))
    return records

def returnNoRepRecord(records):
    temp=[]
    for rows in records:
        if rows[1] not in temp:
            temp.append(rows[1])
            records.remove(rows)
    return records
    


# Collects all the data as class of object and converts it into list of dictionary .Collects the category in a seperate variable.
# returns the feeds and category to app.py 
# Since a single post can be in multiple categories. I filter the unique feeds in allFeedsnorep which has no repititive data.
# Allfeeds has repititive data on category.
def returnData(records):    
    allFeeds=[]
    category=[]
    for rows in records:
        allFeeds.append({'unikey':rows[0],'feedTitle':rows[1],'summary':rows[2],'time':rows[3],'imageUrl':rows[4],'category':rows[5],'author':rows[6],'link':rows[7],'like':rows[8],'dislike':rows[9],'dispTime':rows[10],'logo':rows[11],'userId':rows[12]})
        if rows[5] not in category:
            category.append(rows[5])
    
    allFeeds=sorted(allFeeds, key = lambda k:k['time'], reverse=True)
    return [allFeeds,category]

#With the keys and sort type. We generate the json here and return the actual feed of keys.
# Sorted in both the ways (ascending and desending)
def filtersort(category,filterType,order,time,records,recordsNoRep,key=None,search=None):
        
    if category=='Allfeeds':
        records=recordsNoRep
    categoryList=[]
    temptitle=[]
    for rows in records:
        if rows[5] not in categoryList:
            categoryList.append(rows[5])

    notFound=0
    if category not in categoryList:
        if category!='Allfeeds':
            notFound=1
    if order!='up' and order!='down':
        notFound=1
    if(filterType!='dates' and filterType!='titles' and filterType!='likes'):
        notFound=1
    if notFound==1:
        return {'Format': 'False'}, 401

    filterFeed={}
    filterFeed['Format']='True'
    filterFeed[filterType]=dict()
    flag=0
    if(category=='Allfeeds'):
        flag=1
    for rows in records:
        #Filtering the unique feedTitles
        if rows[1] not in temptitle:
            temptitle.append(rows[1])
            times=datetime.strptime(rows[3][:19],'%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            # Applying the given filter.
            if(time=='alltime'):
                newTime=now +  dateutil.relativedelta.relativedelta(years=-5)
            elif(time=='thisday'):
                newTime=now +  dateutil.relativedelta.relativedelta(days=-1)
            elif(time=='thisweek'):
                newTime=now +  dateutil.relativedelta.relativedelta(weeks=-1)
            elif(time=='thishour'):
                newTime=now +  dateutil.relativedelta.relativedelta(hours=-1)
            elif(time=='thismonth'):
                newTime=now +  dateutil.relativedelta.relativedelta(months=-1)
            elif(time=='thisyear'):
                newTime=now +  dateutil.relativedelta.relativedelta(years=-1)
            else:
                return {'Format': 'False'}, 401
            if(notFound==0):
                checktime=str(newTime.strftime('%Y-%m-%d %H:%M:%S'))+'+5:30'
                # Check the time filter
                if(rows[3]>=checktime):
                    if key==None:
                        if((search!=None and (bool(re.search(search,rows[1],re.IGNORECASE)) or bool(re.search(search,rows[2],re.IGNORECASE))) and (rows[5]==category or flag==1)) or ((rows[5]==category or flag==1) and  (search==None)) ):
                            if filterType=='likes':
                                if rows[8] not in filterFeed['likes']:
                                    filterFeed['likes'][rows[8]]=list()
                            if filterType=='titles':
                                if rows[1].upper()[0] not in filterFeed['titles']:
                                    filterFeed['titles'][rows[1].upper()[0]]=list()
                            if filterType=='dates':
                                if rows[3][:10] not in filterFeed['dates']:
                                    filterFeed['dates'][rows[3][:10]]=list()
                    else:
                        #If they are searching, the following feeds are returned by search. If not search, all feeds are returned
                        if((search!=None and (bool(re.search(search,rows[1],re.IGNORECASE)) or bool(re.search(search,rows[2],re.IGNORECASE))) and (rows[5]==category or flag==1)) or ((rows[5]==category or flag==1) and  (search==None)) ):
                            if filterType=='likes' and rows[8]==int(key):
                                if rows[8] not in filterFeed['likes']:
                                    filterFeed['likes'][rows[8]]=list()
                                filterFeed['likes'][rows[8]].append({'unikey':rows[0],'id':0,'feedTitle':rows[1],'summary':rows[2],'time':rows[3],'imageUrl':rows[4],'category':rows[5],'author':rows[6],'link':rows[7],'like':rows[8],'dislike':rows[9],'dispTime':rows[10],'logo':rows[11],'userId':rows[12]}) 
                            elif filterType=='titles' and rows[1].upper()[0]==key.capitalize():
                                if rows[1].upper()[0] not in filterFeed['titles']:
                                    filterFeed['titles'][rows[1].upper()[0]]=list()
                                filterFeed['titles'][rows[1].upper()[0]].append({'unikey':rows[0],'id':0,'feedTitle':rows[1],'summary':rows[2],'time':rows[3],'imageUrl':rows[4],'category':rows[5],'author':rows[6],'link':rows[7],'like':rows[8],'dislike':rows[9],'dispTime':rows[10],'logo':rows[11],'userId':rows[12]})                
                            elif filterType=='dates' and rows[3][:10]==key:
                                if rows[3][:10] not in filterFeed['dates']:
                                    filterFeed['dates'][rows[3][:10]]=list()
                                filterFeed['dates'][rows[3][:10]].append({'unikey':rows[0],'id':0,'feedTitle':rows[1],'summary':rows[2],'time':rows[3],'imageUrl':rows[4],'category':rows[5],'author':rows[6],'link':rows[7],'like':rows[8],'dislike':rows[9],'dispTime':rows[10],'logo':rows[11],'userId':rows[12]})                

    if key==None:
        if order=='up':
            filterFeed[filterType] = {key : filterFeed[filterType][key] for key in sorted(filterFeed[filterType])}
        else:
            filterFeed[filterType] = {key : filterFeed[filterType][key] for key in sorted(filterFeed[filterType],reverse=True)}
        return filterFeed, 200
    else:
        keys=key
        if filterType=='dates':
            if keys not in filterFeed['dates']:
                notFound=1
        elif filterType=='titles':
            if keys.capitalize() not in filterFeed['titles']:
                notFound=1
        elif filterType=='likes':
            if int(keys) not in filterFeed['likes']:
                notFound=1
        if notFound==1:
            return {'Format': 'False'}, 401
        if filterType=='dates' and order=='down':
            filterFeed['dates'][keys]=sorted(filterFeed['dates'][keys], key = lambda i:i['time'])
        elif filterType=='dates':
            filterFeed['dates'][keys]=sorted(filterFeed['dates'][keys], key = lambda i:i['time'],reverse=True)
        if filterType=='titles' and order=='down':
            filterFeed['titles'][keys.capitalize()]=sorted(filterFeed['titles'][keys.capitalize()], key = lambda i:i['feedTitle'])
        elif filterType=='titles':
            filterFeed['titles'][keys.capitalize()]=sorted(filterFeed['titles'][keys.capitalize()], key = lambda i:i['feedTitle'],reverse=True)
        return filterFeed, 200
