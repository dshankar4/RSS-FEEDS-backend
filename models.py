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