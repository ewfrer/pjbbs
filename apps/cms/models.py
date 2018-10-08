
from exts import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

class Boarder(db.Model):
    __tablename__ = 'boarder'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    boardername = db.Column(db.String(99), nullable=False)
    postnum =db.Column(db.Integer,nullable=False,default=0)
    create_time = db.Column(db.DateTime, default=datetime.now)



class Permission:
    USER_INFO = 1
    BANNER = 2
    POSTS = 4
    COMMON = 8
    PLATE = 16
    FRONT_USER = 32
    CMS_USER = 64
    CMS_USER_GROUP = 128

cms_role_user = db.Table(
    'cms_role_user',
    db.Column('cms_role_id',db.Integer,db.ForeignKey('role.id'),primary_key=True),
    db.Column('cms_user_id',db.Integer,db.ForeignKey('user.id'),primary_key=True)
)


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roleName = db.Column(db.String(20), unique=True, nullable=False)
    desc = db.Column(db.String(200))
    permissions = db.Column(db.Integer, default=Permission.USER_INFO)
    # 中间表绑定到角色zh
    users = db.relationship('User', secondary=cms_role_user, backref=db.backref("roles"))


class User(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    _password = db.Column(db.String(200),nullable=False) # 加密过的
    email = db.Column(db.String(30),unique=True,nullable=False)
    join_time = db.Column(db.DateTime,default=datetime.now)

    #返回当前用户的权限
    @property
    def current_user_permission(self):
        #获取当前用户的权限
        mum = 0
        for role in self.roles:
            mum = mum | role.permissions
        print("当前这个用户的权限"+str(mum))
        return mum

    #校验用户是否拥有这个权限
    def checkpermission(self,permission):
        print('---' + str(self.current_user_permission & permission != 0))
        return self.current_user_permission & permission!= 0

    # 因为要特殊处理password
    def __init__(self,password,**kwargs):
        self.password = password
        kwargs.pop('password',None)
        super(User,self).__init__(**kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self,frontpwd):
        # 1. 密码不希望外界访问 2.防止循环引用
        self._password = generate_password_hash(frontpwd)

    def checkPwd(self,frontpwd):
        #return self.password == generate_password_hash(frontpwd)
        return check_password_hash(self._password,frontpwd)