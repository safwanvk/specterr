from sqlalchemy import text
from flask import jsonify, request,make_response
from flask_restful import Resource,reqparse
from sqlalchemy.exc import SQLAlchemyError
from models import *
from utils.util import *

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

class UserLogin(Resource):

    def post(self):
        try:
  
            parser = reqparse.RequestParser()

            parser.add_argument('email',type=str, required=True,help='email is required')
            parser.add_argument('password',type=str,required=True,help='password is required')
            data = parser.parse_args()
            user_data = Users.query.filter(Users.email==data.get('email')).first()
            if user_data:
                if bcrypt.check_password_hash(user_data.password,data.get('password')):

                    payload = {
                        "id":user_data.id,
                    }
                    token = generate_token(payload)
                    req_sys_type = sys_type()
                    if req_sys_type == 'WEB' or req_sys_type == 'POSTMAN':
                        resp = make_response(jsonify({'msg':'Success','data':{'staff_id':user_data.id}}),200)
                        resp.set_cookie('acces_token',token,httponly=True,max_age=60*60*24*365*2)
                        return resp
                    if req_sys_type == 'MOB':
                        return make_response(jsonify({'msg':'Success','token':token,'staff_id':user_data.id}),200)
                    return make_response(jsonify({'msg':'Unknown Origin'}),403)
                return make_response(jsonify({'msg': 'Invalid Username or Password'}), 400)
            return make_response(jsonify({'msg': 'Invalid Username or Password'}), 400)

        except SQLAlchemyError as e:
            print(e)
            return make_response(jsonify({'msg': 'Invalid Data'}), 400)
        except reqparse.ParserError as e:
            print(e.args)
            return make_response(jsonify({"msg":e.args[0]}), 400)
        except Exception as e:
            print(e)
            return make_response(jsonify({'msg': 'Server Error'}), 500) 