from sqlalchemy import text
from flask import jsonify, request,make_response
from flask_restful import Resource

class Hello(Resource):
    def get(self):
        return make_response(jsonify({'msg': 'Success'}), 200)