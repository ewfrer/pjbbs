from flask import Flask
from apps.cms.urls import bp as cms_bp
from apps.front.urls import bp as front_bp
from exts import db,mail
from flask_wtf import CSRFProtect
from flask import Flask,send_from_directory
from flask import request,url_for
from flask import jsonify
import config
import os
import string
import time
import hashlib
import random
import json
import re
import sys
import qiniu
from io import BytesIO
import base64
from celery import Celery








app = Flask(__name__)
app.register_blueprint(cms_bp)
app.register_blueprint(front_bp)

app.config.from_object(config)

celery_server = Celery(__name__,include=['task'])
celery_server.config_from_object(config)


CSRFProtect(app=app)
db.init_app(app)
mail.init_app(app)

UEDITOR_UPLOAD_PATH = "images"  # 上传到本地服务器的路径
UEDITOR_UPLOAD_TO_QINIU = False # 是否上传到七牛云
UEDITOR_QINIU_ACCESS_KEY = ""
UEDITOR_QINIU_SECRET_KEY = ""
UEDITOR_QINIU_BUCKET_NAME = ""
UEDITOR_QINIU_DOMAIN = "peouv6xac.bkt.clouddn.com"

#第一次访问
@app.before_first_request
def before_first_request():
    global UEDITOR_UPLOAD_TO_QINIU
    global UEDITOR_QINIU_ACCESS_KEY
    global UEDITOR_QINIU_SECRET_KEY
    global UEDITOR_QINIU_BUCKET_NAME
    global UEDITOR_QINIU_DOMAIN

    UEDITOR_UPLOAD_PATH = app.config.get("UEDITOR_UPLOAD_PATH")
    if UEDITOR_UPLOAD_PATH and not os.path.exists(UEDITOR_UPLOAD_PATH):
        os.mkdir(UEDITOR_UPLOAD_PATH)
    UEDITOR_UPLOAD_TO_QINIU = app.config.get("UEDITOR_UPLOAD_TO_QINIU")
    if UEDITOR_UPLOAD_TO_QINIU:
        try:
            UEDITOR_QINIU_ACCESS_KEY = app.config["UEDITOR_QINIU_ACCESS_KEY"]
            UEDITOR_QINIU_SECRET_KEY = app.config["UEDITOR_QINIU_SECRET_KEY"]
            UEDITOR_QINIU_BUCKET_NAME = app.config["UEDITOR_QINIU_BUCKET_NAME"]
            UEDITOR_QINIU_DOMAIN = app.config["UEDITOR_QINIU_DOMAIN"]
        except Exception as e:
            option = e.args[0]
            raise RuntimeError('请在app.config中配置%s！' % option)

    csrf = app.extensions.get('csrf')
    if csrf:
        csrf.exempt(upload) # 标记是受csrf保护的

# 生成文件的名字 防止文件名称重复覆盖
def _random_filename(rawfilename):
    letters = string.ascii_letters
    random_filename = str(time.time()) + "".join(random.sample(letters,5))
    filename = hashlib.md5(random_filename.encode('utf-8')).hexdigest()
    subffix = os.path.splitext(rawfilename)[-1]
    return filename + subffix

@app.route("/upload/",methods=['GET','POST'])
def upload():
    action = request.args.get('action')
    result = {}
    if action == 'config':
        config_path = os.path.join(app.static_folder or app.static_folder,'config.json')
        with open(config_path,'r',encoding='utf-8') as fp:
            result = json.loads(re.sub(r'\/\*.*\*\/','',fp.read()))

    elif action in ['uploadimage','uploadvideo','uploadfile']:  #不管是什么文件 视频 图片 还是文件 都统称文件 可以一起处理
        image = request.files.get("upfile")
        filename = image.filename
        save_filename = _random_filename(filename)
        result = {
            'state': '',
            'url': '',
            'title': '',
            'original': ''
        }
        if UEDITOR_UPLOAD_TO_QINIU:     #为true 则上传七牛云
            if not sys.modules.get('qiniu'):
                raise RuntimeError('没有导入qiniu模块！')
            q = qiniu.Auth(UEDITOR_QINIU_ACCESS_KEY,UEDITOR_QINIU_SECRET_KEY)
            token = q.upload_token(UEDITOR_QINIU_BUCKET_NAME)
            buffer = BytesIO()
            image.save(buffer)
            buffer.seek(0)
            ret,info = qiniu.put_data(token,save_filename,buffer.read())
            if info.ok:
                result['state'] = "SUCCESS"         #返回参数格式是固定的
                result['url'] = "http://peouv6xac.bkt.clouddn.com/"+ret['key']
                result['title'] = ret['key']
                result['original'] = "http://peouv6xac.bkt.clouddn.com/"+ret['key']
        else:#为False 则上传到本地文件夹  #返回参数格式是固定的
            image.save(os.path.join(UEDITOR_UPLOAD_PATH, save_filename))
            result['state'] = "SUCCESS"
            result['url'] = url_for('ueditor.files',filename=save_filename)
            result['title'] = save_filename,
            result['original'] = image.filename

    elif action == 'uploadscrawl':  #涂鸦 指定文件后缀为png
        base64data = request.form.get("upfile")
        img = base64.b64decode(base64data)
        filename = _random_filename('xx.png')
        filepath = os.path.join(UEDITOR_UPLOAD_PATH,filename)
        with open(filepath,'wb') as fp:
            fp.write(img)
        result = {
            "state": "SUCCESS",
            "url": url_for('files',filename=filename),
            "title": filename,
            "original": filename
        }
    return jsonify(result)

@app.route('/files/<filename>/')
def files(filename):
    return send_from_directory(UEDITOR_UPLOAD_PATH,filename)

#注册一个过滤器    作用是在前端页面显示时间格式为 '一天前'
@app.template_filter('convert')
def converTime(t):
    t = t.strftime("%Y-%m-%d %H:%M:%S")
    t = time.strptime(t, "%Y-%m-%d %H:%M:%S")
    t = time.mktime(t)
    curremt_t = time.time()
    r = curremt_t - t
    if r < 60 and r >0 :
        return  "一分钟之前"
    elif r < 60* 10 and r > 60:
        return "十分钟之前"
    elif r < 60 * 60 and r > 60*10:
        return "一小时之前"
    elif r < 60 * 60 * 10 and r > 60* 60 :
        return "十小时之前"
    else:
        return "一天前"
if __name__ == '__main__':
    app.run(port=99)