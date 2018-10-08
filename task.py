from celery_app import celery_server
from celery_app import app
from exts import mail
from flask_mail import Message
from  dysms_python.demo_sms_send import send_sms
@celery_server.task
def sendemail(recvemail,r):
    with app.app_context():
        msg = Message("邮箱验证码", recipients=[recvemail], body="验证码为" + r)
        mail.send(msg)
@celery_server.task
def sendsmscode(phone,code):
    send_sms(phone_numbers=phone,smscode=code)