python -m spacy download en
has to be done in environment
**************************************
Calling various api
**************************************
#Steps for calling resume_parsar api
**************************************
import requests
import json
from flask import Flask, request, redirect, jsonify
myurl = 'http://127.0.0.1:5000/Resume_Parsar'
files = {'file':open("resume.docx",'rb')}
getdata = requests.get(myurl,files=files)
json.loads(getdata.text)

*************************************
#Steps for calling jd_parsar api
*************************************
import requests
import json
from flask import Flask, request, redirect, jsonify
myurl = 'http://127.0.0.1:5000/Jd_Parsar'
files = {'file':open("jd.docx",'rb')}
getdata = requests.get(myurl,files=files)
json.loads(getdata.text)
***************************************
#Steps for calling matcher api
***************************************
import requests
from flask import Flask, request, redirect, jsonify
myurl = 'http://127.0.0.1:5000/Matcher'
#open('test.txt', 'rb')file2
files = {'resume_file':open("//home//lid//Downloads//Omar_Nour_CV.docx",'rb'),'jd_file':open("//home//lid//Downloads//Job Description-20201121T112409Z-001//Job Description//Business Analyst_JD.docx",'rb')}
getdata = requests.get(myurl,files=files)
json.loads(getdata.text)


running diffrent scripts
python resume_parsar.py <resume_file>
python jd_parsar.py <jd_file>
python matcher.py <resume_file> <jd_file>


