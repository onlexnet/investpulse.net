set -e
minikube ip
socat TCP-LISTEN:80,fork TCP:$(minikube ip):80 & # http
socat TCP-LISTEN:9094,fork TCP:$(minikube ip):9094 & # kafka external
