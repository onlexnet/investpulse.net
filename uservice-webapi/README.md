Single entry point to access available services

Run locally:
```bash
socat TCP-LISTEN:80,fork TCP:$(minikube ip):80 & # http

skaffold dev --skip-tests

http://localhost:80/graphiql
```

  # example: to build images to locally deploy to k8s
  # 1) Optionally change context to work on minikube images
  eval $(minikube docker-env)
  # 2) to build image and push it to local k8s instance
  mvn jib:dockerBuild -pl host clean install -DskipTests
  mvn jib:dockerBuild -pl host -Dimage=sinnet.azurecr.io/uservice-projects-host:latest
  mvn jib:dockerBuild -pl initdb-host clean install -DskipTests
  mvn jib:dockerBuild -pl initdb-host -Dimage=sinnet.azurecr.io/uservice-projects-initdb


## Useful links
- [Kafka example with Java](https://www.youtube.com/watch?v=u0kRK-qbopk)
