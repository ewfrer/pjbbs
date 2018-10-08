from pjke2 import celery_server
from exts import mail
from flask_mail import Message

@celery_server.task
def sendEmailCode(recvemail,r):
    msg = Message("邮箱验证码", recipients=[recvemail], body="验证码为" + r)
    mail.send(msg)