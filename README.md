# Uadyam

### Docker

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

Tag the docker image
```bash
docker tag shubhamtatvamasi/private:uadyam shubhamtatvamasi/private:uadyam-1
```

Push the docker image
```bash
docker push shubhamtatvamasi/private:uadyam-1
```

### Kubernetes

Create a POD on k8s and expose it's service on NodePort 31001
```bash
kubectl run uadyam --image=shubhamtatvamasi/private:uadyam-4 --port=5000 --expose \
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
  --command -- python main.py

kubectl patch svc uadyam \
  --patch='{"spec": {"type": "NodePort"}}'

kubectl patch svc uadyam \
  --patch='{"spec": {"ports": [{"nodePort": 31001, "port": 5000}]}}'
```

Update the docker image
```bash
kubectl set image po uadyam uadyam=shubhamtatvamasi/private:uadyam-2
```
