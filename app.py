from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views.user import UserManagement
from models import *

api = Api(app)
CORS(app)


# api.add_resource(Hello, '/hello')
api.add_resource(UserManagement, '/user')


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')