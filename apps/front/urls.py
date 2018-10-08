# 前台
from flask import Blueprint,request,make_response,session
from flask import render_template
from flask.views import MethodView
from apps.front.forms import SendSmsCodeForm,SignupFrom,SigninForm,AddPostForm
import string
import random
from dysms_python.demo_sms_send import send_sms
from flask import jsonify
from apps.common.baseResp import *
import json
from apps.common.captcha.xtcaptcha import Captcha
from io import BytesIO
from apps.common.memcachedUtil import saveCache,delete
from apps.front.models import  FrontUser
from exts import db
from functools import wraps
from apps.common.models import Banner,Post,Tag
from apps.cms.models import Boarder
from config import *
from flask import redirect
from flask import url_for
from flask_paginate import Pagination,get_page_parameter
import math
from apps.common.models import Common
from app import celery_server


bp = Blueprint('front',__name__)

#限制登录的装饰器
def lonigDecotor(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if not session.get(FRONT_USER_ID,None): #如果没有front_user_id 或者为空返回登录界面
            return redirect(location=url_for("front.signin"))
        else:
            r = func(*args,**kwargs)
            return r
    return inner
class Page:
    countofpage = 10    #每页多少个帖子
    @property
    def page(self):
        count = Post.query.count()  #一共有多少个帖子
        return math.ceil(count / self.countofpage) #帖子总数除以每页帖子数量得到总共有多少页,余数向上取整
    currentpage = 0 #默认是第0页
    posts = None

@bp.route("/")
def index():
    banners =  Banner.query.order_by(Banner.priority.desc()).limit(4)
    boarder = Boarder.query.all()
    boarder_id = request.args.get("boarder_id")

    page = Page()   #封装分页的信息 方便使用
    currentpage = request.args.get("current_page") #获取到当前是第几页
    if not currentpage or int(currentpage) < 0 : #如果没有传递页面,默认是从0页开始
        currentpage = 0
    currentpage = int(currentpage)
    if currentpage >= page.page:
        currentpage = page.page- 1
    begin = currentpage * page.countofpage  #偏移量  比如第一页,这个值就是 0  第一条
    end = begin + page.countofpage          #偏移量  比如第一页,这个值就是 10   最后一条

    #按照阅读量进行排序
    readCount = request.args.get("readCount",None)
    new = request.args.get("NEW", None)
    if boarder_id:
        if readCount :
                posts = Post.query.filter(Post.board_id == boarder_id and Post.status == True).order_by(Post.readCount.desc(),Post.create_time.desc()).slice(begin,end)
        else:
            posts = Post.query.filter(Post.board_id == boarder_id).order_by(Post.create_time.desc()).slice(begin, end) #切片查 从begin到end 每次最多查十条
    else:
        if readCount :
            posts = Post.query.order_by(Post.readCount.desc(),Post.create_time.desc()).slice(begin, end)
        else:
            posts = Post.query.outerjoin(Tag, Post.id == Tag.post_id).order_by(Tag.create_time.desc()).slice(begin, end)
    page.posts = posts
    page.currentpage = currentpage
    context = {
        'banners':banners,
        'boarders':boarder,
        'page':page
    }
    return render_template("front/index.html",**context)    #返回给前端显示页面

#前端页面注册
class Signup(MethodView):
    def get(self):
        return render_template("front/signup.html")
    def post(self):
        fm = SignupFrom(formdata=request.form)
        if fm.validate():
            # 把这个用户保存到数据库中
            u = FrontUser(telephone=fm.telephone.data,username=fm.username.data,password=fm.password.data)
            db.session.add(u)
            db.session.commit()
            delete(fm.telephone.data)
            return jsonify(respSuccess("账号注册成功"))
        else:
            return jsonify(respParamErr(fm.err))

@bp.route("/send_sms_code/",methods=['post'])
@celery_server.task
def sendSMSCode():
    fm = SendSmsCodeForm(formdata=request.form)
    if fm.validate():
        #生成验证码
        source = string.digits
        source = ''.join(random.sample(source, 4))
        #发送验证码
        r = send_sms(phone_numbers=fm.telephone.data,smscode=source)
        if json.loads(r.decode("utf-8"))['Code'] == 'OK':
            saveCache(fm.telephone.data, source, 30 * 60)    # 存到缓存中
            return jsonify(respSuccess("短信验证码发送成功，请查收"))
        else:  # 发送失败
            return jsonify(respParamErr("请检查网络"))
    else:
        return jsonify(respParamErr(fm.err))
@bp.route("/logout/")
def logout():
    session.pop(FRONT_USER_ID)  #从session删除用户id
    return redirect(url_for("front.index"))

@bp.route("/img_code/")
def ImgCode():
    # 生成6位的字符串
    # 把这个字符串放在图片上
    #  用特殊字体
    #  添加横线
    #  添加噪点
    text, img = Captcha.gene_code()  # 通过工具类生成验证码
    print(text)
    out = BytesIO()  # 初始化流对象
    img.save(out, 'png')  # 保存成png格式
    out.seek(0)  # 从文本的开头开始读
    saveCache(text, text, 60)
    resp = make_response(out.read())  # 根据流对象生成一个响应
    resp.content_type = "image/png"  # 设置响应头中content-type
    return resp
#前端页面登录
class Signin(MethodView):
    def get(self):
        # 从那个页面点击的注册按钮  (Referer: http://127.0.0.1:9000/signin/)
        location = request.headers.get("Referer")
        if not location :        # 如果直接输入的注册的连接，location为空
            location = '/'
        context = {
            'location':location
        }
        return render_template("front/signin.html",**context)
    def post(self):
        fm = SigninForm(formdata=request.form)
        if fm.validate():
            # 通过电话查询密码
            user = FrontUser.query.filter(FrontUser.telephone == fm.telephone.data).first()
            if not user :
                return jsonify(respParamErr("没有注册"))
            r = user.checkPwd(fm.password.data)
            if r :#登录成功
                remberme = request.values.get("remberme")
                session[REMBERME] = SIGNIN  # 存储登录状态
                session[FRONT_USER_ID] = user.id    #登录成功保存用户的id
                if remberme == "1":  # 记住我  这个功能
                    session.permanent = True  # 31天后清除
                return jsonify(respSuccess("登录成功"))
            else:
                return jsonify(respParamErr("密码错误"))
        else:
            return jsonify(respParamErr(fm.err))
#管理帖子 添加帖子
class AddPost(MethodView):
    decorators = [lonigDecotor] #限制没有登录不能访问,给返回登录界面
    def get(self):
        board = Boarder.query.all()
        context = {
            "boards":board
        }
        return render_template("front/addpost.html",**context)
    def post(self):
        fm = AddPostForm(formdata=request.form)
        if fm.validate():
            user_id = session[FRONT_USER_ID]
            post = Post(title=fm.title.data,content=fm.content.data,board_id=fm.boarder_id.data,user_id=user_id)
            db.session.add(post)
            db.session.commit()
            return jsonify(respSuccess("发布成功"))
        else:
            return jsonify(respParamErr(fm.err))

#展示帖子详情
@bp.route("/showpostdetail/")
def showpostdetail():
    post_id = request.args.get("post_id")   #拿到帖子id
    if not post_id:         #如果拿不到帖子id 正常点击都可以拿到  返回主页
        return render_template("/")
    post = Post.query.filter(Post.id == post_id).first()     #通过帖子id查找帖子
    if not post:        #如果拿不到帖子 正常点击都可以  返回主页
        return render_template("/")
    commoms = Common.query.filter(Common.post_id == post_id).all()
    if post.readCount:  #点击一下增加次阅读量
        post.readCount = post.readCount + 1
    else:
        post.readCount = 1
    db.session.commit()
    context = {
        'post':post,
        'commoms':commoms
    }
    return render_template("front/postdetail.html",**context)
#评论
@bp.route("/addcommon/",methods=['post'])
def addCommon():
    # 判断用户有没有登录
    # 获取当前用户的id
    user_id = session.get(FRONT_USER_ID,None)
    if not user_id :
        return jsonify(respParamErr("请先登录"))
    # 获取帖子的id
    post_id = request.values.get("post_id")
    # 获取评论的内容
    content = request.values.get("content")
    if not content:
        return jsonify(respParamErr("贴子内容不能为空"))
    # 在数据库中插入
    commom = Common(content=content,post_id=post_id,user_id=user_id)
    db.session.add(commom)
    db.session.commit()
    return jsonify(respSuccess("评论成功"))


bp.add_url_rule("/addpost/", endpoint='addpost', view_func=AddPost.as_view('addpost'))
bp.add_url_rule("/signin/", endpoint='signin', view_func=Signin.as_view('signin'))
bp.add_url_rule("/signup/",endpoint='signup',view_func=Signup.as_view('signup'))

#每次登录之前都会访问
@bp.context_processor
def request_befor():
    front_user_id = session.get(FRONT_USER_ID,None)
    if front_user_id:
        user = FrontUser.query.filter(FrontUser.id == front_user_id).first()
        return {'user': user}
    else:
        return {}


