from sqlalchemy import text
from flask import jsonify, request,make_response
from flask_restful import Resource,reqparse
from sqlalchemy.exc import SQLAlchemyError
from models import *
from utils.util import *
from utils.sqalchemy import *
from werkzeug.utils import secure_filename
import threading
from views.visualizer import *

class Video(Resource):
    @auth([Role.User,Role.Admin])
    def post(self):
        
        try:
            if 'file' not in request.files:
                return make_response(jsonify({'msg':'No file part'}),400)
            file = request.files['file']
            if file.filename == '':
                return make_response(jsonify({'msg':'No selected file'}),400)

            file.seek(0, 2)
            file_length = file.tell()
            if not allowed_image_filesize(file_length):
                return make_response(jsonify({'msg':'Please put file less than 5MB'}),400)
            file.seek(0)
            if not allowed_video(file.filename):
                return make_response(jsonify({'msg':'This Video extension is not Allowed'}),400)

            if file and allowed_video(file.filename):
                filename = secure_filename(file.filename)
                # filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                
                main(filename)
                http_args = request.args.to_dict()
                # todo change in host
                video_dict = Videos(url=f'http://192.168.43.88:5000/uploads/{filename}.mp4',user_id=http_args.get('user_id'))
                db.session.add(video_dict)
                db.session.commit()
                os.remove(UPLOAD_FOLDER+filename)
                return make_response(jsonify({'msg':'Success','url':f'http://192.168.43.88:5000/uploads/{filename}.mp4'}), 200)

        except SQLAlchemyError as e:
            print(e)
            if e.__dict__['orig'].args[0] == 1062:
                return make_response(jsonify({'msg': e.__dict__['orig'].args[1]}), 400)
            return make_response(jsonify({'msg': 'Invalid Data'}), 400)
        except Exception as e:
            print(e)
            return make_response(jsonify({'msg': 'Server Error'}), 500)
    @auth([Role.User,Role.Admin])
    def get(self):
        try:
            http_args = request.args.to_dict()
            user_id=http_args.get('user_id')

            query = text("""select id,url from videos
            where user_id=:user_id """)
            video_det = db.engine.execute(query, user_id=user_id).fetchall()
            if video_det:
                data = aslist(video_det)
                return make_response(jsonify({'msg':'Success','data':data}),200)

            return make_response(jsonify({'msg':'Video Not Found','data':{}}),400)
        except SQLAlchemyError as e:
            print(e)
            return make_response(jsonify({'msg': 'Invalid Data'}), 400)
        except Exception as e:
            print(e)
            return make_response(jsonify({'msg': 'Server Error'}), 500)