from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views.user import *

app = Flask(__name__,static_folder='/uploads')
api = Api(app)
CORS(app)


api.add_resource(Hello, '/hello')


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')