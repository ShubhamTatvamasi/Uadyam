# Uadyam

creating new image from Dockerfile
```bash
docker build -t shubhamtatvamasi/private:uadyam .
```

Run application
```bash
docker run --rm -it -p 80:5000 shubhamtatvamasi/private:uadyam resume_parsar_app.py
```

For testing and building docker image
```bash
docker run --rm -it -p 80:5000 \
  -v ${PWD}:/usr/src/app \
  -w /usr/src/app \
  --entrypoint bash \
  shubhamtatvamasi/private:uadyam
```

download library
```bash
python -c "import nltk;nltk.download('stopwords')"
python -m spacy download en
```

  >>> import nltk
  >>> nltk.download('stopwords')
  
python -m spacy download en_core_web_lg
python -m spacy download en


python3.8 -c "print('Real Python');print('Real Python')"



python3.8 -c 'print("Real Python")\nprint("Real Python")\n'

python3.8 -c 'for i in range(10): print "foo"; print "bar"'


### Kubernetes

Create a POD on k8s and expose it's service on NodePort 31001
```bash
kubectl run uadyam --image=shubhamtatvamasi/private:uadyam-1 --port=5000 --expose \
  --overrides='{
   "apiVersion":"v1",
   "spec":{
      "imagePullSecrets":[
         {
            "name":"docker-shubhamtatvamasi"
         }
      ]
   }
}' \
  --command -- python resume_parsar_app.py

kubectl patch svc uadyam \
  --patch='{"spec": {"type": "NodePort"}}'

kubectl patch svc uadyam \
  --patch='{"spec": {"ports": [{"nodePort": 31001, "port": 5000}]}}'
```

Update the docker image
```bash
kubectl set image po uadyam uadyam=shubhamtatvamasi/private:uadyam-2
```
