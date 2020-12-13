import os
import urllib.request
from app import app
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
from resume_parsar import resumeParsar
from jd_parsar import jdParsar
from matcher import matcher

ALLOWED_EXTENSIONS = set(['docx', 'doc'])
rp = resumeParsar()
jdp = jdParsar()
mp = matcher()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/Resume_Parsar', methods=['POST'])
def resume_parsar():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    # print(file)
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 401
        return resp
    if file and allowed_file(file.filename):
        # print('in')
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['RESUME_FOLDER'], filename))
        full_file_name = str(app.config['RESUME_FOLDER']) + '/' + filename
        print(type(full_file_name))
        print(full_file_name)
        resp = rp.generate_resume_result(full_file_name)
        resp['status_code'] = 200
        return jsonify(resp)
    else:
        resp = jsonify({'message': 'Allowed file types are docx'})
        resp.status_code = 400
        return resp


@app.route('/Jd_Parsar', methods=['POST'])
def jd_parsar():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    # print(file)
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 401
        return resp
    if file and allowed_file(file.filename):
        # print('in')
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['JD_FOLDER'], filename))
        full_file_name = str(app.config['JD_FOLDER']) + '/' + filename
        resp = jdp.getparsedjd(full_file_name)
        resp['status_code'] = 200
        return jsonify(resp)
    else:
        resp = jsonify({'message': 'Allowed file types are docx'})
        resp.status_code = 400
        return resp


@app.route('/Matcher', methods=['POST'])
def matcher():
    # check if the post request has the file part
    if 'resume_file' not in request.files:
        resp = jsonify({'message': 'No resume file in the request'})
        resp.status_code = 400
        return resp
    if 'jd_file' not in request.files:
        resp = jsonify({'message': 'No jd file in the request'})
        resp.status_code = 400
        return resp
    resume_file = request.files.getlist("resume_file")
    jd_file = request.files.getlist("jd_file")
    print('**********')
    print(resume_file)
    print("*****************")
    print(type(jd_file[0]))
    if jd_file and allowed_file(jd_file[0].filename):
        filename = secure_filename(jd_file[0].filename)
        jd_file[0].save(os.path.join(app.config['JD_FOLDER'], filename))
        jd_file_name = str(app.config['JD_FOLDER']) + '/' + filename
        resp_jd = jdp.getparsedjd(jd_file_name)
    else:
        resp = jsonify({'message': 'Allowed file types for jd are docx'})
        resp.status_code = 400
        return resp
    if resume_file and allowed_file(resume_file[0].filename):
        filename = secure_filename(resume_file[0].filename)
        resume_file[0].save(os.path.join(app.config['RESUME_FOLDER'], filename))
        resume_file_name = str(app.config['RESUME_FOLDER']) + '/' + filename
        resp_resume = rp.generate_resume_result(resume_file_name)
    else:
        resp = jsonify({'message': 'Allowed file types for resume are docx'})
        resp.status_code = 400
        return resp
    resp = mp.get_similarity_overall(resp_jd, resp_resume, mp.skill_2_vec)
    resp['status_code']=200
    return jsonify(resp)



if __name__ == "__main__":
    # app.debug = True
    app.run(host='0.0.0.0', port=5000)
