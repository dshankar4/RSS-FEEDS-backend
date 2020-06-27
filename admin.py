from __main__ import app,login_manager,admin,bcrypt
from flask import Flask,request,render_template,redirect,url_for,flash
from sqlalchemy import event
from flask_admin import Admin, AdminIndexView
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_login import login_user,current_user,logout_user,login_required
from Db import FeedXmls,Roles,Users,Feeds,Comments,UserLike,SpecialRights,db
from Db import selectEmail,getSpecialRights

class Controllers(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self,name,**kwargs):
        return redirect(url_for('adminLogin'))

class RolesController(Controllers):
    form_columns=['role']   
    def is_accessible(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[6]) and bool(record[3]):
                return True
        return False
    @property
    def can_create(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[6]) and bool(record[2]):
                return True
        return False
    @property
    def can_edit(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[6]) and bool(record[4]):
                return True
        return False
    @property
    def can_delete(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[6]) and bool(record[5]):
                return True
        return False

class UsersController(Controllers):
    form_columns=['roles','firstname','lastname','email','password','userId']
    def is_accessible(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[7]) and bool(record[3]):
                return True
        return False
    @property
    def can_create(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[7]) and bool(record[2]):
                return True
        return False
    @property
    def can_edit(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[7]) and bool(record[4]):
                return True
        return False
    @property
    def can_delete(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[7]) and bool(record[5]):
                return True
        return False

class FeedsController(Controllers):
    form_columns=['users','feedTitle','summary','time','imageUrl','category','author','link','likes','dislikes','dispTime','logo']
    column_filters = ['feedTitle','time','category','likes']
    column_editable_list = ['feedTitle','summary']
    def is_accessible(self):        
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[8]) and bool(record[3]):
                return True
        return False
    @property
    def can_create(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[8]) and bool(record[2]):
                return True
        return False
    @property
    def can_edit(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[8]) and bool(record[4]):
                return True
        return False
    @property
    def can_delete(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[8]) and bool(record[5]):
                return True
        return False

class UserLikeController(Controllers):
    form_columns=['users','feeds','like','dislike']
    def is_accessible(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[9]) and bool(record[3]):
                return True
        return False
    @property
    def can_create(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[9]) and bool(record[2]):
                return True
        return False
    @property
    def can_edit(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[9]) and bool(record[4]):
                return True
        return False
    @property
    def can_delete(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[9]) and bool(record[5]):
                return True
        return False
        

class CommentController(Controllers):
    form_columns=['users','feeds','comment']
    def is_accessible(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[10]) and bool(record[3]):
                return True
        return False
    @property
    def can_create(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[10]) and bool(record[2]):
                return True
        return False
    @property
    def can_edit(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[10]) and bool(record[4]):
                return True
        return False
    @property
    def can_delete(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[10]) and bool(record[5]):
                return True
        return False


class FeedXmlsController(Controllers):
    column_filters = ['category']
    def is_accessible(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[11]) and bool(record[3]):
                return True
        return False
    @property
    def can_create(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[11]) and bool(record[2]):
                return True
        return False
    @property
    def can_edit(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[11]) and bool(record[4]):
                return True
        return False
    @property
    def can_delete(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if bool(record[11]) and bool(record[5]):
                return True
        return False
        
class Controller(Controllers):
    def is_accessible(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if int(record[1])==1:
                return True
        return False
    @property
    def can_create(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if int(record[1])==1:
                return True
        return False
    @property
    def can_edit(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if int(record[1])==1:
                return True
        return False
    @property
    def can_delete(self):
        records=getSpecialRights(current_user.userId)
        for record in records:
            if int(record[1])==1:
                return True
        return False
        
@event.listens_for(Users.password,'set',retval=True)
def hashPass(target,value,oldvalue,initiator):
    if value!=oldvalue:
        return bcrypt.generate_password_hash(value).decode('utf-8')
    return value
    
@login_manager.user_loader
def load_user(id):
    return Users.query.filter_by(userId=id).first()


@app.route('/',methods=['POST','GET'])
def adminLogin():    
    if request.method== 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        records=selectEmail(email)
        user = Users.query.filter_by(email=email).first()
        if records==None:
            flash('Invalid credentials')
            return render_template('login.html')
        elif bcrypt.check_password_hash(records[5], password):
            if records[1]!=2:
                login_user(user)
                flash('Logged in successfully.')
                return redirect(url_for('admin.index'))
            else:
                flash('Invalid credentials')
                return render_template('login.html')
        else:   
            flash('Invalid credentials')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
@login_required
def adminLogout():    
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('adminLogin'))



