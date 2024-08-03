FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN sudo apt update

# require graphviz to run PlantUML vscode plugin
# more: https://plantuml.com/graphviz-dot
RUN sudo apt install graphviz -y

# install ping
RUN sudo apt install iputils-ping -y
# install dnslookup
# RUN sudo apt install dnsutils -y

# install k9s to use it later to monitor local minikube cluster
RUN curl -Lo k9s.tar.gz https://github.com/derailed/k9s/releases/latest/download/k9s_Linux_amd64.tar.gz
RUN tar -zxvf k9s.tar.gz
RUN sudo mv k9s /usr/local/bin/
