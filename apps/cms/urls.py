# 后台
from flask import Blueprint
from flask.views import MethodView
from flask import render_template, session, g
from apps.cms.forms import UserForm, ResetPwdForm, ResetEailForm, ResetEmailSendCode,BannerForm,BannerUpdate,BoarderForm,BoarderUpdate
from flask import request, jsonify
from apps.common.baseResp import *
from exts import db, mail
from flask_mail import Message
from apps.cms.models import *
from config import REMBERME, LOGIN, CURRENT_USER_ID, CURRENT_USER
import string
import random
from apps.common.memcachedUtil import saveCache, getCache
from functools import wraps
from apps.common.models import Banner,Post,Tag
from apps.cms.models import Boarder
from qiniu import Auth
from task import sendEmailCode

bp = Blueprint('cms', __name__, url_prefix="/cms/")

def loginDecotor(func):
    """限制登录的装饰器"""
    @wraps(func)
    def inner(*args, **kwargs):
        login = session.get(REMBERME)
        if login == LOGIN:  #如果login是登录状态
            return func(*args, **kwargs)
        else:
            return render_template("cms/login.html")
    return inner

#给用户赋予权限的装饰器
def checkPermission(permission):
    def outer(func):
        @wraps(func)
        def inner(*args,**kwargs):
            # 取出来当前的用户， 判断这个用户有没有这个权限
            userid = session[CURRENT_USER_ID]
            user = User.query.get(userid)
            r = user.checkpermission(permission)
            if r:   #用户有这个权限
                return func(*args,**kwargs)
            else:
                return render_template("cms/login.html")
        return inner
    return outer


@bp.route("/")
def loginView():
    return render_template("cms/login.html")


@bp.route("/login/", methods=['post'])
def login():
    fm = UserForm(formdata=request.form)    #获取到form表单对象(值)并进行验证
    if fm.validate():   #如果为true
        email = fm.email.data  # 获取到input的值
        pwd = fm.password.data
        user = User.query.filter(User.email == email).first()   #查询user表中有没有符合要求的一条记录
        if not user:  # 如果没有查询到用户
            return jsonify(respParamErr('用户名错误'))
        if user.checkPwd(pwd):#?
            remberme = request.values.get("remberme")
            session[REMBERME] = LOGIN   #存储登录状态
            session[CURRENT_USER_ID] = user.id  #存储userid
            if remberme == "1": #记住我  这个功能
                session.permanent = True  # 31天后清除
            return jsonify(respSuccess('登录成功'))
        else:
            return jsonify(respParamErr('密码错误'))
    else:
        return jsonify(respParamErr(msg=fm.err))


@bp.route('/index/')
@loginDecotor
def cms_index():
    return render_template('cms/cms_index.html')


@bp.route("/logout/")
@loginDecotor
def logout():
    session.clear()
    return render_template("cms/login.html")


@bp.route("/user_infor/")
@loginDecotor
@checkPermission(Permission.USER_INFO)
def user_infor():
    return render_template("cms/userInfo.html")

#修改密码
class ResetPwd(MethodView):
    decorators = [checkPermission(Permission.USER_INFO),loginDecotor]
    def get(self):
        return render_template('cms/resetpwd.html')
    def post(self):
        fm = ResetPwdForm(formdata=request.form)      #获取到form表单对象(值)并进行验证
        if fm.validate():
            #根据id去找用户,然后修改密码
            userid = session[CURRENT_USER_ID]   #把登录状态的id赋值
            user = User.query.get(userid)   #根据id查到用户
            r = user.checkPwd(fm.oldpwd.data)#?
            if r:
                user.password = fm.newpwd.data  #把原来的密码覆盖
                db.session.commit() #提交
                return jsonify(respSuccess(msg='修改成功'))
            else:
                return jsonify(respParamErr(msg='修改失败,密码错误'))
        else:
            return jsonify(respParamErr(msg=fm.err))


#修改邮箱
class ResetEmail(MethodView):
    decorators = [checkPermission(Permission.USER_INFO), loginDecotor]
    def get(self):
        return render_template('cms/resetemail.html')
    def post(self):
        fm = ResetEailForm(formdata=request.form)
        if fm.validate:
            user = User.query.get(session[CURRENT_USER_ID])
            user.email = fm.email.data
            print(fm.email.data)
            db.session.commit()
            return jsonify(respSuccess(msg='修改邮箱成功'))
        else:
            return jsonify(respParamErr(msg=fm.err))


#修改邮箱时发送的验证码
@bp.route("/send_email_code/", methods=['post'])
@loginDecotor
@checkPermission(Permission.USER_INFO)
def sendEmailCode():
    fm = ResetEmailSendCode(formdata=request.form)
    if fm.validate():
        r = string.ascii_letters + string.digits
        r = ''.join(random.sample(r, 6))
        saveCache(fm.email.data, r.upper(), 30 * 60)
        # msg = Message("邮箱验证码", recipients=[fm.email.data], body="验证码为" + r)
        # mail.send(msg)
        recvmail = fm.email.data
        sendEmailCode.dalay(recvmail,r)
        return jsonify(respSuccess(msg='发送成功，请查看邮箱'))
    else:
        return jsonify(respParamErr(msg=fm.err))

#轮播图
@bp.route("/banner/")
@loginDecotor
@checkPermission(Permission.BANNER)
def banner_view():
    banners = Banner.query.all()    #查到所有的轮播图
    context = {
        'banners': banners
    }
    return render_template("cms/banner.html",**context) #返回给后台页面

#添加轮播图
@bp.route("/addbanner/",methods=['post'])
@loginDecotor
@checkPermission(Permission.BANNER)
def addBanner():
    fm = BannerForm(formdata=request.form)
    if fm.validate():
        #拿到输入的值
        banner = Banner(bannerName=fm.bannerName.data,imglink=fm.imglink.data,link=fm.link.data,priority=fm.priority.data)
        db.session.add(banner)  #添加到数据库
        db.session.commit() #提交
        return jsonify(respSuccess(msg="添加成功"))
    else:
        return jsonify(respParamErr(msg=fm.err))

#删除轮播图
@bp.route("/deletebanner/",methods=['post'])
@loginDecotor
@checkPermission(Permission.BANNER)
def deleteBanner():
    # 拿到客户端提交的id    #根据id进行查询删除
    banner_id = request.values.get("id")
    "".isdigit()
    if not banner_id or not banner_id.isdigit():
        return jsonify(respParamErr(msg='请输入正确的banner_id'))
    #根据id 查出来记录
    banner = Banner.query.filter(Banner.id == banner_id).first()
    if banner:
        #在这里删除记录
        db.session.delete(banner)
        db.session.commit()
        return jsonify(respSuccess(msg="删除成功"))
    else:#没有 一般不会走到这里
        return jsonify(respParamErr(msg='请输入正确的banner_id'))

#更新轮播图
@bp.route("/updatebanner/",methods = ['post'])
@loginDecotor
@checkPermission(Permission.BANNER)
def updateBanner():
    fm = BannerUpdate(formdata=request.form)  #客户端的值
    if fm.validate():
        banner = Banner.query.get(fm.id.data)   #数据库的值
        if banner :
            #拿客户端提交的值对数据库的值更新
            banner.link = fm.link.data
            banner.imglink = fm.imglink.data
            banner.priority = fm.priority.data
            banner.bannerName = fm.bannerName.data
            db.session.commit()
            return jsonify(respSuccess(msg="更新成功"))
        else:
            return jsonify(respParamErr(msg="id失效"))
    else:
        return jsonify(respParamErr(msg=fm.err))

# 应该写common中，因为这个视图函数，前后台都要使用
# 给客户端返回上传的令牌（token），因为
@bp.route("/qiniu_token/")
def qiniukey():
    #通过secer-key id 生成一个令牌,返回给客户端
    ak = "gixRZTC9nnM_ODSEyAmDtFPVBD5sBWJo1dsfszvB"
    sk = "X8TYRWzELi-hfyzl1MeAkEbS9i5DKL_8qI4m_o3l"
    q= Auth(ak,sk)
    bucket_name = 'pjssb'
    token = q.upload_token(bucket_name)
    return jsonify({'uptoken':token})

#模块管理   添加板块
class AddBoarder(MethodView):
    decorators = [checkPermission(Permission.PLATE), loginDecotor]
    def get(self):
        boarders = Boarder.query.all()
        context = {
            'boarders': boarders
        }
        return render_template("cms/boarder.html", **context)   #返回boarder页面,并返回查到的数据
    def post(self):
        fm = BoarderForm(formdata=request.form)
        if fm.validate:
            boarder = Boarder(boardername=fm.boardername.data, postnum=fm.postnum.data)
            db.session.add(boarder)
            db.session.commit()
            return jsonify(respSuccess(msg="添加板块成功"))
        else:
            return jsonify(respParamErr(msg=fm.err))
#删除板块
@bp.route("/deleteBoarder/",methods = ['post'])
@loginDecotor
@checkPermission(Permission.PLATE)
def deleteBoarder():
    boarder_id = request.values.get("id")
    "".isdigit()
    if not boarder_id or not boarder_id.isdigit():
        return jsonify(respParamErr(msg="id有误"))
    banner = Boarder.query.filter(Boarder.id == boarder_id).first()
    if banner:
        db.session.delete(banner)
        db.session.commit()
        return jsonify(respSuccess(msg="删除成功"))
    else:
        return jsonify(respParamErr(msg="id有误"))
#更新板块
@bp.route("/updateBoarder/",methods = ['post'])
@loginDecotor
@checkPermission(Permission.PLATE)
def updateBoarder():
    fm = BoarderUpdate(formdata=request.form)
    if fm.validate():
        boarder = Boarder.query.get(fm.id.data)
        if boarder:
            boarder.boardername = fm.boardername.data
            db.session.commit()
            return jsonify(respSuccess(msg="更新成功"))
        else:
            return jsonify(respParamErr(fm.err))
    else:
        return jsonify(respParamErr(msg=fm.err))

#帖子加精管理
@bp.route("/showpost/")
@loginDecotor
@checkPermission(Permission.PLATE)
def showPost():
    posts = Post.query.all()    #查找出所有帖子
    context = {
        'posts':posts
    }
    return render_template("cms/postmgr.html",**context)    #返回给cms帖子管理界面

#加精
@bp.route("/addtag/",methods=['post'])
@loginDecotor
@checkPermission(Permission.POSTS)
def addTag():
    post_id = request.values.get("post_id") #获取到帖子id
    post = Post.query.filter(Post.id == post_id).first()    #通过帖子id查到帖子
    if post:
        tag = Tag(post=post,status=True)    #给帖子进行加精
        db.session.add(tag)
        db.session.commit()
        return jsonify(respSuccess("加精完成"))
    else:
        return jsonify(respParamErr("请传入正确的post_id"))
#取消加精
@bp.route("/deletetag/",methods=['post'])
@loginDecotor
@checkPermission(Permission.POSTS)
def deleteTag():
    post_id = request.values.get("post_id") #拿到帖子id
    tag = Tag.query.filter(Tag.post_id == post_id).first()  #y用帖子id跟数据库的加精表相匹配
    if tag :
        tag.status = False  #取消加精
        db.session.commit()
        return jsonify(respSuccess("取消加精成功"))
    else:
        return jsonify(respParamErr("请传入正确的post_id"))
bp.add_url_rule('/boarder/', endpoint='boarder', view_func=AddBoarder.as_view('boarder'))
bp.add_url_rule('/resetpwd/', endpoint='resetpwd', view_func=ResetPwd.as_view('resetpwd'))
bp.add_url_rule('/resetemail/', endpoint='resetemail', view_func=ResetEmail.as_view('resetemail'))


@bp.context_processor
def requestUser():
    login = session.get(REMBERME)
    if login == LOGIN:
        userid = session[CURRENT_USER_ID]
        user = User.query.get(userid)
        return {'user': user}
    return {}
