from flask import Flask,session,request
from data import returnData,filtersort,returnRecord
from flask_bcrypt import Bcrypt
from flask_jwt_extended import  JWTManager,create_access_token
from flask_restful import Resource, Api
from datetime import datetime
import os
from models import feeds
# from Db import selectEmail,registerUser,addComment,comment,feedEdit,feedUrlAdd,addLikes,addDislikes,newRole, checkFeedId, checkUserId

app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)
app.config['SECRET_KEY']=os.environ.get('SECRET_KEY')
app.config['JWT_SECRET_KEY']=os.environ.get('JWT_SECRET_KEY')



class register(Resource):
    def post(self):
        first_name = request.get_json()['first_name']
        last_name = request.get_json()['last_name']
        email = request.get_json()['email']
        password = bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')
        records=selectEmail(email)
        if records==None:
            registerUser(first_name,last_name,email,password)
            access_token = create_access_token(identity = {'first_name': first_name,'last_name': last_name,'email': email})
            session['email']=email
            return {"access_token": access_token}, 201
        else:
            return {'access_token': 'None'}, 401

class login(Resource):
    def post(self):
        email = request.get_json()['email']
        password = request.get_json()['password']
        records=selectEmail(email)
        if records==None:
            return {"access_token": 'None' }, 401    
        elif bcrypt.check_password_hash(records[5], password):
            access_token = create_access_token(identity = {'first_name': records[2],'last_name': records[3],'email': records[4]})
            session['email']=records[4]
            return {"access_token": access_token}, 201
        else:   
            return {"access_token": 'None' }, 401

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
            access_token = create_access_token(identity = {'first_name': first_name,'last_name': last_name,'email': email})
            session['email']=email
            return {"access_token": access_token}, 201
        else:
            return {'access_token': 'None'}, 401

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


@app.route('/')
def hello():
    return "Hello World!!!"

if __name__ == '__main__':
    app.run()

