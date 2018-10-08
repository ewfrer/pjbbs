from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField
from wtforms.validators import Regexp,InputRequired,Length,EqualTo
import hashlib
from flask import jsonify
from apps.common.baseResp import  *
from apps.front.models import FrontUser
from apps.common.memcachedUtil import getCache,delete
from wtforms.validators import ValidationError

class BaseForm(FlaskForm):
    @property    # 把函数变成了属性来调用
    def err(self):
        return self.errors.popitem()[1][0]

class SendSmsCodeForm(BaseForm):     #前端发送验证码
    telephone = StringField(validators=[Regexp('^1[35786]\d{9}$',message='请输入正确电话号码')])
    sign = StringField(validators=[InputRequired(message="必须输入签名")])
    def validate_telephone(self,filed):
        u= FrontUser.query.filter(FrontUser.telephone==filed.data).first()
        if u :
            raise ValidationError('手机号已经注册过了')
    def validate_sign(self,filed):
        sign = md5(self.telephone.data)
        print(sign)
        if sign != filed.data:
            raise ValidationError('请输入正确的签名')

class SignupFrom(SendSmsCodeForm):  #前端注册
    username = StringField(validators=[InputRequired(message="必须输入用户名"),Length(min=6,max=20,message="长度必须时6到20位")])
    password = StringField(validators=[InputRequired(message="必须输入密码"),Length(min=6,max=20,message="密码必须是6-20位")])
    password1 = StringField(validators=[EqualTo('password',message="两次密码必须一致")])
    smscode = StringField(validators=[InputRequired(message="必须输入手机验证码")])
    captchacode = StringField(validators=[InputRequired(message="必须输入图片验证码")])
    sign = StringField()
    def validate_sign(self,filed):
        pass
    def validate_smscode(self,filed):
        smscode= getCache(self.telephone.data)
        if not smscode:
            raise ValidationError("请输入验证码")
        if smscode.upper() != filed.data:
            raise ValidationError("请输入正确的手机验证码")
    def validate_captchacode(self,filed):
        if not getCache(filed.data):
            raise ValidationError("请输入正确的图片验证码")
    def validate_username(self,filed):
        u = FrontUser.query.filter(FrontUser.username == filed.data).first()
        if u:
            raise ValidationError("用户名已存在")

class SigninForm(BaseForm): #前端登录
    telephone = StringField(validators=[Regexp('^1[35786]\d{9}$', message='请输入正确电话号码')])
    password = StringField(validators=[InputRequired(message="必须输入密码"), Length(min=6, max=20, message="密码必须是6-20位")])

def md5(telephone):
    m = hashlib.md5()
    v = telephone + 'jiangwangzi'
    m.update(v.encode("utf-8"))
    r = m.hexdigest()
    return r
class AddPostForm(BaseForm):#前端发帖子校验
    title = StringField(validators=[InputRequired(message="标题不能为空")])
    boarder_id = IntegerField(validators=[InputRequired(message="板块不能为空")])
    content = StringField(validators=[InputRequired(message="内容不能为空")])