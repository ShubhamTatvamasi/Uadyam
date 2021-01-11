# Uadyam

### Docker

creating new image from Dockerfile
```bash
docker build -t shubhamtatvamasi/private:uadyam .
```

Run application
```bash
docker run --rm -it -p 80:5000 shubhamtatvamasi/private:uadyam main.py
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

create deployment and service:
```bash
kubectl create deployment uadyam --image=shubhamtatvamasi/private:uadyam-18
kubectl expose deployment uadyam --port=5000 --name=uadyam

# update the image pull secret
kubectl patch deployment uadyam \
  --patch='{
  "spec": {
    "template": {
      "spec": {
        "imagePullSecrets":[
          {
            "name":"docker-shubhamtatvamasi"
          }
        ]
      }
    }
  }
}'
```

Create Deployment:
```yaml
kubectl apply -f - << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: uadyam
  labels:
    app: uadyam
spec:
  replicas: 2
  selector:
    matchLabels:
      app: uadyam
  template:
    metadata:
      labels:
        app: uadyam
    spec:
      containers:
      - name: uadyam
        image: shubhamtatvamasi/private:uadyam-18
      imagePullSecrets:
      - name: docker-shubhamtatvamasi
EOF
```

Create service for Deployment:
```bash
kubectl expose deployment uadyam --port=5000 --name=uadyam
```

Scale Deployment:
```bash
kubectl scale deployment uadyam --replicas=3
```

Create a POD on k8s and expose it's service on NodePort 31001
```bash
kubectl run uadyam --image=shubhamtatvamasi/private:uadyam-18 --port=5000 --expose \
  --overrides='{
   "apiVersion":"v1",
   "spec":{
      "imagePullSecrets":[
         {
            "name":"docker-shubhamtatvamasi"
         }
      ]
   }
}'

# Don't add these if using Ingress:
kubectl patch svc uadyam \
  --patch='{"spec": {"type": "NodePort"}}'

kubectl patch svc uadyam \
  --patch='{"spec": {"ports": [{"nodePort": 31001, "port": 5000}]}}'
```

Update the docker image
```bash
kubectl set image po uadyam uadyam=shubhamtatvamasi/private:uadyam-18
```

Ingress deployment
```bash
kubectl apply -f - << EOF
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: uadyam
spec:
  tls:
  - hosts:
      - uadyam.k8s.shubhamtatvamasi.com
    secretName: letsencrypt
  rules:
  - host: uadyam.k8s.shubhamtatvamasi.com
    http:
      paths:
      - backend:
          serviceName: uadyam
          servicePort: 5000
EOF
```

Delete deployment
```bash
kubectl delete pod/uadyam service/uadyam
```

