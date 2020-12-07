import os
from flask import Flask, flash, request, redirect, url_for,render_template,session
from pathlib import Path
from werkzeug.utils import secure_filename
from resume_parsar import resumeParsar
from jd_parsar import jdParsar
app = Flask(__name__)
full_path = os.getcwd()
UPLOAD_FOLDER = str(Path(full_path).parents[0]) + '/app/uploads/'
#print(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
rp = resumeParsar()
jdp = jdParsar()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/resume_parsar', methods=['POST','GET'])
def resume_parsar():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            #return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(filename)
            return(rp.generate_resume_result(filename))
    return render_template("upload.html")
@app.route("/jd_parsar", methods=["POST","GET"])
def jd_parsar():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            # return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(filename)
            return (jdp.getparsedjd(filename))
    return render_template("JD_upload.html")
if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
