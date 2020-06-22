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
@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run()

