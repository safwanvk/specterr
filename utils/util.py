from jose import jwt
import os
from flask import make_response,jsonify, request
from .const import *

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