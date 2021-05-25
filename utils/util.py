from jose import jwt
import os
from flask import make_response,jsonify, request
from .const import *
from functools import wraps
from werkzeug.datastructures import ImmutableMultiDict
from models import *

# to generate new token for customers
def generate_token(payload):
    token = jwt.encode(payload,
                       os.environ.get('FLASK_SECRET_KEY'), algorithm='HS256')
    return token

def sys_type():

    req = request.environ
    req_from = req.get('HTTP_USER_AGENT')
    if REQ_ENVS_WEB['postman'] in req_from:
        return 'POSTMAN'
    if REQ_ENVS_WEB['mozilla'] in req_from or REQ_ENVS_WEB['appleWebKit'] in req_from or REQ_ENVS_WEB['chrome'] in req_from or REQ_ENVS_WEB['safari'] in req_from:
        return 'WEB'
    
    if REQ_ENVS_WEB['dart'] in req_from:
        return 'MOB'
    
    return None

def auth_error():
    return make_response(jsonify({'msg': 'Invalid Auth Token'}),401)

# auth decorator
def auth(role):
    def decor(func):
        @wraps(func)
        def inner(*args, **kwargs):
            token = ""
            req_sys_type = sys_type()
            if req_sys_type == "WEB" or req_sys_type == 'POSTMAN':
                token = request.cookies.get('acces_token')
            if req_sys_type == "MOB":
                token = request.headers.get('acces_token')
            if token:
                try:
                    # if token exist and decode
                    payload = jwt.decode(
                        token, os.environ.get('FLASK_SECRET_KEY'), algorithms=['HS256'])
                    if payload['role'] in role:
                        http_args = request.args.to_dict()
                        http_args['user_role'] = payload.get('role')
                        http_args['user_id'] = payload.get('id')
                        request.args = ImmutableMultiDict(http_args)
                        return func(*args, **kwargs)
                    else:
                        return auth_error()
                except Exception as e:
                    print(e)
                    return auth_error()
            else:
                return auth_error()
        return inner
    return decor

def allowed_image_filesize(filesize):
    if int(filesize) <= MAX_IMAGE_FILESIZE:
        return True
    else:
        return False


# def allowed_video(filename):

#     if not "." in filename:
#         return False

#     ext = filename.rsplit(".", 1)[1]

#     if ext.upper() in ALLOWED_EXTENSIONS:
#         return True
#     else:
#         return False

def allowed_video(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 