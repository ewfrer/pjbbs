# 进行表单校验
from flask_wtf import FlaskForm
from wtforms import IntegerField,StringField
from wtforms.validators import Email,InputRequired,Length,EqualTo,URL
from apps.cms.models import User
from wtforms.validators import ValidationError
from flask import jsonify
from apps.common.baseResp import  respParamErr
from apps.common.memcachedUtil import  getCache
from apps.common.models import Banner
from apps.cms.models import Boarder
class BaseForm(FlaskForm):
    @property #把函数变成了属性来调用
    def err(self):
        return self.errors.popitem()[1][0]
class UserForm(BaseForm):
    email = StringField(validators=[Email(message="必须是邮箱"),InputRequired(message="不能为空")])
    password = StringField(validators=[InputRequired(message="密码不能为空"),Length(min=6,max=40,message="密码长度是6-40位")])

class ResetPwdForm(BaseForm):
    oldpwd = StringField(validators=[InputRequired(message='必须输入旧密码')])
    newpwd = StringField(validators=[InputRequired(message='必须输入新密码')])
    newpwd2 = StringField(validators=[EqualTo("newpwd",message='密码不一致')])

class ResetEmailSendCode(BaseForm):
    email = StringField(validators=[Email(message="必须为邮箱"),InputRequired(message='不能为空')])
    def validate_email(self,filed):
        #判断邮箱在不在
        user = User.query.filter(User.email == filed.data).first()
        if user:
            return jsonify(respParamErr(msg='邮箱已注册'))

class ResetEailForm(ResetEmailSendCode):
    emailCode = StringField(validators=[InputRequired(message='必须输入'),Length(min=6,max=6,message='长度必须为六')])
    def validate_emailCode(self,filed):
        emailcode = getCache(filed.data)
        # upper()  不区别大小写
        print("校验验证码")
        if not emailcode or emailcode != filed.data.upper():
            return jsonify(respParamErr(msg='请输入正确的邮箱验证码'))

#校验轮播图添加
class BannerForm(BaseForm):
    bannerName = StringField(validators=[InputRequired(message="不能为空")])
    imglink = StringField(validators=[InputRequired(message="不能为空"),URL(message="必须是一个url地址")])
    link = StringField(validators=[InputRequired(message="不能为空"),URL(message="必须是一个url地址")])
    priority = IntegerField(validators=[InputRequired(message='必须输入优先级')])

    #判断用户输入的url是否已经存在
    def validate_imglink(self,filed):
        r = Banner.query.filter(Banner.imglink == filed.data).first()
        if r :
            raise ValidationError('图片的url已存在,请勿重复添加'+str(r.id)+r.bannerName)
        # 判断用户输入的url是否已经存在
    def validate_link(self,filed):
        r = Banner.query.filter(Banner.link == filed.data).first()
        if r:
            raise ValidationError("内容的url已存在，请勿重复添加" + str(r.id) + r.bannerName)
# 校验轮播图更新
class BannerUpdate(BannerForm):
    id = IntegerField(validators=[InputRequired(message="请传入id")])
    def validate_imglink(self,filed):
        pass
    def validate_link(self,filed):
        pass
#校验板块管理
class BoarderForm(BaseForm):
    boardername = StringField(validators=[InputRequired(message="不能为空")])
    postnum = StringField(validators=[InputRequired(message="不能为空")])

    def validate_boardername(self,filed):
        r = Boarder.query.filter(Boarder.boardername == filed.data).first()
        if r :
            raise ValidationError("该板块已存在,请勿重复添加"+str(r.id) + r.boardername)
class BoarderUpdate(BaseForm):
    id = IntegerField(validators=[InputRequired(message="请传入id")])
    boardername = StringField(validators=[InputRequired(message="不能为空")])

