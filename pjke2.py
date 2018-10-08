from celery import Celery
from flask import Flask
import config

app = Flask(__name__)

celery_server = Celery(__name__,include=['task'])
celery_server.config_from_object(config)
if __name__ == '__main__':
    app.run()