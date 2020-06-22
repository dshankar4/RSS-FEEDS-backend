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

@app.route('/')
def hello():
    return "Hello World!!!"

if __name__ == '__main__':
    app.run()

