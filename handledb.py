from app import app
db= SQLAlchemy(app)

class FeedXmls(db.Model):
    __tablename__="feedXmls"
    feedXmlId=db.Column('feedXmlId',db.Integer,primary_key=True)
    feedXml=db.Column('feedXml',db.String)
    category=category=db.Column('category',db.String)

class Roles(db.Model):
    __tablename__="roles"
    adminId= db.Column('adminId',db.Integer,primary_key=True)
    role=db.Column('role',db.String,unique=True)
    
class Users(db.Model,UserMixin):
    __tablename__="users"
    userId=db.Column('userId',db.Integer,primary_key=True)
    adminId=db.Column('adminId',db.Integer,db.ForeignKey('roles.adminId'))
    roles = db.relationship("Roles", backref='adminId_roles')
    firstname=db.Column('firstname',db.String)
    lastname=db.Column('lastname',db.String)
    email=db.Column('email',db.String,unique=True)
    password=db.Column('password',db.String)
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

class Comments(db.Model):
    __tablename__="comments"
    commentId=db.Column('commentId',db.Integer,primary_key=True)
    userId=db.Column('userId',db.Integer,db.ForeignKey('users.userId'))
    users = db.relationship("Users", backref='userId_comments')
    feedId=db.Column('feedId',db.Integer,db.ForeignKey('feeds.feedId'))
    feeds = db.relationship("Feeds", backref='feedId_comments')
    comment=db.Column('comment',db.String)


class UserLike(db.Model):
    __tablename__="userLike"
    userId=db.Column('userId',db.Integer,db.ForeignKey('users.userId'))
    users = db.relationship("Users", backref='userId_userlike')
    feedId=db.Column('feedId',db.Integer,db.ForeignKey('feeds.feedId'))
    feeds = db.relationship("Feeds", backref='feedId_userlike')
    like=db.Column('like',db.Boolean)
    dislike=db.Column('dislike',db.Boolean)
    likeId=db.Column('likeId',db.Integer,primary_key=True)
    
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
                
class Controllers(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self,name,**kwargs):
        return redirect(url_for('adminLogin'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated
        
class RolesController(Controllers):
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
        records=getSpecialRights(current_user.userId)[0]
        if int(records[1])==1:
            return True
        return False
    @property
    def can_create(self):
        records=getSpecialRights(current_user.userId)[0]
        if int(records[1])==1:
            return True
        return False
    @property
    def can_edit(self):
        records=getSpecialRights(current_user.userId)[0]
        if int(records[1])==1:
            return True
        return False
    @property
    def can_delete(self):
        records=getSpecialRights(current_user.userId)[0]
        if int(records[1])==1:
            return True
        return False
        
@event.listens_for(Users.password,'set',retval=True)
def hashPass(target,value,oldvalue,initiator):
    if value!=oldvalue:
        return bcrypt.generate_password_hash(value).decode('utf-8')
    return value
    
app.config['FLASK_ADMIN_SWATCH'] = 'Darkly' 
admin=Admin(app,name='Admin Panel',template_mode='bootstrap3',index_view=MyAdminIndexView())
login_manager= LoginManager()
login_manager.init_app(app)
login_manager.login_view= 'login'


@app.route('/login',methods=['POST','GET'])
def adminLogin():    
    if request.method== 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        records=selectEmail(email)
        user = Users.query.filter_by(email=email).first()
        if records==None:
            flash('Invalid User')
            return redirect(url_for('adminLogin'))
        elif bcrypt.check_password_hash(records[5], password):
            if records[1]!=2:
                login_user(user)
                flash('Logged in successfully.')
                return redirect(url_for('admin.index'))
            else:
                flash('Invalid User')
                return redirect(url_for('adminLogin'))
        else:   
            return redirect(url_for('adminLogin'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def adminLogout():    
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('adminLogin'))

@login_manager.user_loader
def load_user(id):
    return Users.query.filter_by(userId=id).first()
    
admin.add_view(RolesController(Roles, db.session))
admin.add_view(UsersController(Users, db.session))
admin.add_view(Controller(SpecialRights, db.session))
admin.add_view(FeedXmlsController(FeedXmls, db.session))
admin.add_view(FeedsController(Feeds, db.session))
admin.add_view(CommentController(Comments, db.session))
admin.add_view(UserLikeController(UserLike, db.session))

