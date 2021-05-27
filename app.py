from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views.user import *
from views.equalizer import *
from models import *

api = Api(app)
CORS(app)


# api.add_resource(Hello, '/hello')
api.add_resource(UserManagement, '/user')
api.add_resource(UserLogin, '/user/login')
api.add_resource(UserLogout, '/user/logout')
api.add_resource(SingleUserManagement, '/user/<int:user_id>')
api.add_resource(Video, '/video')
api.add_resource(Download, '/download/<int:id>')


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')