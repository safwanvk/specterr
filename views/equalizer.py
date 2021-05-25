from sqlalchemy import text
from flask import jsonify, request,make_response
from flask_restful import Resource,reqparse
from sqlalchemy.exc import SQLAlchemyError
from models import *
from utils.util import *
from werkzeug.utils import secure_filename
import threading
from views.visualizer import *

class Video(Resource):

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
                

                t = threading.Thread(target=main,args=(filename,))
                t.daemon = True
                t.start()

            global complete
            print(complete)
            if complete:
                http_args = request.args.to_dict()
                video_dict = Videos(url=f'{filename}.mp4',user_id=http_args.get('user_id'))
                db.session.add(video_dict)
                db.session.commit()
                os.remove(UPLOAD_FOLDER+filename)
                return make_response(jsonify({'msg':'Success','url':f'{filename}.mp4'}), 200)

        except SQLAlchemyError as e:
            print(e.__dict__['orig'].args[0])
            if e.__dict__['orig'].args[0] == 1062:
                return make_response(jsonify({'msg': e.__dict__['orig'].args[1]}), 400)
            return make_response(jsonify({'msg': 'Invalid Data'}), 400)
        except Exception as e:
            print(e)
            return make_response(jsonify({'msg': 'Server Error'}), 500)