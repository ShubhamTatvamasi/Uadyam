import requests

url = 'http://127.0.0.1:5000/jd_parsar'
myobj = "//home//lid//Downloads//Job Description-20201121T112409Z-001//Job Description//"

x = requests.post(url, data = myobj)

print(x.text)
