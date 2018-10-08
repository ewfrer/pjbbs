from flask import Flask
from celery import Celery
import exts

app = Flask(__name__)
celery_server = Celery(__name__,include=['apps.front.urls'])
celery_server.config_from_object(exts)

if __name__ == '__main__':
    app.run()


