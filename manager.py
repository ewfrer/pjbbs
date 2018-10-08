# flask_script 使用命令行管理项目
from flask_script import Manager
# flask_migrate 数据库迁移脚本
from flask_migrate import Migrate,MigrateCommand
from apps.cms.models import User,Role
from pjkj import app
from exts import db
from  apps.common.models import Banner
from apps.cms.models import User
from apps.common.models import Post

manager=Manager(app)
migrate=Migrate(app,db)
manager.add_command('db',MigrateCommand)


# migrate = Migrate(app)
# manage = Manager(app)
# Migrate(app,db)
# manager.add_command("db",MigrateCommand)

@manager.option('-e','--email',dest='email')
@manager.option('-u','--username',dest ='username')
@manager.option('-p','--password',dest = 'password')
def addcmsuser(email,username,password):
    user = User(email=email,username=username,password=password)
    db.session.add(user)
    db.session.commit()


@manager.option('-n','--rolename',dest='rolename')
@manager.option('-d','--roledesc',dest='roledesc')
@manager.option('-p','--permissions',dest='permissions')
def addcmsrole(rolename,roledesc,permissions):
    r = Role(roleName=rolename,desc=roledesc,permissions=permissions)
    db.session.add(r)
    db.session.commit()
@manager.option('-uid','--user_id',dest='user_id')
@manager.option('-rid','--role_id',dest='role_id')
def useraddrole(user_id,role_id):
    u = User.query.get(user_id)
    r = Role.query.get(role_id)
    u.roles.append(r)
    db.session.commit()
@manager.command
def addpost():
    for i in range(100):
        post = Post(title="title"+str(i),content="content"+str(i),board_id=40,user_id="tUdAWqxJJto3VX5ebXdcHT")
        db.session.add(post)
        db.session.commit()
    print("100个帖子发表完毕")

if __name__ == '__main__':
    manager.run()

