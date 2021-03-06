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
            parser.add_argument('role')
            
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

class SingleUserManagement(Resource):

    def put(self,user_id):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('email',type=str,required=True,help='email must be  string')
            parser.add_argument('name',type=str,required=True,help='name must be  string')

            parse_data = parser.parse_args()    # get parsed data from requset 

            #  getting staff details
            Users.query.filter(Users.id==user_id).update(parse_data)
            db.session.commit()

            return make_response(jsonify({'msg':'Updated User'}), 200)

        except SQLAlchemyError as e:
            print(e)
            return make_response(jsonify({'msg': 'Invalid Data'}), 400)
        except reqparse.ParserError as e:
            print(e.args)
            return make_response(jsonify({"msg":e.args[0]}), 400)
        except Exception as e:
            print(e)
            return make_response(jsonify({'msg': 'Server Error'}), 500)

    def get(self,user_id):
        try:

            query = text("""select id,name,email from users
            where id=:id """)
            user_det = db.engine.execute(query, id=user_id).fetchone()
            if user_det:
                data = dict(user_det)
                return make_response(jsonify({'msg':'Success','data':data}),200)

            return make_response(jsonify({'msg':'User Not Found','data':{}}),400)
        except SQLAlchemyError as e:
            print(e)
            return make_response(jsonify({'msg': 'Invalid Data'}), 400)
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
                        "role":user_data.role
                    }
                    token = generate_token(payload)
                    query = text("""UPDATE users SET token=:token,no_logins=no_logins+1 WHERE id=:id""")
                    db.engine.execute(query, token=token,id=user_data.id)


                    req_sys_type = sys_type()
                    if req_sys_type == 'WEB' or req_sys_type == 'POSTMAN':
                        resp = make_response(jsonify({'msg':'Success','data':{'user_id':user_data.id}}),200)
                        resp.set_cookie('acces_token',token,httponly=True,max_age=60*60*24*365*2)
                        return resp
                    if req_sys_type == 'MOB':
                        return make_response(jsonify({'msg':'Success','token':token,'user_id':user_data.id}),200)
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

class UserLogout(Resource):
    @auth([Role.User,Role.Admin])
    def post(self):
        try:
            http_args = request.args.to_dict()
            query = text("""UPDATE users SET token=:token,no_logins=no_logins-1 WHERE id=:id and no_logins <= 1 """)
            dic = {
                "token": None,
                "id": http_args.get('user_id')
            }
            db.engine.execute(query, dic)

            query = text("""UPDATE users SET no_logins=no_logins-1 WHERE id=:id and no_logins > 1 """)
            dic = {
                "token": None,
                "id": http_args.get('user_id')
            }
            db.engine.execute(query, dic)
            req_sys_type = sys_type()
            if req_sys_type == 'WEB' or req_sys_type == 'POSTMAN':
                resp = make_response(jsonify({'msg':'success'}),200)
                resp.set_cookie('acces_token',"",httponly=True,max_age=0)
                return resp
            if req_sys_type == 'MOB':
                return make_response(jsonify({'msg':'Success'}),200)

        except SQLAlchemyError as e:
            print(e)
            return make_response(jsonify({'msg': 'Invalid Data'}), 400)
        except Exception as e:
            print(e)
            return make_response(jsonify({'msg': 'Server Error'}), 500)

class ForgotPassword(Resource):
    # OTP send to mail
    def post(self):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('email',type=str, required=True,help='email is required')
            args = parser.parse_args()

            query = text("""SELECT name,email from users where email=:email """)
            res = db.engine.execute(query, email=args.get('email')).fetchone()
            if res:
                res = dict(res)
                
                # store in cache
                otp = cache_code(res.get('email'))
                
                email_status = send_otp(res.get('name'), res.get('email'), otp)
                if email_status:
                    return make_response(jsonify({'msg': 'Success'}), 200)
                    
                return make_response(jsonify({'msg': 'Mail Server Error'}), 500)
            else:
                return make_response(jsonify({'msg': 'Invalid Data'}), 400)
        except SQLAlchemyError as e:
            print(e)
            return make_response(jsonify({'msg': 'Invalid Data'}), 400)
        except reqparse.ParserError as e:
            print(e.args)
            return make_response(jsonify({"msg":e.args[0]}), 400)
        except Exception as e:
            print(e)
            return make_response(jsonify({'msg': 'Server Error'}), 500)

    def put(self):
        # change password
        try:
            parser = reqparse.RequestParser()
            
            parser.add_argument('otp',type=int, required=True,help='otp is required')
            parser.add_argument('email',type=str, required=True,help='email is required')
            parser.add_argument('password',type=str, required=True,help='password is required')
            args = parser.parse_args()

            otp = cache_code(args.get('email'))

            if otp == args.get('otp'):
                password = bcrypt.generate_password_hash(args.get('password'), 10)

                query = text("""update users set password=:password where email=:email """)
                db.engine.execute(query, password=password, email=args.get('email'))
                return make_response(jsonify({'msg': 'Password Updated'}), 200)
            else:
                return make_response(jsonify({'msg': 'invalid otp'}), 400)
        except SQLAlchemyError as e:
            print(e)
            return make_response(jsonify({'msg': 'Invalid Data'}), 400)
        except reqparse.ParserError as e:
            print(e.args)
            return make_response(jsonify({"msg":e.args[0]}), 400)
        except Exception as e:
            print(e)
            return make_response(jsonify({'msg': 'Server Error'}), 500)

class VerifyOTP(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            
            parser.add_argument('otp',type=int, required=True,help='otp is required')
            parser.add_argument('email',type=str, required=True,help='email is required')
            args = parser.parse_args()

            otp = cache_code(args.get('email'))

            if otp == args.get('otp'):
                return make_response(jsonify({'msg': 'Otp Verified'}), 200)
            else:
                return make_response(jsonify({'msg': 'Invalid Otp'}), 400)
        except reqparse.ParserError as e:
            print(e.args)
            return make_response(jsonify({"msg":e.args[0]}), 400)
        except Exception as e:
            print(e)
            return make_response(jsonify({'msg': 'Server Error'}), 500)

class ChangePassword(Resource):
    @auth([Role.User,Role.Admin])
    def post(self):
        try:
            parser = reqparse.RequestParser()
            
            parser.add_argument('old_password',type=str, required=True,help='old_password is required')
            parser.add_argument('new_password',type=str, required=True,help='new_password is required')
            args = parser.parse_args()
            
            http_args = request.args.to_dict()
            query = text("""SELECT password from users where id=:id """)
            res = db.engine.execute(query, id=http_args.get('user_id')).fetchone()
            if res:
                res = dict(res)

                if bcrypt.check_password_hash(res.get('password'),args.get('old_password')):

                    password = bcrypt.generate_password_hash(args.get('new_password'), 10)
                    query = text("""update users set password=:password where id=:id """)
                    db.engine.execute(query, password=password, id=http_args.get('user_id'))

                    return make_response(jsonify({'msg': 'Password Changed'}), 200)

                else:
                    return make_response(jsonify({'msg': 'Invalid Password'}), 400)
            else:
                return make_response(jsonify({'msg': 'Invalid User'}), 400)
        except SQLAlchemyError as e:
            print(e)
            return make_response(jsonify({'msg': 'Invalid Data'}), 400)
        except reqparse.ParserError as e:
            print(e.args)
            return make_response(jsonify({"msg":e.args[0]}), 400)
        except Exception as e:
            print(e)
            return make_response(jsonify({'msg': 'Server Error'}), 500)

