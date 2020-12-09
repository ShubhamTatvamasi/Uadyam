from flask import Flask
from flask_cors import CORS
import os
from pathlib import Path
full_path = os.getcwd()
RESUME_FOLDER = str(Path(full_path).parents[0]) + '/app/resume'
JD_FOLDER = str(Path(full_path).parents[0]) + '/app/jd'


app = Flask(__name__)
CORS(app)
app.secret_key = "secret key"
app.config['RESUME_FOLDER'] = RESUME_FOLDER
app.config['JD_FOLDER'] = JD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024