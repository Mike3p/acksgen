import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER = "var/www/uploads"
    ALLOWED_EXTENSIONS = {'txt', 'yaml'}
    SESSION_TYPE = 'filesystem'
    MAX_CONTENT_LENGTH = 1024 * 1024
    UPLOAD_EXTENSIONS = ['.yaml']
    PERMANENT_SESSION_LIFETIME = 3600
