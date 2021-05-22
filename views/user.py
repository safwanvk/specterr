from sqlalchemy import text
from flask import jsonify, request,make_response
from flask_restful import Resource,reqparse
from sqlalchemy.exc import SQLAlchemyError
from models import *

# class Hello(Resource):
#     def get(self):
#         return make_response(jsonify({'msg': 'Success'}), 200)

class UserManagement(Resource):

    def post(self):
       
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('email',type=str,required=True,help='email is required and must be str')
            parser.add_argument('password',required=True,help='password is required')
            
            args = parser.parse_args()
            args['password'] = bcrypt.generate_password_hash(args.get('password'), 10)

            user = Users(**args)
            db.session.add(user)
            db.session.commit()

            return make_response(jsonify({'msg':'User Created'}), 200)
        except SQLAlchemyError as e:
            print(e.__dict__['orig'].args[0])
            if e.__dict__['orig'].args[0] == 1062:
                return make_response(jsonify({'msg': e.__dict__['orig'].args[1]}), 400)
            return make_response(jsonify({'msg': 'Invalid Data'}), 400)
        except reqparse.ParserError as e:
            print(e.args)
            return make_response(jsonify({"msg":e.args[0]}), 400)
        except Exception as e:
            print(e)
            return make_response(jsonify({'msg': 'Server Error'}), 500) 